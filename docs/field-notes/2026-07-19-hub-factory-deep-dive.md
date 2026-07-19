# Deep dive — the hub factory: cited repos → knowledge graphs + agentic tooling (2026-07-19)

The hub thesis: FDE-os is where **knowledge**, **tooling**, and **experts** meet. The repos it
cites are load-bearing inputs to the first two — so they get compiled by a factory
([`skills/repo-compiler`](../../skills/repo-compiler/SKILL.md)), not curated by hand. This note is
the design deep-dive: how the factory stays **high quality, fast, cheap, up-to-date, and
future-proof** — and where each property's ceiling is.

## What exists as of this note

- Registry: [`knowledge/hub/repos.yml`](../../knowledge/hub/repos.yml) — 10 cited repos, star bar 1000.
- Compiled (7 top-rated): awesome-mcp-servers ⭐91k (33 concepts, **2,205 evidence**),
  modelcontextprotocol/servers ⭐89k, ai-engineering-from-scratch ⭐40k, langfuse ⭐31k (245
  evidence), fastmcp ⭐26k, mcp-registry ⭐7k, mlrun ⭐1.7k.
- Per repo: `knowledge/hub/<slug>.graph.json` + an entry in `hub-skills.json` (skill contract +
  integration recipe) + `hub-index.json` (pinned SHAs, compile status).

## The five dimensions, mechanism by mechanism

### 1. High quality — enforced, not hoped for

- **Provenance is pinned.** Every node's `source_url` is a blob/tree URL at a commit SHA —
  it can never drift under you. A graph without a pinned SHA fails `validate_graph`.
- **Contract validation aborts the compile** on dangling edges or missing provenance — a bad
  graph never lands on disk.
- **Honest edges are generated, not optional.** Every tooling entry carries `notGoodAt` by kind
  (curated index: "popularity ≠ safety"; platform: "not zero-ops"; unclear license: extra flag).
- **Fail-loud beats fail-quiet.** The factory's first real run produced a *silently hollow* graph
  for its highest-starred repo: GitHub's JSON readme endpoint returns empty content past 1MB.
  Caught because the output claimed 0 concepts for a 91k-star list — now the fetcher uses the raw
  media type and an empty README warns on stderr. Lesson banked: **assert output plausibility
  against input importance** (a top-rated repo with an empty graph is an error until proven
  otherwise).
- **Ceiling:** README-level semantics. Deeper quality (code architecture, API surfaces) costs a
  clone + `understand-anything` — worth it selectively, not by default.

### 2. Fast — seconds, not minutes

- **API-only:** ~3 calls/repo (meta, HEAD SHA, raw README). No clones — the 91k-star list and the
  monorepo cost the same.
- **O(changed), not O(all):** `refresh` diffs HEAD SHAs (1 call/repo) and names exactly which
  repos need a rebuild.
- **Parallel-safe:** each repo writes only its own graph file; the two registries are written once
  at the end.
- **Ceiling:** GitHub API latency (~300ms/call). At 100+ repos, batch via GraphQL (one query for
  all SHAs) — the fetcher seam is where that lands, nothing downstream changes.

### 3. Cheap — $0 by construction

- Deterministic extraction (regex over markdown, typed rules for classification) — **no LLM on
  the base path**, so cost doesn't scale with repo count or model prices.
- `gh` auth = free API quota (5k/hr authenticated; a full compile uses ~25 calls).
- Where an LLM *would* add value (semantic edges between concepts, summary quality), it's an
  opt-in enrich pass on top of the deterministic skeleton — same posture as knowledgefy and
  rag-eval-harness. The skeleton is always reproducible; the enrichment is never load-bearing.

### 4. Most up-to-date — freshness as a CI signal

- Every artifact records `source.sha` + `pushed_at`; `hub-index.json` is the freshness ledger.
- `refresh` exits **3** on drift. Design correction discovered while wiring CI: active upstreams
  (langfuse commits daily) drift *every* week, so a red-build-on-drift would be permanent noise.
  The shipped semantics: the weekly cron (`freshness.yml → hub-drift`) treats drift as a
  **trigger, not a failure** — it rebuilds (`all --render-html`) and opens a bot PR
  (`bot/hub-refresh`), so main stays PR-only and a human reviews what upstream changed.
- Unreachable repos (renamed, deleted, rate-limited) exit **4** and are reported stale with their
  last-known SHA — **kept, never silently dropped** (a vanished dependency is a signal, not a gap
  to paper over).
- **Ceiling:** freshness of *our copy*, not of the upstream's own accuracy. A stale awesome-list
  that is itself freshly-fetched is still stale knowledge — the star bar and `why_cited` review
  (human, per registry edit) are the guard there.

### 5. Future-proof — seams, specs, and versioned contracts

- **Spec-as-data:** `repos.yml` is the single source of truth. Adding a cited repo = one YAML
  entry; nothing else is hand-edited. The published artifacts are pure functions of registry +
  upstream state.
- **The fetcher seam:** all network lives in `GitHubFetcher`. GitLab, a corporate mirror, or a
  local clone farm = a new fetcher class; extraction, validation, and emission are untouched
  (swappable-seams, the same pattern BRACE uses for evidence).
- **Versioned contract:** every output carries `contractVersion` — consumers (the course, the
  playground, future viewers) can migrate deliberately instead of breaking silently.
- **Degradation order:** raw-README fallback → metadata-only graph (warned) → stale-kept
  (reported). Each step is louder, none is silent.
- **Ceiling:** the taxonomy (`KIND_RULES`, integration recipes) is curated vocabulary — it will
  need the same flywheel as jd-compiler's clusters: extend the tables as the field teaches new
  kinds. That's a feature (deterministic, reviewable) as long as the table stays small.

## How the three hub pillars consume this

- **Knowledge:** the per-repo graphs join the spine the same way jd/vault graphs do; knowledgefy's
  HTML viewer works on them unchanged.
- **Tooling:** `hub-skills.json` is the tooling **candidate registry** — each entry names *how* to
  consume the repo (discovery-source / plugin-dependency / workflow-organ / distribution-surface /
  course-citation) plus the honest edge that keeps adoption disciplined. Adoption stays
  human/eval-gated: the factory proposes, it never installs.
- **Experts:** `why_cited` + the integration recipes are the map a newcomer (or an agent) reads to
  know *why the hub trusts what it trusts* — the experts' judgment, serialized.

## Queued next (deliberately not rushed)

1. **GraphQL batch fetcher** when the registry passes ~30 repos (same seam, one query).
2. **Opt-in LLM enrich pass** for concept-to-concept semantic edges — additive layer, never
   load-bearing.
3. **Code-level deep dives** for the 2–3 repos where README depth isn't enough (fastmcp,
   langfuse) via `understand-anything` on a pinned clone.
4. ~~Weekly `refresh` cron in CI~~ — **shipped** (`freshness.yml → hub-drift`: weekly refresh →
   rebuild → bot PR; drift is a trigger, not a failure).
