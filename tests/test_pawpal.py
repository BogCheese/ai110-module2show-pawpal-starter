from datetime import date, timedelta

import pytest

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def make_owner() -> tuple[Owner, Pet, Pet]:
    """An owner with two pets, used by the tests below."""
    owner = Owner("Jordan", available_minutes=120)
    buddy, mia = Pet("Buddy", "dog"), Pet("Mia", "cat")
    owner.add_pet(buddy)
    owner.add_pet(mia)
    return owner, buddy, mia


# --- Basics ---------------------------------------------------------------


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", 30, Priority.HIGH)

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "dog")

    pet.add_task(Task("Morning walk", 30, Priority.HIGH))

    assert len(pet.tasks) == 1


# --- Sorting --------------------------------------------------------------


def test_sort_by_time_orders_by_preferred_time_with_unscheduled_last():
    late = Task("Evening brush", 10, Priority.LOW, preferred_time=18 * 60)
    anytime = Task("Cuddle", 10, Priority.LOW)
    early = Task("Morning walk", 30, Priority.HIGH, preferred_time=7 * 60)

    sorted_tasks = Scheduler.sort_by_time([late, anytime, early])

    assert sorted_tasks == [early, late, anytime]


# --- Filtering ------------------------------------------------------------


def test_filter_tasks_by_pet_and_status():
    owner, buddy, mia = make_owner()
    walk = Task("Walk", 30, Priority.HIGH)
    brush = Task("Brush", 10, Priority.LOW)
    meds = Task("Meds", 5, Priority.HIGH)
    buddy.add_task(walk)
    buddy.add_task(brush)
    mia.add_task(meds)
    brush.mark_complete()

    assert owner.filter_tasks(pet_name="Buddy") == [walk, brush]
    assert owner.filter_tasks(completed=False) == [walk, meds]
    assert owner.filter_tasks(pet_name="Buddy", completed=True) == [brush]
    assert owner.filter_tasks() == [walk, brush, meds]


# --- Recurring tasks ------------------------------------------------------


def test_completing_daily_task_creates_task_due_tomorrow():
    pet = Pet("Buddy", "dog")
    today = date.today()
    walk = Task("Walk", 30, Priority.HIGH, Frequency.DAILY, due_date=today)
    pet.add_task(walk)

    next_walk = pet.complete_task(walk)

    assert walk.completed is True
    assert next_walk.due_date == today + timedelta(days=1)
    assert next_walk.completed is False
    assert next_walk in pet.tasks
    assert next_walk.pet_name == "Buddy"
    assert next_walk.id != walk.id


def test_completing_overdue_daily_task_is_due_tomorrow_not_relative_to_old_date():
    pet = Pet("Buddy", "dog")
    three_days_ago = date.today() - timedelta(days=3)
    walk = Task("Walk", 30, Priority.HIGH, Frequency.DAILY, due_date=three_days_ago)
    pet.add_task(walk)

    next_walk = pet.complete_task(walk)

    assert next_walk.due_date == date.today() + timedelta(days=1)


def test_completing_weekly_task_creates_task_due_in_seven_days():
    pet = Pet("Buddy", "dog")
    today = date.today()
    brush = Task("Brush", 15, Priority.LOW, Frequency.WEEKLY, due_date=today)
    pet.add_task(brush)

    next_brush = pet.complete_task(brush)

    assert next_brush.due_date == today + timedelta(days=7)


def test_completing_one_time_task_does_not_repeat():
    pet = Pet("Buddy", "dog")
    vet = Task("Vet visit", 60, Priority.HIGH, Frequency.ONCE)
    pet.add_task(vet)

    assert pet.complete_task(vet) is None
    assert len(pet.tasks) == 1


def test_complete_task_rejects_task_from_another_pet():
    pet = Pet("Buddy", "dog")

    with pytest.raises(ValueError):
        pet.complete_task(Task("Walk", 30, Priority.HIGH))


def test_plan_ignores_tasks_not_due_yet():
    owner, buddy, _ = make_owner()
    today = date.today()
    due_today = Task("Walk", 30, Priority.HIGH, due_date=today)
    due_tomorrow = Task("Bath", 30, Priority.HIGH, due_date=today + timedelta(days=1))
    buddy.add_task(due_today)
    buddy.add_task(due_tomorrow)

    plan = Scheduler(owner).generate_plan(today)

    assert [item.task for item in plan.scheduled_items] == [due_today]
    assert plan.skipped_items == []


# --- Conflict detection ---------------------------------------------------


def test_detect_conflicts_flags_overlapping_preferred_times_across_pets():
    owner, buddy, mia = make_owner()
    buddy.add_task(Task("Walk", 30, Priority.HIGH, preferred_time=9 * 60))  # 9:00-9:30
    mia.add_task(Task("Meds", 10, Priority.HIGH, preferred_time=9 * 60 + 15))  # 9:15-9:25

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Meds" in warnings[0]


def test_detect_conflicts_flags_same_time_tasks_for_the_same_pet():
    owner, buddy, _ = make_owner()
    buddy.add_task(Task("Walk", 30, Priority.HIGH, preferred_time=9 * 60))
    buddy.add_task(Task("Flea treatment", 10, Priority.MEDIUM, preferred_time=9 * 60))

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert "Walk (Buddy" in warnings[0] and "Flea treatment (Buddy" in warnings[0]


def test_detect_conflicts_ignores_back_to_back_and_completed_tasks():
    owner, buddy, mia = make_owner()
    buddy.add_task(Task("Walk", 30, Priority.HIGH, preferred_time=9 * 60))  # 9:00-9:30
    mia.add_task(Task("Meds", 10, Priority.HIGH, preferred_time=9 * 60 + 30))  # starts as walk ends
    done = Task("Play", 30, Priority.LOW, preferred_time=9 * 60)
    mia.add_task(done)
    done.mark_complete()

    assert Scheduler(owner).detect_conflicts() == []


def test_plan_moves_conflicting_task_to_next_free_slot():
    owner, buddy, mia = make_owner()
    buddy.add_task(Task("Walk", 30, Priority.HIGH, preferred_time=9 * 60))
    mia.add_task(Task("Meds", 10, Priority.MEDIUM, preferred_time=9 * 60))

    plan = Scheduler(owner).generate_plan()
    start_by_title = {item.task.title: item.start_minute for item in plan.scheduled_items}

    assert start_by_title["Walk"] == 9 * 60
    # Meds lost its 9:00 slot, so it goes in the earliest free slot (the 8:00 day start).
    assert start_by_title["Meds"] == 8 * 60
