# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. **Add a pet (and owner info).** The user enters basic details about themselves and their pet (name, species, how much time they have available each day) so the app knows who the plan is for.
2. **Add and edit care tasks.** The user creates tasks such as walks, feeding, meds, or grooming, giving each a duration and a priority, and can change or remove them later.
3. **Generate and view today's plan.** The user asks the app to build a daily schedule from their tasks, time available, and priorities, then sees the ordered plan along with an explanation of why each task was included or left out.

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML (see [diagrams/uml.mmd](diagrams/uml.mmd)) uses five classes. An `Owner` has one or more `Pet`s, and each `Pet` has zero or more `Task`s. A `Scheduler` reads from the `Owner` and creates a `DailyPlan`. I split the classes so that data (who and what), logic (how to schedule), and output (the resulting plan) each live in their own place.

- **Owner:** holds the owner's name, how many minutes they have available each day, their preferences, and their list of pets. It adds and removes pets, and `get_all_tasks()` gathers every task across all pets so the scheduler doesn't need to know how pets are organized.
- **Pet:** holds the pet's name, species, and its own list of tasks. It is responsible for adding, editing, and removing its tasks, which covers the "add and edit care tasks" action.
- **Task:** represents one care activity (walk, feeding, meds, grooming) with a title, duration, priority, completion status, and optional preferred time. It can mark itself complete and convert its priority (low/medium/high) into a number via `priority_value()` so tasks can be sorted.
- **Scheduler:** the "brain" of the app. It holds a reference to an `Owner`, and `generate_plan()` decides which tasks fit in the available time and in what order. `explain_plan()` produces the plain-language reasoning for the result. It keeps scheduling logic out of the data classes.
- **DailyPlan:** the result of scheduling. It stores the scheduled items with start times, the skipped tasks with reasons, the total minutes used, and the reasoning notes. `display()` formats it for the user, so the UI can show a plan without knowing how it was built.

`Task`, `Pet`, `Owner`, and `DailyPlan` are Python dataclasses because they mainly store data. `Scheduler` is a regular class because it mainly provides behavior.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

After an AI review of my class skeleton, I changed the following:

- **`Task` links back to its pet (`pet_name`) and has a unique `id`.** Without this, a plan couldn't say which pet a task was for, and identical tasks were indistinguishable. `Task` now uses identity equality so it can also go in sets and dicts.
- **Times are minutes since midnight, and `priority` is a `Priority` enum.** Strings couldn't be compared or added, and a typo in a priority string would break sorting.
- **`DailyPlan` stores `ScheduledItem` and `SkippedItem` objects, each with a reason, and `total_minutes` is computed.** This replaces the untyped tuple lists and the separate `reasoning` list. It gives one source of truth for the "why" and stops the total from drifting out of sync.
- **`Owner` gained `day_start_minute` and a typed `Preferences` class.** The scheduler needs a start time, and an untyped dict left it unclear which preferences exist.
- **`Owner` to `Pet` is now `0..*` in the UML**, since an owner exists before adding a pet.
- **`edit_task` must reject unknown fields, and `generate_plan` documents its rules** (skip completed tasks, greedy by priority then duration then pet order, honor preferred time when free). This makes the scheduler's behavior and its tradeoff explicit.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers the owner's available minutes for the day, each task's priority and duration, an optional preferred time, the owner's day start time and an optional buffer between tasks, and whether a task is already completed or not yet due.

I ranked them by what hurts most if it goes wrong. The time budget is a hard limit, because no plan can use more minutes than the owner has. Priority comes next, since a high-priority task like medication should never lose its place to grooming. A preferred time is only a soft preference: if the slot is taken, the task moves to the earliest free slot instead of being dropped. That order means a conflict can change when a task happens, but never whether an important task happens.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler is greedy: it sorts tasks by priority (then shorter duration) and takes each one if it still fits in the owner's remaining minutes. It never tries other combinations, so it can pick a worse overall plan. For example, with 60 minutes available, one 50-minute high-priority task gets scheduled and three 20-minute medium-priority tasks are skipped, even though the three smaller tasks together might matter more to the owner. Finding the best combination is a harder "knapsack" problem.

