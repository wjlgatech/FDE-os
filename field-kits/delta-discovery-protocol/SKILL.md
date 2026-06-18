---
name: delta-discovery-protocol
description: Run a Forward-Deployed-Engineer-style discovery to capture the scarce tacit context behind a customer problem BEFORE building. Use when starting a new deployment or engagement, scoping an AI/software solution for a customer, when requirements feel thin, vague, or suspiciously clean, or when a stakeholder hands you a "list of requirements" and you sense the real problem is hidden underneath. Produces a structured Site Survey artifact.
---

# Delta Discovery Protocol

> Field Kit for Delta · Field Manual 01. The reusable half of "The Delta Loop."
> Principle: **context is what's scarce.** A requirements doc is a lossy compression of a reality the customer can't fully articulate. This protocol decompresses it.

## When to run this

- Kicking off a new customer deployment or internal project.
- The stated requirements feel thin, too clean, or politically sanitized.
- You're about to build from a spec you didn't watch get made.
- Before — not after — writing production code.

## What it produces

A **Site Survey**: a one-page structured artifact that captures the real workflow, the data reality, the political map, and the true definition of success — the thing a Forward Deployed Engineer builds before touching the product. Template at the bottom.

## The protocol — five passes

Work through these in order. Do not skip to building. If you're an AI agent, ask the user the questions in each pass and refuse to produce the Site Survey until passes 1–4 have real answers (mark unknowns explicitly as RISKS, never invent them).

### Pass 1 — Get on the plane (immerse in the real, not the reported)
Goal: see the work as it actually happens, not as it's described in a deck.
- Who actually does this work, day to day? (Not the buyer — the operator.)
- Walk me through the last real instance of this task, step by step, including the annoying parts.
- What do people do *outside* the official system — the spreadsheets, the side-channels, the "we just text Maria"?
- Where does the current process break, and what's the workaround everyone pretends isn't there?

### Pass 2 — Map the real workflow (vs. the stated one)
Goal: separate the official process from the lived one.
- Stated workflow: what the org *says* happens.
- Actual workflow: what *really* happens, including the undocumented steps.
- The deltas between them = where the real value (and risk) lives.

### Pass 3 — Find the data reality
Goal: surface the integration truth early — it is almost always the hidden bottleneck.
- What data does this actually need, and where does it live?
- Who controls access, and how long will getting it really take? (Assume longer.)
- What's the quality/format truth — clean API, or a nightly CSV email and three legacy systems?
- What can't leave the customer's perimeter (security, residency, compliance)?

### Pass 4 — Map the political terrain
Goal: name the human dynamics that decide whether anything ships.
- Who wins if this succeeds? Who loses, or feels threatened?
- Whose sign-off is required, and whose quiet veto can kill it?
- Who is the internal champion, and how exposed are they if it fails?
- What's the org actually rewarded for — which may differ from the stated goal?

### Pass 5 — Define true success
Goal: replace the vanity metric with the outcome that matters.
- What business outcome makes this undeniably worth it? (In their numbers, not yours.)
- What does "it works" look like to the operator at 5pm on a normal day?
- What's the smallest end-to-end win that would build belief? (The first paved inch.)
- How will we know we're wrong early?

## Output: the Site Survey template

```
# Site Survey — <customer / project>
Date: <date>   |   Surveyed by: <name>

## 1. The operator & the real task
- Who does the work:
- Last real instance, step by step:
- Off-system workarounds observed:

## 2. Stated vs. actual workflow
- Stated:
- Actual:
- Key deltas (value + risk live here):

## 3. Data reality
- Data needed / where it lives:
- Access owner + realistic timeline:
- Quality/format truth:
- Perimeter constraints:

## 4. Political map
- Winners / losers if this ships:
- Required sign-offs / silent vetoes:
- Champion (and their exposure):
- What the org is actually rewarded for:

## 5. True success
- Business outcome that matters (their numbers):
- "It works" to the operator:
- Smallest end-to-end win:
- Early signal we're wrong:

## 6. Risks & unknowns (do NOT invent — list gaps)
-

## 7. Recommended first build (the gravel road)
- One narrow, end-to-end slice that proves value and earns the next step:
```

## How to use as an agent skill
1. Load this skill when a discovery/scoping task begins.
2. Run passes 1–5 as a guided interview (one pass at a time; don't dump all questions at once).
3. Populate the Site Survey. Mark every gap as a RISK rather than guessing.
4. End with the "Recommended first build" — the smallest end-to-end slice (the Delta Loop's first paved inch), not a big-bang plan.

## Provenance
Distilled from Palantir's Forward Deployed Engineering practice (the "Delta" role) as documented by Palantir alumni (Nabeel Qureshi, "Reflections on Palantir"; Ted Mabrey, "Sorry, that isn't an FDE") and Palantir's "Dev versus Delta." Part of the Delta series / FDE-os.
