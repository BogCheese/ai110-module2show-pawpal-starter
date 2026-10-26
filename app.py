import streamlit as st

from datetime import time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task, format_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Streamlit re-runs this whole script on every click, so a plain `owner = Owner(...)`
# would be recreated empty each time. st.session_state is a dictionary that survives
# re-runs, so we only create the Owner the first time and reuse it afterwards.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = int(
    st.number_input("Minutes available today", min_value=1, max_value=1440, value=owner.available_minutes)
)

st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_clicked = st.form_submit_button("Add pet")

if add_pet_clicked:
    if pet_name.strip():
        # Owner.add_pet stores the new Pet inside the Owner kept in session_state.
        owner.add_pet(Pet(name=pet_name.strip(), species=species))
    else:
        st.warning("Please enter a pet name.")

# Streamlit re-runs the script after the form is submitted, so this list is rebuilt
# from owner.pets and the new pet shows up right away.
if owner.pets:
    st.table(
        [{"Pet": pet.name, "Species": pet.species, "Tasks": len(pet.tasks)} for pet in owner.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
scheduler = Scheduler(owner)

if not owner.pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    # Select by position, then look the pet up in owner.pets. Streamlit hands back a
    # *copy* of objects passed to selectbox, and a task added to a copy would be lost.
    pet_index = st.selectbox(
        "Pet", range(len(owner.pets)), format_func=lambda i: owner.pets[i].name
    )
    selected_pet = owner.pets[pet_index]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox(
            "Priority", list(Priority), index=2, format_func=lambda p: p.name.title()
        )
    with col4:
        frequency = st.selectbox(
            "Frequency", list(Frequency), format_func=lambda f: f.value.title()
        )

    # The scheduler stores times as minutes since midnight, so convert the time picker.
    preferred_time = None
    if st.checkbox("Set a preferred time"):
        chosen_time = st.time_input("Preferred time", value=time(8, 0))
        preferred_time = chosen_time.hour * 60 + chosen_time.minute

    if st.button("Add task"):
        # Pet.add_task stores the Task on the selected pet (and records the pet's name on it).
        selected_pet.add_task(
            Task(task_title, int(duration), priority, frequency, preferred_time=preferred_time)
        )

    # This sits above the task table so a completed task shows as done on the same click.
    pending = [(pet, task) for pet in owner.pets for task in pet.tasks if not task.completed]
    if pending:
        st.markdown("#### Mark a task complete")
        pending_index = st.selectbox(
            "Task",
            range(len(pending)),
            format_func=lambda i: f"{pending[i][1].title} ({pending[i][0].name})",
        )
        if st.button("Mark complete"):
            pet, task = pending[pending_index]
            # Pet.complete_task also adds the next occurrence if the task repeats.
            next_task = pet.complete_task(task)
            if next_task:
                st.success(
                    f"Done! '{task.title}' repeats {task.frequency.value}, "
                    f"so the next one is due {next_task.due_date:%b %d}."
                )
            else:
                st.success(f"Done! '{task.title}' is complete.")

if owner.get_all_tasks():
    st.markdown("#### Your tasks")
    filter_pet_col, filter_status_col = st.columns(2)
    with filter_pet_col:
        pet_filter = st.selectbox("Filter by pet", ["All pets"] + [pet.name for pet in owner.pets])
    with filter_status_col:
        status_filter = st.radio("Filter by status", ["All", "To do", "Done"], horizontal=True)

    # Owner.filter_tasks narrows the list; Scheduler.sort_by_time puts it in time order.
    filtered_tasks = owner.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "To do": False, "Done": True}[status_filter],
    )
    shown_tasks = scheduler.sort_by_time(filtered_tasks)

    if shown_tasks:
        st.table(
            [
                {
                    "Time": format_time(task.preferred_time) if task.preferred_time is not None else "Any time",
                    "Pet": task.pet_name,
                    "Task": task.title,
                    "Minutes": task.duration_minutes,
                    "Priority": task.priority.name.title(),
                    "Frequency": task.frequency.value.title(),
                    "Status": "Done" if task.completed else "To do",
                }
                for task in shown_tasks
            ]
        )
    else:
        st.info("No tasks match these filters.")

    # Tell the owner about clashes now, while they can still fix them.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for message in conflicts:
            st.warning(message)
        st.caption(
            "To fix a conflict, change one task's time. If you leave it, the scheduler keeps the "
            "higher-priority task at its time and moves the other to the next free slot."
        )
    else:
        st.success("No time conflicts between your tasks.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Builds today's plan from every pet's tasks: highest priority first, within your available minutes.")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()

    if plan.scheduled_items:
        st.success(
            f"Scheduled {len(plan.scheduled_items)} task(s) using "
            f"{plan.total_minutes} of {owner.available_minutes} minutes."
        )
        st.table(
            [
                {
                    "Start": format_time(item.start_minute),
                    "End": format_time(item.end_minute),
                    "Task": item.task.title,
                    "Pet": item.task.pet_name,
                    "Why": item.reason,
                }
                for item in plan.scheduled_items
            ]
        )
    else:
        st.warning("Nothing could be scheduled. Add tasks or increase your available minutes.")

    if plan.skipped_items:
        left_out = "\n".join(
            f"- **{skipped.task.title}** ({skipped.task.pet_name}): {skipped.reason}"
            for skipped in plan.skipped_items
        )
        st.warning(f"Some tasks were left out:\n\n{left_out}")
