# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Implementation Summary

The logic lives in `pawpal_system.py` and can be tried from the terminal with `python main.py`.

- **`Task`**: one care activity (title, duration, priority, frequency, optional preferred time, completion status).
- **`Pet`**: a pet and its list of tasks. It adds, edits, and removes its own tasks.
- **`Owner`**: has the available minutes for the day and a list of pets. `get_all_tasks()` returns every pet's tasks together.
- **`Scheduler`**: the "brain". `generate_plan()` reads tasks from `Owner.get_all_tasks()` (so all pets are covered), skips completed tasks, orders the rest by priority then duration, and places each one at its preferred time if free or in the earliest free slot until the owner's time runs out.
- **`DailyPlan`**: the result. It holds the scheduled items (with start times and reasons) and the skipped items (with reasons), and `display()` prints it.

How they work together: `Owner` → `Pet` → `Task` hold the data, `Scheduler` reads from the `Owner` and creates a `DailyPlan`. See [diagrams/uml.mmd](diagrams/uml.mmd) for the full class diagram.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

Output from running `python main.py`, which builds an owner with two pets and four tasks and prints the generated schedule:

```
Owner: Jordan (120 minutes available)
Pets: Buddy, Mia

Today's Schedule
----------------
7:00 AM - 7:30 AM  Morning walk (Buddy)
8:00 AM - 8:05 AM  Give medication (Mia)
12:00 PM - 12:20 PM  Play with laser (Mia)
6:00 PM - 6:15 PM  Brush coat (Buddy)
Total: 70 minutes

Why this plan:
- Morning walk: high priority, placed at its preferred time 7:00 AM
- Give medication: high priority, placed at its preferred time 8:00 AM
- Play with laser: medium priority, placed at its preferred time 12:00 PM
- Brush coat: low priority, placed at its preferred time 6:00 PM
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
