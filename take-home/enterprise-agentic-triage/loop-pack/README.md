# Loop knowledge pack — the take-home, RAG-ready

11 curated files so Loop's knowledge base can answer take-home questions near-real-time
during the enterprise interview: solution overview, gap audit + 10X, all 8 core modules
(wrapped as markdown), and the golden-dataset ledger with the honest first-run story.

## Load into Loop (one minute)

1. Loop → Settings (⌘,) → **Knowledge** → upload every `.md` in this folder.
   (Embeddings use the OpenAI key configured in Loop — `text-embedding-3-small`;
   without a key the KB can't embed, but the playbook layers below still work.)
2. Select the **"Deloitte Agentic AI Take-Home"** playbook (named in the private Loop app only) (built-in as of loop PR #33
   on the default branch — rebuild the app to see it; priority 12, auto-triggers on
   enterprise/take-home/triage/golden dataset/…).
3. `playbook.md` already carries the delimited `DELOITTE-TAKEHOME` (private, local-machine only) cheat-sheet block —
   live on every request, no rebuild needed. Delete that block after the interview.

Three layers, by freshness: playbook.md (live now, every request) → built-in playbook
(durable, scenario-triggered) → this KB pack (deep RAG: exact code and case-level answers).

Regenerate after code changes: the pack is derived — re-run the generation snippet in
the repo history (PR that added this folder) or re-copy README/field-note/scripts/golden.
