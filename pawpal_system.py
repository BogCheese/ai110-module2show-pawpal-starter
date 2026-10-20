"""Logic layer for the PawPal system.

This module holds the core classes described in diagrams/uml.mmd:

    Owner  --has-->  Pet  --has-->  Task
    Scheduler reads from an Owner and creates a DailyPlan.
    DailyPlan holds ScheduledItems and SkippedItems.

Times are stored as "minutes since midnight" (e.g. 8:30 AM = 510) so they can
be compared and added together without parsing strings.

Every method below is a stub. The class names, attributes, and method
signatures match the UML so the behavior can be filled in step by step.
"""

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class Priority(Enum):
    """How important a task is. The value is used for sorting (higher = first)."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


# eq=False: two tasks are only "the same" if they are the same object, so two
# identical-looking tasks can be told apart and a Task can be used in a set/dict.
@dataclass(eq=False)
class Task:
    """A single care activity for a pet (e.g. a walk or feeding)."""

    title: str
    duration_minutes: int
    priority: Priority
    completed: bool = False
    preferred_time: int | None = None  # minutes since midnight; None = no preference
    pet_name: str = ""  # set by Pet.add_task so a plan can say which pet a task is for
    id: str = field(default_factory=lambda: uuid4().hex)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def priority_value(self) -> int:
        """Return the priority as a number so tasks can be sorted."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet and record the pet's name on the task."""
        pass

    def edit_task(self, task: Task, **changes) -> None:
        """Update fields on an existing task, e.g. edit_task(t, priority=Priority.HIGH).

        Raises ValueError if a key in `changes` is not a field of Task.
        """
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass


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
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        pass


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
        """Schedule a task to start at the given time."""
        pass

    def skip(self, task: Task, reason: str) -> None:
        """Record that a task could not be scheduled, and why."""
        pass

    def display(self) -> str:
        """Return the plan as human-readable text."""
        pass


class Scheduler:
    """Builds a DailyPlan from an owner's pets, tasks, and available time."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_plan(self) -> DailyPlan:
        """Choose and order tasks that fit within the owner's available time.

        Rules the implementation should follow:
        - Skip tasks that are already completed.
        - Greedy: take tasks by priority (high first), then shorter duration,
          then pet order, so the result is repeatable. Tradeoff: one long
          high-priority task can use up time that several smaller ones would fit.
        - Start at owner.day_start_minute and honor preferred_time when it does
          not overlap an already scheduled task; otherwise place the task in the
          next free slot and say so in the reason.
        - Record every task as either scheduled or skipped, each with a reason.
        """
        pass

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return a plain-language explanation built from the reasons in the plan."""
        pass
