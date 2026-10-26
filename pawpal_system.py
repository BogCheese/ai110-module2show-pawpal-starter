"""Logic layer for the PawPal system.

This module holds the core classes described in diagrams/uml.mmd:

    Owner  --has-->  Pet  --has-->  Task
    Scheduler reads from an Owner and creates a DailyPlan.
    DailyPlan holds ScheduledItems and SkippedItems.

Times are stored as "minutes since midnight" (e.g. 8:30 AM = 510) so they can
be compared and added together without parsing strings. Use format_time() to
turn one back into text for display.
"""

from dataclasses import dataclass, field, fields
from enum import Enum
from uuid import uuid4


def format_time(minute: int) -> str:
    """Turn minutes since midnight into text, e.g. 510 -> '8:30 AM'."""
    hour, minutes = divmod(minute, 60)
    suffix = "AM" if hour % 24 < 12 else "PM"
    return f"{hour % 12 or 12}:{minutes:02d} {suffix}"


class Priority(Enum):
    """How important a task is. The value is used for sorting (higher = first)."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """How often a task needs to be done."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


# eq=False: two tasks are only "the same" if they are the same object, so two
# identical-looking tasks can be told apart and a Task can be used in a set/dict.
@dataclass(eq=False)
class Task:
    """A single care activity for a pet (e.g. a walk or feeding)."""

    title: str
    duration_minutes: int
    priority: Priority
    frequency: Frequency = Frequency.ONCE
    completed: bool = False
    preferred_time: int | None = None  # minutes since midnight; None = no preference
    pet_name: str = ""  # set by Pet.add_task so a plan can say which pet a task is for
    id: str = field(default_factory=lambda: uuid4().hex)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_value(self) -> int:
        """Return the priority as a number so tasks can be sorted."""
        return self.priority.value


