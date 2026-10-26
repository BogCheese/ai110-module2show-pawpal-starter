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

## Features

- **Multiple pets, one schedule.** An owner can have any number of pets, and the scheduler reads every pet's tasks together through `Owner.get_all_tasks()`.
- **Priority-based daily plan.** Tasks are chosen greedily: high priority first, then shorter tasks, then pet order, until the owner's available minutes run out. Tasks that don't fit are skipped with a reason.
- **Preferred times with a fallback.** A task is placed at its preferred time if that slot is free. Otherwise it goes in the earliest free slot after the day's start time.
- **Sorting by time.** Tasks can be listed in time order, with tasks that have no preferred time last (`Scheduler.sort_by_time()`).
- **Filtering.** Tasks can be filtered by pet, by completion status, or both (`Owner.filter_tasks()`).
- **Conflict warnings.** Tasks whose preferred times overlap, for the same pet or different pets, produce a readable warning instead of an error (`Scheduler.detect_conflicts()`).
- **Daily and weekly recurrence.** Completing a repeating task creates the next one, due tomorrow (daily) or in 7 days (weekly). Completing the same task twice does not create duplicates.
- **Explained plans.** Every scheduled and skipped task comes with a plain-language reason (`Scheduler.explain_plan()`).
- **Tested.** 26 automated tests cover scheduling, sorting, filtering, recurrence, conflicts, and edge cases.

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

Run the tests with:

```bash
python -m pytest
```

The 26 tests in `tests/test_pawpal.py` cover:

- **Basics:** marking a task complete, adding a task to a pet, and editing a task (unknown fields and `id` are rejected).
- **Sorting:** tasks come back in time order with untimed tasks last, equal times keep their order, and an empty list or the original list is left unchanged.
- **Filtering:** by pet, by completion status, and by both, plus an unknown pet returning nothing.
- **Recurring tasks:** a daily task creates a copy due tomorrow, a weekly task one due in 7 days, a one-time task creates nothing, a late completion is still due tomorrow, and completing the same task twice doesn't duplicate it.
- **Conflict detection:** same-time and overlapping tasks (same pet and different pets) are flagged, back-to-back, completed, and untimed tasks are not, and three tasks at one time give three warnings.
- **Scheduling:** priority order, skipping tasks that don't fit or are already completed, ignoring tasks not due yet, moving a clashing task to the next free slot, and empty cases (no pets, a pet with no tasks).

Output of a successful run:

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\Brand\Desktop\Codepath A110\ai110-module2show-pawpal-starter
configfile: pytest.ini
plugins: anyio-4.15.1
collected 26 items

tests\test_pawpal.py ..........................                          [100%]

