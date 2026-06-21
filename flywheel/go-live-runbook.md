# Stage 1 Go-Live Runbook

Everything that blocks the roadmap is in here, turned into a ~30-minute checklist. These are the
**outward, account-owning actions a human must take** (publishing, creating forms) — code can't do
them. Do these, record the numbers, and **Gate A** unlocks Stage 2.

Order matters: hub before post (so the post has somewhere to convert to).

---

## Step 1 — Wire the email list (~10 min)  · unblocks U5

1. Create a free **ConvertKit / Kit** account → create a **Form** (type: inline/embed).
2. From the form's settings, copy its **Form ID** (the number in the form's action URL,
   `app.kit.com/forms/<THIS>/subscriptions`).
3. In `delta-community-landing.html`, replace `KIT_FORM_ID = "REPLACE_WITH_KIT_FORM_ID"` with that id.
4. In Kit: set up a one-email **welcome sequence** that includes the Delta chat invite link.
5. Confirm the GDPR/unsubscribe footer is intact (it already ships in the page).
6. **Test:** open the page, submit your own email → you should land in Kit and get the welcome email.

## Step 2 — Stand up the rooms (~5 min)  · unblocks U5

1. Create the **Delta Discord** (one #welcome + one #war-stories channel is enough). Paste a warm
   welcome message. Put the invite link into the Kit welcome email (Step 1.4).
2. Create **`r/ForwardDeployed`** on Reddit — zero-cost flag-plant, no content needed yet.

## Step 3 — Publish Post #1 (~10 min)  · unblocks U6

Pre-flight (already passing — re-run if you edited the draft):
```
python3 skills/true-scorer/scripts/score.py Delta-01-field-manual.md   # must PASS (12/12)
```
Then:
1. Post the **Signal** (`Delta-01-linkedin.md`) as a native LinkedIn post. **Put the link to the
   Field Manual / landing page in the FIRST COMMENT, not the body** (body links cut reach ~60%).
2. Publish the **Field Manual** (`Delta-01-field-manual.md`) as a LinkedIn **Newsletter**; link the
   Field Kit (`field-kits/delta-discovery-protocol/`).
3. Drop the **war-story prompt** into the Discord #war-stories channel.
4. For the first 30–60 min, **reply to every comment** (LinkedIn's dwell-time signal).

## Step 4 — Read Gate A (~after ~2 weeks)  · unlocks Stage 2

Fill Post #1's row in `flywheel/metrics.md`, then check the gate:

- [ ] Owned-list conversions **> 0** (the post converted at least one stranger to the email list)
- [ ] Field Kit forks **≥ 5**
- [ ] (recorded) `true-scorer` passed pre-publish

**If all checked → Gate A passes.** Tell me, and I'll start Stage 2 (the `dreammaketrue` draft
wiring U9, posts 2–4 U10, runbook U11).

**If not → do not automate.** Iterate the post/topic; a pipeline that ships content nobody converts
on isn't worth systematizing. That's the gate doing its job, not a failure.

---

## What I (the agent) will do the moment you report Gate A

- **Pass:** wire `dreammaketrue` as the draft engine (U9), draft posts 2–4 from the spine, score
  each with `true-scorer`, mint each Field Kit with `field-kit-generator`, write the production
  runbook (U11). All gated work, unlocked.
- **One-liner I can do now if you give me the Form ID:** drop `KIT_FORM_ID` into the landing page
  (Step 1.3) as a one-line PR — the only part of Step 1 that's code, not an account action.