# eq=False for the same reason as Task: pets are compared by identity, so two
# pets with the same name and species are still different pets.
@dataclass(eq=False)
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet and record the pet's name on the task."""
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, task: Task, **changes) -> None:
        """Update fields on an existing task, e.g. edit_task(t, priority=Priority.HIGH).

        Raises ValueError if the task is not this pet's, or if a key in
        `changes` is not an editable field of Task.
        """
        if task not in self.tasks:
            raise ValueError(f"{task.title!r} is not one of {self.name}'s tasks")

        # id and pet_name are managed by the system, so they can't be edited.
        editable = {f.name for f in fields(Task)} - {"id", "pet_name"}
        unknown = set(changes) - editable
        if unknown:
            raise ValueError(f"Cannot edit unknown task field(s): {sorted(unknown)}")

        for field_name, new_value in changes.items():
            setattr(task, field_name, new_value)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet (raises ValueError if it isn't here)."""
        self.tasks.remove(task)


@dataclass
class Preferences:
    """Scheduling preferences an owner can set."""

    buffer_minutes: int = 0  # gap to leave between consecutive tasks


@dataclass
class Owner:
    """A pet owner with limited time and scheduling preferences."""

    name: str
    available_minutes: int
    day_start_minute: int = 8 * 60  # when the schedule begins; default 8:00 AM
    preferences: Preferences = field(default_factory=Preferences)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner (raises ValueError if it isn't here)."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets, in pet order."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledItem:
    """A task placed on the plan, with when it starts and why it was chosen."""

    task: Task
    start_minute: int  # minutes since midnight
    reason: str

    @property
    def end_minute(self) -> int:
        """When the task finishes."""
        return self.start_minute + self.task.duration_minutes


@dataclass
class SkippedItem:
    """A task that did not make it onto the plan, with the reason."""

    task: Task
    reason: str


@dataclass
class DailyPlan:
    """The result of scheduling: what was planned and what was skipped, and why."""

    scheduled_items: list[ScheduledItem] = field(default_factory=list)
    skipped_items: list[SkippedItem] = field(default_factory=list)

    @property
    def total_minutes(self) -> int:
        """Total scheduled time. Computed so it can never drift out of sync."""
        return sum(item.task.duration_minutes for item in self.scheduled_items)

    def add_item(self, task: Task, start_minute: int, reason: str) -> None:
        """Schedule a task to start at the given time (items stay sorted by start)."""
        self.scheduled_items.append(ScheduledItem(task, start_minute, reason))
        self.scheduled_items.sort(key=lambda item: item.start_minute)

    def skip(self, task: Task, reason: str) -> None:
        """Record that a task could not be scheduled, and why."""
        self.skipped_items.append(SkippedItem(task, reason))

    def display(self) -> str:
        """Return the plan as human-readable text: the timeline, then what was skipped."""
        lines = ["Today's Schedule", "----------------"]

        if not self.scheduled_items:
            lines.append("Nothing scheduled.")
        for item in self.scheduled_items:
            lines.append(
                f"{format_time(item.start_minute)} - {format_time(item.end_minute)}  "
                f"{item.task.title} ({item.task.pet_name})"
            )
        lines.append(f"Total: {self.total_minutes} minutes")

        if self.skipped_items:
            lines.append("")
            lines.append("Skipped:")
            for skipped in self.skipped_items:
                lines.append(f"- {skipped.task.title} ({skipped.task.pet_name})")

        return "\n".join(lines)


class Scheduler:
    """Builds a DailyPlan from an owner's pets, tasks, and available time."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans for the given owner and all of their pets."""
        self.owner = owner

    def generate_plan(self) -> DailyPlan:
        """Choose and order tasks that fit within the owner's available time.

        Rules:
        - Tasks come from owner.get_all_tasks(), so every pet is included.
        - Tasks that are already completed are skipped.
        - Greedy: take tasks by priority (high first), then shorter duration,
          then pet order, so the result is repeatable. Tradeoff: one long
          high-priority task can use up time that several smaller ones would fit.
        - A task is scheduled at its preferred_time if that slot is free;
          otherwise it goes in the earliest free slot after owner.day_start_minute.
        - Every task ends up either scheduled or skipped, each with a reason.
        """
        plan = DailyPlan()
        buffer = self.owner.preferences.buffer_minutes
        minutes_left = self.owner.available_minutes

        # Step 1: set aside tasks that are already done.
        to_schedule = []
        for task in self.owner.get_all_tasks():
            if task.completed:
                plan.skip(task, "already completed")
            else:
                to_schedule.append(task)

        # Step 2: highest priority first, shorter tasks first within a priority.
        # sort() is stable, so ties keep the owner's pet order.
        to_schedule.sort(key=lambda task: (-task.priority_value(), task.duration_minutes))

        # Step 3: place each task if it fits in the time that is left.
        for task in to_schedule:
            time_needed = task.duration_minutes + buffer
            if time_needed > minutes_left:
                plan.skip(
                    task,
                    f"needs {time_needed} min but only {minutes_left} min left",
                )
                continue

            start, placement = self._choose_start(plan, task, buffer)
            reason = f"{task.priority.name.lower()} priority, {placement}"
            plan.add_item(task, start, reason)
            minutes_left -= time_needed

        return plan

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return a plain-language explanation built from the reasons in the plan."""
        lines = ["Why this plan:"]
        for item in plan.scheduled_items:
            lines.append(f"- {item.task.title}: {item.reason}")
        for skipped in plan.skipped_items:
            lines.append(f"- {skipped.task.title} (skipped): {skipped.reason}")
        return "\n".join(lines)

    def _choose_start(self, plan: DailyPlan, task: Task, buffer: int) -> tuple[int, str]:
        """Pick a start time for the task and describe how it was chosen."""
        preferred = task.preferred_time
        if preferred is not None and self._is_free(plan, preferred, task, buffer):
            return preferred, f"placed at its preferred time {format_time(preferred)}"

        start = self._earliest_free_start(plan, task, buffer)
        if preferred is not None:
            return start, "preferred time was taken, placed in the next free slot"
        return start, "placed in the earliest free slot"

    def _is_free(self, plan: DailyPlan, start: int, task: Task, buffer: int) -> bool:
        """True if the task fits at `start` without overlapping a scheduled task."""
        end = start + task.duration_minutes
        for item in plan.scheduled_items:
            ends_before_item = end + buffer <= item.start_minute
            starts_after_item = start >= item.end_minute + buffer
            if not (ends_before_item or starts_after_item):
                return False
        return True

    def _earliest_free_start(self, plan: DailyPlan, task: Task, buffer: int) -> int:
        """Find the first start time, from the day start onward, where the task fits."""
        start = self.owner.day_start_minute
        # Items are sorted by start time, so walk forward past each one that is in the way.
        for item in plan.scheduled_items:
            if self._is_free(plan, start, task, buffer):
                break
            start = max(start, item.end_minute + buffer)
        return start
