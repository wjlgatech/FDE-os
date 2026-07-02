# coding-drill-kit — the no-AI mock harness, as a gate

The Day-1 artifact from the [Google FDE loop case study](../../google-fde-loop-prep-2026-07-07.md),
built as an FDE-os tool: **eval-as-gate applied to a human**. The coding room gives you syntax
highlighting and nothing else, so the drill is *production from memory*, scored mechanically.

## The coding drill (daily, ~20 min)

```bash
cd course/prep/tools/coding-drill-kit
python3 drill.py start                      # → attempts/attempt-<stamp>.py (signatures only)
# open it in a BARE editor — autocomplete OFF, no AI — write all 6 templates from memory
python3 drill.py check attempts/attempt-<stamp>.py
```

`check` runs real unit cases per template (BFS reachability, topo-sort chain + cycle→[],
sliding-window classics incl. `""`, union-find connectivity, LRU eviction order, token-bucket
refill with injectable time) and names exactly what broke. Every run appends to `problems.md` —
the tracker is the eval-loop run-log (Round │ Score │ What broke).

**Gate: 6/6 from a blank page, twice, on different days = coding-room ready.**
A syntax error is scored as a lost round, because in the room it is one.

## The design-round self-score (after each mock)

Do a timed mock (§6 of the case study), *write down what you actually said* as rough notes,
then score the notes against the recruiter's graded areas with `criteria-scorer`:

```bash
python3 ../../../../skills/criteria-scorer/scripts/criteria_score.py score \
    my-mock-notes.md design-self-score.json --threshold 0.9
```

12 criteria = the graded behaviors (discovery-first, PII + tenant isolation, prompt/RAG/fine-tune
tree, cache + stateless scale, groundedness + golden-set monitoring, HITL, cost, GCP names, a real
number). A miss tells you which §6 layer to re-drill — mechanically, not by feel.

`attempts/`, `problems.md`, and your mock notes are yours — gitignored, never committed.
