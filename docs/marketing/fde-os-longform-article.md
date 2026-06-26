# The most copied job in AI doesn't have a school. So I'm building one — and it keeps catching its own mistakes.

*Long-form. ~7 min. Concrete enough for a sharp 15-year-old, honest enough for an AI director who's
seen a hundred decks.*

---

## Start with a number that should not be real

Forward Deployed Engineer job posts grew **1,165%** last year.

That's not a typo. One role, up more than tenfold, in twelve months. The median base is **$173,816**,
**70%** come with equity, and — the part that breaks people's brains — **0%** carry a sales quota.
These are engineers. They just happen to sit *inside the customer's building* instead of yours.

Here's the weird part: almost nobody can tell you how to become one. There's no bootcamp, no
"FDE 101," no clean ladder. The hottest job in AI is being hired faster than anyone is being taught
to do it.

That gap is the whole story. It's also what I'm building a fix for, in public, called **FDE-os**.

## The job, explained like you're fifteen (because the best ideas survive that test)

Imagine you sell software and your biggest customer is the CIA. Now go gather requirements. You
can't. The work is classified. Half of what the operators know lives in their hands, not their
heads. There is no document anyone can email you. Build to the spec they *can* write down, and
you'll ship something technically correct and completely useless.

In 2006, Palantir made a heretical bet. Instead of dragging the problem back to headquarters, they
sent the engineer *forward* — onto the customer's site, into the room where the work actually
happened. They called the role "Delta."

The mental model came from, of all places, a French restaurant. In a bad one, the waiter is a
delivery mechanism: takes your order, brings your food, vanishes. In a *great* one, the waitstaff is
part of the kitchen. They taste the dish, read the table, walk back, and tell the chef the duck is
too salty for table six — and the chef changes the duck. The person at the edge, touching the
customer, is wired straight back into the thing being made.

That wire is the entire job. Call it the **Delta Loop**:

> Deploy → learn the messy truth a spec can't capture → build the hacky thing that works → codify it
> back into the product → repeat.

Service stops being downstream of product. It becomes an *input* to it.

That bet built a company running **80% gross margins** in 2023, while Accenture — the gold standard
of the actual services business — runs about **32%**. Palantir looked like a consulting shop and
earned like software. Now every AI lab on earth is racing to copy the role, because the model is
brilliant and cheap, and the last mile — making it actually *land* inside a real company — is where
all the value pooled. (MIT found **95%** of enterprise AI pilots show no measurable business impact.
The model was never the bottleneck. Landing it is.)

## So what is FDE-os, actually?

Three things that feed each other:

1. **A JD-validated course.** Point it at a real job description — I've run it against Reflection
   AI's and CVS Health's actual FDE postings — and it tells you exactly what to learn, and ships you
   the tools to prove you learned it.
2. **Cross-agent tooling.** A growing kit of small, tested skills any AI agent can run — score a
   draft, evaluate a RAG system for hallucinations, mint a reusable skill, talk MCP.
3. **A field-practice flywheel.** The whole thing is wired as a loop: write an essay → it ships a
   reusable tool → the tool earns a community → the community generates the next field stories →
   which become the next essay. Writing the series *builds* the product. Content production **is**
   product production.

If that sounds abstract, here's the concrete version: there are seven working, tested tools in the
repo right now. A live website. Prep curricula for two real jobs. Every single piece runs offline,
with no API key, and is gated by tests on every commit. It's not a deck. It runs. And it's all a
**forkable Field Kit** — clone the repo, drop a skill into your own agent stack, run it on your own
work. The reusable tool, not just the idea, is the point.

## The part I didn't expect: the way you build it *is* the lesson

Here's what I learned that I think matters far beyond this one project.

The skill that actually separates people in AI right now isn't prompting. It's running a **loop**:
you change one thing, you *score* the result, you keep it if it's better and revert it if it's
worse, and you let the history live in version control so it remembers what worked when you don't.
Prompts are disposable. A versioned, evaluated, looping artifact controls how your AI behaves every
day without you babysitting it.

FDE-os is built that way, on purpose — and it dogfoods itself, sometimes embarrassingly:

- I added a link-checker to keep the repo honest. The first thing it did was flag two of *my own*
  citations as dead 404s. (Turned out the claim was real — Accenture really did launch a Forward
  Deployed Engineering practice in 2026 — but I'd pasted truncated URLs. The robot caught the human.)
- I shipped a signup form that cheerfully told visitors "You're in!" while saving nothing. On a live
  public page. A scorer for honesty would've blocked it; now there is one.
- I wrote a quality gate, then ran this very article through it before you read it.

That's the encouraging secret nobody tells you: **the loop is more forgiving than perfectionism.**
You don't have to be right the first time. You have to be *reversible*, *measured*, and *honest about
what broke*. Git remembers, the gate catches, you move faster precisely because you're allowed to be
wrong out loud.

## Why an AI director should care (the part under the jokes)

Strip the charm and here's the load-bearing claim: the durable unit of AI work is shifting from the
*prompt* to the **evaluated, version-controlled artifact**. Teams that treat quality as a runnable
gate — not a vibe, not a Friday review — ship faster and regress less, because every change is
tracked, diffable, and reversible. FDE-os is a small, legible proof of that thesis you can read in an
afternoon: seven skills, three eval gates, one self-improving loop, a CI that fails the build on a
dead link or a dropped test. The same spine that trains a Forward Deployed Engineer is the spine that
keeps any AI system honest at scale.

The role might become the most durable job in tech. Or — the uncomfortable version — the labs use
armies of FDEs to build the very agents that one day do the FDE's job. Nobody knows yet. That
uncertainty is exactly why it's the most interesting seat in AI, and exactly why having a *system* for
mastering it beats having opinions about it.

## You can start the loop today (no permission required)

Open the last thing you built with an AI. Find the original ask. Count how many requirements turned
out wrong, missing, or quietly renegotiated once you got into the real work. That number is the
deployment gap — the distance between the tidy spec and the messy truth. Every wrong requirement is a
place where being *closer to the real work* would have caught it sooner.

That's the whole job. That's the whole project. And the best time to start your own loop was last
sprint; the second best time is the next commit.

The model is brilliant and getting cheaper by the week. The last mile — the human, political,
duct-tape work of making it land — is the whole race. Come build a home for the people running it.

---

**Links**
- The project (open source): https://github.com/wjlgatech/FDE-os
- Live community door: https://wjlgatech.github.io/FDE-os/
- The system design, with diagrams: [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- Where it all started, the cited research: [`FDE-research-synthesis.md`](../../FDE-research-synthesis.md)

*Sources for the numbers: Bloomberry's 1,000-job FDE analysis (1,165% growth; comp figures —
single-source, methodology shown); Nabeel Qureshi, "Reflections on Palantir" (80% vs 32% margins);
a16z and Sequoia on services-as-software; MIT NANDA (the 95%). Fuller sourcing, with reliability
flags, lives in the repo's research vault — because a project about honesty should show its work.*
