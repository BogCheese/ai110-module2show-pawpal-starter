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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