This is reasonable for PawPal+ because an owner has only a handful of tasks, high-priority care like medication should always win, and a greedy plan is easy to explain ("this was high priority, so it went first"). I made the same kind of choice when reviewing `detect_conflicts()`. A faster version that stops comparing once tasks no longer overlap exists, but I kept the simple "compare every pair" loop and only moved the overlap rule and the message into small named helpers, because readability matters more than speed for a few tasks. A related limit is that conflict detection only checks preferred times, and the scheduler resolves a clash by quietly moving the lower-priority task to the earliest free slot instead of asking the owner.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI to turn my UML into dataclass skeletons, to review that skeleton for missing relationships and logic problems, to implement the four core classes, and to write `main.py` and the first two pytest tests. The most helpful prompt was asking it to review my skeleton for "missing relationships or potential logic bottlenecks", because it caught problems before any scheduling code existed (no link from a task back to its pet, string times that can't be compared, and two tasks that look identical being treated as the same task).

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI's review gave 13 suggestions. I accepted the ones that fixed real problems (task-to-pet link, unique task identity, numeric times, a `Priority` enum, computed `total_minutes`, validated `edit_task`), but the AI did not fully act on two of them: tasks that repeat daily only got a stored `frequency` field and don't change scheduling yet, and `Preferences` only has a placeholder `buffer_minutes` that the AI chose without asking me. I also told the AI to keep the questions in this file and to keep the README placeholder text instead of letting it rewrite them.

To verify, I ran `python main.py` and read the schedule against what I expected (two pets, tasks at their preferred times, the explanation matching the plan). In an earlier test run, two tasks wanted 9:00 AM and the shorter one won, which matched my tie-break rule but is something I would want to confirm is the behavior I want. I then added two pytest tests (`mark_complete()` changes status, adding a task increases a pet's task count) and ran `python -m pytest`, which passed.

**c. AI strategy**

- Which AI coding assistant features were most effective for building your scheduler?
- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
- How did using separate chat sessions for different phases help you stay organized?
- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.

The most effective features were asking the AI to review my design before writing logic, letting it edit several files at once so the code, tests, demo, and UML stayed in sync, and having it run the code instead of just writing it. Running things found two real bugs that reading the code did not: completing the same recurring task twice created duplicate copies, and Streamlit's `st.selectbox` hands back a copy of an object, so tasks added in the app were silently lost.

One suggestion I rejected was a faster, more compact version of `detect_conflicts()`. The AI offered a sweep that stops comparing early (faster) and a single list comprehension with the message built inline (shorter). I kept neither, because an owner has only a handful of tasks and both were harder to read. I took only the part that helped: moving the overlap rule and the message into small named helpers. I also changed the AI's first recurring-task code, which counted from the old due date, so it counts from today (today + 1 day), as the requirements say.

I did most of this project in one long chat session, so I did not get the separation that separate chats would give. I stayed organized by working in clear phases with a file for each (UML, class skeleton, logic, `main.py` demo, tests, then `app.py`) and by checking each phase before moving on. Next time I would start a fresh chat for testing, so the AI reviews the code without remembering how it wrote it.

As lead architect, I learned that the AI is fast at writing code but the decisions are mine: what the classes are, what the scheduling rules are, and what "done" means. When I left a gap, such as the placeholder `Preferences` field, the AI filled it with a guess, so I need to state requirements clearly and check what it assumed. Reading its output, running it, and testing it mattered more than the typing speed it saved.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 26 tests in `tests/test_pawpal.py`. They cover marking tasks complete and adding or editing tasks, sorting by time (including untimed tasks, equal times, and an empty list), filtering by pet and status, recurring tasks (daily, weekly, one-time, late completion, and completing twice), conflict detection (same pet, different pets, back-to-back, completed and untimed tasks, and three tasks at one time), and scheduling (priority order, tasks that don't fit, completed tasks, tasks not due yet, and empty cases).

They matter because the scheduler's value is that its decisions are right and explainable, and a plan that silently drops a medication task or double-books the owner would be worse than no plan. The tests also found a real bug (duplicate recurring tasks) that I would not have noticed from the demo output.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am fairly confident, about 4 out of 5. All 26 tests pass and they cover the main behaviors and the edge cases I could think of. I am not at 5 because some things are untested, and the greedy scheduler can pick a worse plan than the best possible one.

With more time I would test month and year rollover for recurring dates (this needs a faked clock), tasks that cross midnight, the buffer between tasks, two pets with the same name (filtering is by name), and the Streamlit app itself, which has no automated tests.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied that the scheduler explains itself. Every task in the plan has a reason ("high priority, placed at its preferred time"), and every skipped task says why, so the owner never has to guess. I am also happy that the layers stayed separate: the classes in `pawpal_system.py` know nothing about Streamlit, so the same logic works from `main.py`, the tests, and the app.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would replace the single "available minutes" number with real time windows, so a task can't land late in the evening on a short day. I would handle tasks that cross midnight and let the owner choose how to resolve a conflict instead of the scheduler moving a task quietly. I would also let the app edit and delete tasks, expose the day start and buffer settings, and save data to a file, because everything is lost when the browser tab is refreshed. Finally, I would try a smarter search than greedy for choosing which tasks fit.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Design the structure and the rules first, then let the AI fill in code, and always verify what it gives you. Reviewing my class skeleton before writing any scheduling logic saved me from several problems later, and running the code and tests caught bugs that looked fine when I read them. The AI can write a lot of code quickly, but I am still responsible for deciding what the system should do and for checking that it does.
