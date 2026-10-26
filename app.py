import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

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

    if st.button("Add task"):
        # Pet.add_task stores the Task on the selected pet (and records the pet's name on it).
        selected_pet.add_task(Task(task_title, int(duration), priority, frequency))

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "Pet": task.pet_name,
                "Task": task.title,
                "Minutes": task.duration_minutes,
                "Priority": task.priority.name.title(),
                "Frequency": task.frequency.value.title(),
            }
            for task in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
