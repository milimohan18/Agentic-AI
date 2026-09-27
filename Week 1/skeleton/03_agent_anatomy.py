"""
03 · Agent anatomy — design a task-execution agent blueprint.

   >>> THIS IS YOUR WEEK 1 DELIVERABLE. <<<

Every agent, from a toy to a production system, is made of four parts:
    GOAL     — what it's trying to achieve (and how we know it's done)
    TOOLS    — how it acts on the world (APIs, code, search, databases)
    MEMORY   — what it remembers between steps
    ACTIONS  — the sequence of steps it takes

A worked EXAMPLE is filled in for you below. Study it, then design YOUR OWN
agent for a real, repetitive, multi-step task you'd like to automate.

-------------------------------------------------------------------
YOUR TASK
  TODO: Fill in `my_agent` with your own blueprint. Keep the task realistic
        and bounded. Be specific about `done_when` — a vague goal can't be
        evaluated. Then run the file to print your blueprint.
-------------------------------------------------------------------
No LLM/API key needed for this exercise — it's pure design.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AgentBlueprint:
    name: str
    goal: str
    done_when: str
    tools: List[str] = field(default_factory=list)
    memory: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)

    def show(self):
        print("=" * 60)
        print(f" AGENT BLUEPRINT: {self.name}")
        print("=" * 60)
        print(f"GOAL       : {self.goal}")
        print(f"DONE WHEN  : {self.done_when}")
        print("TOOLS      :")
        for t in self.tools:
            print(f"   - {t}")
        print("MEMORY     :")
        for m in self.memory:
            print(f"   - {m}")
        print("ACTIONS    :")
        for i, a in enumerate(self.actions, 1):
            print(f"   {i}. {a}")
        print()


# ---------------------------------------------------------------------------
# WORKED EXAMPLE (already complete) — a restaurant-booking agent
# ---------------------------------------------------------------------------
example = AgentBlueprint(
    name="Restaurant Booking Agent",
    goal="Book a dinner table for 4 people this Friday at 8 PM near the user.",
    done_when="A confirmed booking (with a reference number) exists, or the user is told none is available.",
    tools=[
        "restaurant_search(area, cuisine) -> list of places",
        "check_availability(place, date, time, party_size) -> bool",
        "make_booking(place, date, time, party_size) -> confirmation",
    ],
    memory=[
        "User preferences (cuisine, budget, location)",
        "Places already tried (so it doesn't repeat)",
        "The current best candidate",
    ],
    actions=[
        "Search restaurants matching the user's preferences",
        "For each candidate, check availability for Friday 8 PM, party of 4",
        "If available, make the booking and return the confirmation",
        "If none available, report back and suggest alternative times",
    ],
)


# ---------------------------------------------------------------------------
# YOUR BLUEPRINT — TODO: design an agent of your own
# ---------------------------------------------------------------------------
my_agent = AgentBlueprint(
    name="Weekly Assignment Tracker Agent",
    goal=("Every Sunday evening, collect all course assignments due in the next 7 days, "
          "check which ones I've already pushed to GitHub, and send me one prioritised "
          "to-do list for the week."),
    done_when=("A single to-do message has been sent that lists EVERY assignment due in the "
               "next 7 days, each marked DONE (a matching commit exists) or PENDING, sorted by "
               "due date — or a message saying nothing is due this week."),
    tools=[
        "read_course_readme(week) -> list of {task, due_date} from the week's README / action items",
        "list_github_commits(repo, since) -> list of {message, files_changed, date}",
        "calendar_lookup(start, end) -> my busy slots for the week (to suggest when to work)",
        "send_message(channel, text) -> delivery confirmation (email or WhatsApp)",
    ],
    memory=[
        "Which course repo(s) and branch to check",
        "Assignments found this run and their DONE/PENDING status",
        "Last week's list, so carried-over PENDING items are flagged as overdue",
        "My preferred delivery channel and time",
    ],
    actions=[
        "Read the current and next week's README to collect tasks and due dates",
        "Fetch commits pushed since the start of the week",
        "Match each task to a commit (by file name / commit message); mark DONE or PENDING",
        "Compare with last week's list and flag anything overdue",
        "Look up free calendar slots and attach a suggested time to each PENDING task",
        "Sort by due date and send the to-do list; stop once delivery is confirmed",
    ],
)


if __name__ == "__main__":
    example.show()
    my_agent.show()
