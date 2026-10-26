# Temporary testing ground to verify the logic works in the terminal
# before connecting it to the app UI.

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create an owner with two pets, each with a few care tasks."""
    owner = Owner(name="Jordan", available_minutes=120)

    buddy = Pet(name="Buddy", species="dog")
    mia = Pet(name="Mia", species="cat")
    owner.add_pet(buddy)
    owner.add_pet(mia)

    # preferred_time is minutes since midnight, so 7 * 60 = 7:00 AM.
    buddy.add_task(Task("Morning walk", 30, Priority.HIGH, Frequency.DAILY, preferred_time=7 * 60))
    buddy.add_task(Task("Brush coat", 15, Priority.LOW, Frequency.WEEKLY, preferred_time=18 * 60))
    mia.add_task(Task("Give medication", 5, Priority.HIGH, Frequency.DAILY, preferred_time=8 * 60))
    mia.add_task(Task("Play with laser", 20, Priority.MEDIUM, Frequency.DAILY, preferred_time=12 * 60))

    return owner


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan()

    print(f"Owner: {owner.name} ({owner.available_minutes} minutes available)")
    print(f"Pets: {', '.join(pet.name for pet in owner.pets)}")
    print()
    print(plan.display())
    print()
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
