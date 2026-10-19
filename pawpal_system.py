"""Logic layer for the PawPal system.

This module holds the core classes described in diagrams/uml.mmd:

    Owner  --has-->  Pet  --has-->  Task
    Scheduler reads from an Owner and creates a DailyPlan.

Every method below is a stub. The class names, attributes, and method
signatures match the UML so the behavior can be filled in step by step.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single care activity for a pet (e.g. a walk or feeding)."""

    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    completed: bool = False
    preferred_time: str = ""  # e.g. "morning"; empty means no preference

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
        """Add a care task to this pet."""
        pass

    def edit_task(self, task: Task, **changes) -> None:
        """Update fields on an existing task, e.g. edit_task(t, priority="high")."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass


@dataclass
class Owner:
    """A pet owner with limited time and scheduling preferences."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
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
class DailyPlan:
    """The result of scheduling: what was planned, what was skipped, and why."""

    scheduled_items: list = field(default_factory=list)  # (task, start_time) pairs
    skipped_tasks: list = field(default_factory=list)  # (task, reason) pairs
    total_minutes: int = 0
    reasoning: list[str] = field(default_factory=list)

    def add_item(self, task: Task, start_time: str) -> None:
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
        """Choose and order tasks that fit within the owner's available time."""
        pass

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return a plain-language explanation of why the plan looks this way."""
        pass
