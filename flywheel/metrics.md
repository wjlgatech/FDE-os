# Delta pipeline metrics

The few signals that tell us the loop actually closed — and the **gates** they feed. A tracked
ledger, not a dashboard (per roadmap U7 / KTD2: build nothing custom until flow exists).

**Guardrail (R3):** every public surface must route to the owned hub. *If a surface didn't
capture an email, it didn't count.* Reach without conversion is vanity.

## The funnel (per post)

One row per post. Fill from the platform's own analytics + the email provider's subscriber delta.

| Post | Signal reach | Signal saves | FM read-through | **Email conversions** | Field Kit forks | War-story replies | Kit-usefulness¹ |
|---|---|---|---|---|---|---|---|
| 01 — The Delta Loop | — | — | — | — | — | — | — |

¹ **Kit-usefulness** = independent forks/runs from *outside* the post's audience — the falsifiable
test of "content IS product." A kit nobody outside the readership runs is a byproduct, not tooling.
This is distinct from raw fork count (which can be vanity from the post's own readers).

**Email conversions is the only owned metric** — the one number that survives an algorithm change.
Weight it accordingly.

## Gate A — Stage 1 → Stage 2 (proof, not just mechanics)

Entering Stage 2 (investing in automation) requires that Post #1 *earned attention*, not merely
that the pipeline ran. Minimum to pass:

- [ ] Owned-list conversions from Post #1 **> 0** (the loop converted at least one stranger)
- [ ] Field Kit forks **≥ 5** (the asset was worth taking)
- [ ] TRUE gate passed pre-publish (recorded, not a funnel metric)

If Gate A is missed: the pipeline works but the content didn't land — **iterate the post / topic,
do not automate a loop that produces content nobody converts on.**

## Gate B — Stage 2 → Stages 3/4 (the funding floor)

The load-bearing bet of the whole roadmap: content traction funds the heavy stages. Before
committing to flywheel infra (Stage 3) or the course (Stage 4), the engine must clear a quantified
floor **across posts 1–4**:

- [ ] _Threshold TBD from posts 1–4 data_ — candidate: a sustained per-post owned-list conversion
      rate + a Field-Kit-fork count, held over the four posts (see plan Open Questions).

**If the floor is missed, the default branch is to iterate content — not to proceed.** The heavy
stages hold. This is what makes the staged sequencing real rather than sequencing-in-name-only.

## How to update

After each post's first ~2 weeks: fill its funnel row from platform analytics + the provider's
subscriber delta, then re-check whether the active gate's boxes are all ticked. Reconcile the
email-conversion number against the provider's actual subscriber count (the validity check).
