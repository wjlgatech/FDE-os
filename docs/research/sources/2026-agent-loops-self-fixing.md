# Source — "Agent Loops that fix themselves" (2026)

**Provenance (read this first — honesty discipline).** This text circulated on LinkedIn in 2026,
posted **verbatim and identically** by both **Andrew Ng** and **Shubham Saboo**. It is therefore
**one piece of content, not two independent sources** — do not treat the duplicate as
corroboration (same rule we applied to the Accenture citations). The post credits the full guide as
**co-authored with Aakash Gupta**, and points to the reference repo
**https://github.com/aakashg/pm-github-workflow-repo** (`aakashg` = Aakash Gupta). Attribution of
the verbatim reposts is taken at face value but not independently verified.

**Audience:** AI Product Managers ("the AI PMs getting hired in 2026"). FDE-os's audience is
Forward Deployed / agentic-AI engineers — adjacent, not identical.

---

## The post (verbatim)

> The AI PMs getting hired in 2026 run Agent Loops that fix themselves 🤯
>
> Forget prompting. The AI PMs who win are running loops that test their own work, keep what wins,
> and revert what breaks while they sleep.
>
> Here's the complete loop, start to finish.
>
> Your CLAUDE.md, your skills, your eval criteria change every single week. And when the AI starts
> ignoring half your instructions, you have no idea what broke or when.
>
> A loop fixes that. It's not "the agent does a task." It's a cycle the AI runs over and over to
> keep its own work high quality.
>
> • You tweak one line in your launch checklist.
> • The agent runs a task using that new version.
> • A scoring system checks the output.
> • Score goes up, you keep the change. Score drops, you revert instantly.
> • Then you commit that history to GitHub.
>
> GitHub becomes the memory layer. It remembers which wording made the AI better and which one
> broke it. You stop guessing and your workspace starts improving on its own.
>
> This is also where the artifact lifecycle lives. Most prompts should die. The ones you reuse
> mature into versioned assets.
>
> A one-off prompt becomes a repeated workflow, hardens into a structured skill file, earns eval
> criteria to prove its quality holds, moves into your shared team repo, and eventually runs on its
> own as an automation.
>
> That only works if every step is tracked, diffable, and reversible. Which is the entire reason
> version control sits underneath all of it.
>
> A prompt is not scalable. You copy paste it every time and redo the same work. A versioned,
> evaluated, looping artifact controls how your AI acts every single day without you touching it.
>
> Co-authored this full guide with Aakash Gupta. Full guide dropping soon.

## Reference repo (researched 2026-06-26)

`github.com/aakashg/pm-github-workflow-repo` — a **practice repo for PMs** learning to version
AI artifacts. Thesis: *"the git history IS the lesson."* Structure:

- `CLAUDE.md` (workspace config to customize)
- `skills/` — `prd-reviewer/SKILL.md` (evolved v1→v7 in git history), `competitor-scan/`,
  `feedback-synthesizer/`
- `evals/` — binary pass/fail criteria files + `how-to-write-eval-criteria.md`
- `autoresearch/` — the self-improving loop: a seed prompt + `eval-criteria.md` + `run-log.md`
- `decisions/`, `examples/`, `.github/workflows/gitleaks.yml` (secret scan)

**Their loop, concretely** — `autoresearch/run-log.md` is a 4-column table
(Round │ Change │ Score │ Verdict) tracing 41% → 68% → 79% → 90%, then a Round-4 regression to 82%
that was **reverted** back to 90%. "What the loop learned": forcing a concrete number gave the
biggest single gain (+27 pts); brand voice + legal stay **human checks, outside the loop**.

**Their eval criteria** — each is *"a binary question with a concrete PASS and FAIL example"*
(e.g. "Does the response reference only the knowledge base?"), scored 1/0, averaged 0.00–1.00;
"review the first Monday of each month"; calibrate on 20+ inputs.
