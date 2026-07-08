# JD → knowledge graph + skills, explained (the wired board)

*What the `/jd` pipeline actually does, in a mental model a 12-year-old gets, mapped 1:1 to the code.*

## The story
A job description is a **wall of words** — a person in a big coat. You can't see the skeleton: what
it *really* wants, how the pieces connect, where you're strong or short. Reading harder doesn't help;
fog doesn't get clearer by staring.

So we do what a detective does with a case full of noise: **wire a corkboard.**
1. **Pin the real things** to the board (the concepts + tools the JD names) — nodes.
2. **String yarn** between pins that connect (role → competency → tool) — edges. Now you *see* the shape.
3. **Label each pin honestly** — what it's for *and what it is NOT for*. A label with no "not good at" is a lie.
4. **Staple a photo of the real source** to the board (the public posting URL) — so it's a real case, not a fantasy.
5. **Hang the board where it stays**, and let people **move the pins around** to explore it.
6. **Only the chief can add to the official board**; anyone can read a printout.

That's the whole system: **fog → wired board → honest labels → grounded → pinned → gated.**

## The 1:1 map (kid-word → technical term → the actual move)
| Corkboard word | Technical term | The move (in the code) |
|---|---|---|
| the wall of words | the JD source text | input to `jdToArtifact(jd, title, url)` |
| a pin | a graph **node** `{id, type, name, summary}` | an extracted concept / cluster / tool |
| yarn between pins | a graph **edge** `{source, target, type}` | `role→cluster` (requires), `cluster→tool` (uses) |
| finding the needles | **word-boundary keyword match** over a competency taxonomy | deterministic extraction — **no LLM** |
| honest label | a **skill** `{oneLine, notGoodAt[], verified}` | skillfy; `notGoodAt` is **required** |
| the source photo | `source.url` (must be `http(s)`) | grounding — no URL ⇒ **refused** |
| no phantom yarn | edges whose endpoints aren't nodes are dropped | integrity check |
| a board you can rearrange | force-directed **GraphView** (repel + spring + gravity) | the interactive render |
| pinned so it stays | **persist**: durable KV (Postgres) *or* committed `content/deepen.json` | two tiers |
| official board vs printout | **owner / `INGEST_SECRET`-gated write** vs **public read/build** | the auth boundary |

## The mechanisms, as near-formulas
- **Extraction:** cluster *present* ⇔ ∃ keyword `k ∈ taxonomy(cluster)` matching the JD on a word boundary (so `rust` never matches inside `trust`).
- **Graph:** `nodes = {role} ∪ {present clusters} ∪ {named tools}`; `edges = {role→c : c∈clusters} ∪ {anchor→t : t∈tools}`.
- **Valid ⇔** `source.title` present **∧** `isHttp(source.url)` **∧** every skill has `notGoodAt ≠ ∅` **∧** every edge's endpoints ∈ nodes.
- **May publish ⇔** `isOwner(req)` **∨** `header["x-ingest-secret"] == INGEST_SECRET`.

## Patterns (why it's built this way)
- **Sink, not builder** — the builder makes the artifact; the node *receives + presents*. Separate "make" from "show."
- **Data is the single source of truth** — one artifact JSON drives both the viewer and persistence; nothing can drift.
- **Public read, gated write** — anyone can *build/preview*; only the owner can *publish* to the durable feed.
- **Grounded-or-refused** — observed beats claimed; no real source URL ⇒ no artifact.
- **Honest limits required** — a skill with no "not good at" is dropped.
- **Deterministic over LLM where you can** — a keyword taxonomy is cheap, offline, reliable; save the LLM for what only it can do.

## Antipatterns (the traps this avoids)
- **Ungrounded artifact** (no source URL) → the "prettier résumé" trap → refused.
- **Public write** to the owner's feed → spam/pollution → gated.
- **LLM for a deterministic job** → flaky + costly → keyword extraction.
- **Dangling edges / phantom nodes** → a map that lies → dropped.
- **Skills with no limits** → fluff that reads as competence → dropped.
- **Persisting to serverless ephemeral FS** → silent data loss → durable KV or committed files.

## The transferable mental model (keep this one)
**Fog → wired board → honest labels → grounded → pinned → gated.**

It isn't about JDs. *Any* wall of messy prose — a research paper, a repo, a customer's rambling
requirements, a meeting transcript — becomes a trustworthy, explorable artifact the same way:
**extract nodes + edges, label with honest limits, ground it in a real source, persist + make it
interactive, and gate who can write.** It's the same spine as the rest of this work — *evidence over
claims, a gate on the write, honest about the edges* — pointed at "understand a domain fast."
