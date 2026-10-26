from pawpal_system import Pet, Priority, Task


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", 30, Priority.HIGH)

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "dog")

    pet.add_task(Task("Morning walk", 30, Priority.HIGH))

    assert len(pet.tasks) == 1