============================= 26 passed in 0.08s ==============================
```

**Confidence Level: ★★★★☆ (4 out of 5)**

All 26 tests pass, and they cover the main behaviors and the edge cases I could think of, including one real bug found and fixed (completing a recurring task twice). I'm not giving 5 stars because month and year rollover for recurring dates isn't tested, the Streamlit UI has no automated tests, tasks that cross midnight display without a "next day" marker, and the greedy scheduler can pick a worse plan than the best possible one.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by preferred time; tasks with no time go last. |
| Filtering | `Owner.filter_tasks()` | Filters by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns when two tasks' preferred times overlap. |
| Recurring tasks | `Task.mark_complete()`, `Pet.complete_task()` | Completing a daily or weekly task creates the next one. |

### Sorting

`Scheduler.sort_by_time(tasks)` returns a new list ordered by `preferred_time` (stored as minutes since midnight), earliest first. Tasks without a preferred time go at the end, and the original list is not changed. Separately, `Scheduler.generate_plan()` orders tasks by priority (high first), then shorter duration, then pet order, and the finished `DailyPlan` is always listed by start time.

### Filtering

`Owner.filter_tasks(pet_name=None, completed=None)` returns the tasks that match. Leave a filter as `None` to ignore it, or give both to require both. For example, `owner.filter_tasks(pet_name="Mia", completed=False)` returns Mia's unfinished tasks.

### Conflict detection

`Scheduler.detect_conflicts()` looks at every pair of pending tasks (due today or earlier, and not completed) that have a preferred time, across all pets. Two tasks conflict when each starts before the other ends, so identical times and partial overlaps are both caught, while back-to-back tasks are fine. It returns a list of warning messages (empty if there are none) and never raises an error or changes any task. When `generate_plan()` later builds the schedule, it resolves a clash by keeping the higher-priority task at its time and moving the other to the earliest free slot.

### Recurring tasks

Each `Task` has a `frequency` (`ONCE`, `DAILY`, or `WEEKLY`) and a `due_date`. `Task.mark_complete()` marks the task done and, for a repeating task, returns a copy that is not completed and is due today + 1 day (daily) or today + 7 days (weekly), calculated with `timedelta`. `Pet.complete_task(task)` calls it and adds the new task to the pet. `generate_plan()` only includes tasks due on or before the plan date, so tomorrow's copy stays out of today's schedule.

## 📸 Demo Walkthrough

Start the app with `streamlit run app.py`. You can also try the logic without the UI by running `python main.py`.

### What you can do in the app

- **Owner:** set your name and how many minutes you have available today.
- **Pets:** add a pet with a name and species. A table lists your pets and how many tasks each has.
- **Tasks:** pick a pet, then give the task a title, duration, priority, frequency (once, daily, or weekly), and an optional preferred time.
- **Your tasks:** see all tasks in a table sorted by time, and filter it by pet and by status (all, to do, done).
- **Conflict warnings:** if two tasks' preferred times overlap, an orange warning names both tasks and tells you how to fix it. A green message appears when there are no conflicts.
- **Mark a task complete:** finish a task, and if it repeats the app tells you when the next one is due.
- **Build Schedule:** generate today's plan, with a summary, a table of start and end times with the reason for each, and a list of tasks that were left out.

### Example workflow

1. Set the owner to "Jordan" with 120 minutes available.
2. Add two pets: Buddy (dog) and Mia (cat).
3. Add a "Walk" for Buddy (30 min, high priority, daily, 9:00 AM) and "Meds" for Mia (10 min, high priority, once, 9:00 AM).
4. Look at the task table, which is sorted by time. A conflict warning appears because both tasks want 9:00 AM.
5. Click **Generate schedule**. Meds (shorter, so it goes first) keeps 9:00 AM, and Walk moves to the earliest free slot at 8:00 AM. The Why column explains each choice.
6. Select "Walk" under **Mark a task complete**. Because it is daily, the app creates tomorrow's Walk and the conflict goes away for today.

### Scheduler behaviors shown

- **Sorting:** tasks added out of order are listed by time of day.
- **Conflict warnings:** overlapping tasks are flagged for the same pet and across pets, without crashing.
- **Priority and time budget:** higher-priority tasks are scheduled first, and tasks that don't fit are skipped with a reason.
- **Preferred time fallback:** a task that loses its slot is moved to the next free one.
- **Recurrence:** completing a daily task adds a copy due tomorrow, which stays out of today's plan.
- **Filtering:** tasks can be narrowed to one pet or to done or unfinished tasks.

### Sample CLI output

Output from `python main.py`. It adds tasks out of order, shows sorting and a conflict check, completes a daily task, filters tasks, and prints the final schedule:

```
Owner: Jordan (120 minutes available)
Pets: Buddy, Mia

Tasks sorted by time:
    7:00 AM  Morning walk (Buddy) [to do, due 2026-10-25]
    7:00 AM  Flea treatment (Buddy) [to do, due 2026-10-25]
    7:15 AM  Feed breakfast (Mia) [to do, due 2026-10-25]
    8:00 AM  Give medication (Mia) [to do, due 2026-10-25]
   12:00 PM  Play with laser (Mia) [to do, due 2026-10-25]
    6:00 PM  Brush coat (Buddy) [to do, due 2026-10-25]

Conflict check:
  Conflict: Morning walk (Buddy, 7:00 AM-7:30 AM) overlaps Flea treatment (Buddy, 7:00 AM-7:10 AM)
  Conflict: Morning walk (Buddy, 7:00 AM-7:30 AM) overlaps Feed breakfast (Mia, 7:15 AM-7:25 AM)

Completed 'Morning walk'; next one is due 2026-10-26.

Mia's tasks:
   12:00 PM  Play with laser (Mia) [to do, due 2026-10-25]
    8:00 AM  Give medication (Mia) [to do, due 2026-10-25]
    7:15 AM  Feed breakfast (Mia) [to do, due 2026-10-25]

Completed tasks:
    7:00 AM  Morning walk (Buddy) [done, due 2026-10-25]

Today's Schedule
----------------
7:00 AM - 7:10 AM  Flea treatment (Buddy)
7:15 AM - 7:25 AM  Feed breakfast (Mia)
8:00 AM - 8:05 AM  Give medication (Mia)
12:00 PM - 12:20 PM  Play with laser (Mia)
6:00 PM - 6:15 PM  Brush coat (Buddy)
Total: 60 minutes

Skipped:
- Morning walk (Buddy)

Why this plan:
- Flea treatment: medium priority, placed at its preferred time 7:00 AM
- Feed breakfast: high priority, placed at its preferred time 7:15 AM
- Give medication: high priority, placed at its preferred time 8:00 AM
- Play with laser: medium priority, placed at its preferred time 12:00 PM
- Brush coat: low priority, placed at its preferred time 6:00 PM
- Morning walk (skipped): already completed
```

In this run the morning walk was completed before the schedule was built, so it is skipped as "already completed", and tomorrow's copy is not part of today's plan.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
