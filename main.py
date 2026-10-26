# Temporary testing ground to verify the logic works in the terminal
# before connecting it to the app UI.

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task, format_time


def build_demo_owner() -> Owner:
    """Create an owner with two pets, each with a few care tasks (added out of time order)."""
    owner = Owner(name="Jordan", available_minutes=120)

    buddy = Pet(name="Buddy", species="dog")
    mia = Pet(name="Mia", species="cat")
    owner.add_pet(buddy)
    owner.add_pet(mia)

    # preferred_time is minutes since midnight, so 7 * 60 = 7:00 AM.
    buddy.add_task(Task("Brush coat", 15, Priority.LOW, Frequency.WEEKLY, preferred_time=18 * 60))
    buddy.add_task(Task("Morning walk", 30, Priority.HIGH, Frequency.DAILY, preferred_time=7 * 60))
    # Same pet, exactly the same time as the morning walk (7:00 AM).
    buddy.add_task(Task("Flea treatment", 10, Priority.MEDIUM, Frequency.ONCE, preferred_time=7 * 60))
    mia.add_task(Task("Play with laser", 20, Priority.MEDIUM, Frequency.DAILY, preferred_time=12 * 60))
    mia.add_task(Task("Give medication", 5, Priority.HIGH, Frequency.DAILY, preferred_time=8 * 60))
    # Deliberately overlaps the morning walk (7:00-7:30) so conflict detection has something to find.
    mia.add_task(Task("Feed breakfast", 10, Priority.HIGH, Frequency.DAILY, preferred_time=7 * 60 + 15))

    return owner


def print_tasks(heading: str, tasks: list[Task]) -> None:
    """Print a short list of tasks under a heading."""
    print(heading)
    for task in tasks:
        time_text = format_time(task.preferred_time) if task.preferred_time is not None else "any time"
        status = "done" if task.completed else "to do"
        print(f"  {time_text:>9}  {task.title} ({task.pet_name}) [{status}, due {task.due_date}]")
    print()


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)
    buddy = owner.pets[0]

    print(f"Owner: {owner.name} ({owner.available_minutes} minutes available)")
    print(f"Pets: {', '.join(pet.name for pet in owner.pets)}")
    print()

    # Sorting: the tasks were added out of order, so sort them by preferred time.
    print_tasks("Tasks sorted by time:", scheduler.sort_by_time(owner.get_all_tasks()))

    # Conflict detection: warn before building the plan.
    print("Conflict check:")
    for warning in scheduler.detect_conflicts() or ["No conflicts."]:
        print(f"  {warning}")
    print()

    # Recurring tasks: completing a daily task adds tomorrow's copy to the pet.
    morning_walk = buddy.tasks[1]
    next_walk = buddy.complete_task(morning_walk)
    print(f"Completed '{morning_walk.title}'; next one is due {next_walk.due_date}.")
    print()

    # Filtering: by pet, and by completion status.
    print_tasks("Mia's tasks:", owner.filter_tasks(pet_name="Mia"))
    print_tasks("Completed tasks:", owner.filter_tasks(completed=True))

    plan = scheduler.generate_plan()
    print(plan.display())
    print()
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
