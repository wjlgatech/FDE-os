# Case study — Google Cloud FDE technical loop (2026-07-07): the prep doc + what FDE-os could and couldn't do

> **Why this is in FDE-os:** a real interview loop is the highest-grade ground truth Objective 1 has —
> *given a JD, does this system train the person well enough to land that job?* This case study preserves
> the actual prep instruction used for a real Google Cloud FDE onsite (coding + system design, Senior,
> Mountain View/Sunnyvale) **and** the honest audit of which parts FDE-os covered and which it didn't.
> Comp figures are redacted per the repo's born-clean rule (this is a public repo).

## The FDE-os coverage audit (evidence first)

Compiled from the real JD ([`course/target-jds/google-cloud-fde.md`](../target-jds/google-cloud-fde.md)
via `jd-compiler`: **6 of 7 competency clusters demanded**) and the recruiter's explicit grading signals
in the doc below:

| Graded interview area | FDE-os artifact | Verdict |
|---|---|---|
| Discovery & stakeholder alignment (~25% of the design grade) | [`invisible-workflow-mapper`](../../skills/invisible-workflow-mapper/) (12 tests) + the Delta Discovery Protocol field kit — the §6 Phase-1 question groups are its dimensions | ✅ covered |
| Monitoring — catch hallucinations / off-brand (explicitly graded) | [`rag-eval-harness`](../../skills/rag-eval-harness/) (groundedness proxy, citation coverage, gate) + `criteria-scorer` + `eval-loop` — §6(e) is this toolkit, verbatim | ✅ covered |
| Sensitive data / PII / isolation | The born-clean security convention (AGENTS.md), the regulated-signoff archetype, field-note lesson #3 (HITL mandatory) — §6(c)'s one-liner is the pharma field note's thesis | ✅ covered (pattern level; GCP service names — DLP, VPC-SC, CMEK — live only in this doc) |
| "Structure > models" talking point | [`doc-understanding`](../../skills/doc-understanding/) — parse-quality gate; *Output Quality ≤ Input Representation Quality* | ✅ covered |
| JD-grounded prioritization | [`jd-compiler`](../../skills/jd-compiler/) + the knowledge spine (41 concepts) | ✅ covered |
| **Hand-coding under zero assist (the #1 named risk)** | **Nothing.** `grep -ril "leetcode\|sliding window\|topological\|LRU\|BFS\|union-find\|rate limiter"` across the repo → **0 hits** before this file | ⚠️ **harness shipped, muscle is yours** — [`coding-drill-kit`](tools/coding-drill-kit/) gates blank-page template recall (6/6 twice = ready); the daily reps are still human work |
| GCP reference-architecture fluency (Vertex, Cloud Run, Pub/Sub…) | Thin — the toolkit is deliberately provider-agnostic | ⚠️ partial |

**The honest verdict:** FDE-os is **sufficient for the system-design hour** (its eval/discovery/PII
artifacts map 1:1 onto the graded areas) and **insufficient for the coding hour** — drilling
no-autocomplete hand-coding is a human-muscle problem the toolkit doesn't (and shouldn't pretend to)
solve. What FDE-os *did* contribute to the coding hour is the discipline: templates-as-artifacts,
a tracker, and gates — the same eval-loop shape, applied to a person instead of a codebase.

---

# Google Cloud FDE — Technical Loop Prep (Coding + System Design)

**Candidate:** Paul Jialiang Wu, PhD
**Interview date:** Tuesday, 2026-07-07
**Prep window:** 7 work days (authored Sat 2026-06-27; dates below are as-written)
**Loop:** (1) Coding — 60 min · (2) System Design / Role-Related Knowledge — 60 min
**Level / location:** Senior, Mountain View / Sunnyvale
**Comp benchmark (pre-negotiation):** *[redacted — born-clean rule; kept in the private tracker]*

> This is your single source of truth. You flagged weak recall — don't re-derive any of this under pressure. Read it, drill it, trust it. The plan at the bottom tells you exactly what to do each day.

---

## 0. The 30-second framing — what these two rooms actually test

Two different muscles, graded differently:

- **Coding room = "can you write clean, correct Python by hand, out loud, with zero assist?"** It is NOT about exotic algorithms. It's about *craft under a stripped-down environment.* The platform has **syntax highlighting only** — no autocomplete, no linting, no AI. That constraint IS the test. The person who practiced hand-coding wins; the person who leaned on Copilot fumbles `collections.defaultdict` and dies by a thousand typos.
- **System Design room = "can you turn a vague business problem into a scalable, secure, production-ready AI system — and talk a customer through it?"** This is your home turf. Co-founder + Physical-AI-in-production is exactly this job. Don't coast on it; *structure* it.

**Two-builder note (your operating system):** you told the recruiter "I just have fun preparing and building at the same time." Good — lean into it. The prep plan below has you *build* a no-AI mock harness and a problem tracker. Building the prep system fixes your recall problem AND rehearses the skill. Cross-pollination, on purpose.

---

## 1. KEY POINTS — documented from the recruiter call (don't lose this signal)

### Coding interview (60 min)
- **Language:** Python (your primary).
- **Shape:** primarily **ONE question, multiple parts + follow-ups** — not 2–3 separate problems. They go *deep* on one thing.
- **Platform:** virtual, **syntax highlighting ONLY**. No code correction, no autocomplete, no suggestions. **No AI, no external tools, no code assistance. Old-school hands-on.**
- **Difficulty:** LeetCode-style, **medium-to-hard**.
- **Graded explicitly on:** readable variable names · sensible function composition · appropriate control structures & data structures. (i.e., production-quality code, not just "passes tests.")
- **Topics to focus:** **strings, graphs, site reliability engineering (SRE), distributed systems.**
- **NOT expected:** identifying exact complexity orders (**ballpark Big-O is enough**), and **no dynamic programming.**
- **Wildcard:** **distributed computing/systems may appear in the coding round.** Recruiter said this is unusual and couldn't give an example — told you to research it and email if still unclear. (Examples + email draft in §5.)

### System Design interview (60 min, 1:1 with an FDE)
- **Format:** single scenario → a few high-level questions → you design, build, deploy a solution.
- **The core test:** take a **vague business problem → scalable, secure, production-ready AI solution.**
- **Time budget:** ~**15 min discovery + stakeholder alignment**, then ~**30 min system design + architecture** (≈15 min buffer for follow-ups/wrap).
- **They will probe:**
  - **Model selection, prompting, vs. fine-tuning** — when and why each.
  - **Sensitive data** — the prompt *will* mention it. Be explicit about **PII protection and data isolation.**
  - **Scale** — starts at **10,000 users → millions.** Show the architecture holds under load.
  - **Monitoring** — how do you **catch hallucinations and off-brand content?**
- **No AI / external tools here either.**

### Universal tips the recruiter gave (these are graded behaviors)
1. **Pause on purpose.** "Let me take 30–60 seconds to gather my thoughts." Say it out loud. Don't rush in.
2. **Ask thoughtful, probing, clarifying questions first** — *even if you think you fully understand.* "When a customer gives you a problem, you don't jump in." This is literally the FDE muscle being tested.
3. **Think out loud. Bring the interviewer along.** Both rooms are designed to see *how you think and brainstorm*, not just the final answer.

---

## 2. Your edge & your risks — honest diagnosis (read this twice)

**Your edge (lean in):**
- **System design is your turf.** Production AI, sensitive data, scaling, monitoring, model-vs-RAG-vs-fine-tune — you've shipped this. Your Accenture pharma-compliance story (deterministic guardrail above a non-deterministic LLM) is a *perfect* PII/reliability anchor.
- **The clarifying-questions / stakeholder-alignment phase is your co-founder reflex.** Most engineers rush it. You won't — *if* you remember to slow down.
- **You translate eng ↔ business losslessly.** That's the entire FDE grade.

**Your risks (defend against):**
1. **#1 RISK — raw hand-coding atrophy.** You build AI loops for a living; you've been heavily AI-assisted. A no-autocomplete editor is your single biggest threat. You will fumble idioms you "know" (`deque`, `defaultdict`, `heapq`, lambda keys, `enumerate`) because muscle memory ≠ recognition memory. **Fix: hand-write code daily, no assist, starting Day 1.** This is non-negotiable and front-loaded in the plan.
2. **Recall under pressure.** You externalize for a reason. You can't bring notes into the room — so the fix is *over-rehearsal of a small number of templates* (§4) until they're reflex, not recall.
3. **Survey-mode / over-talking.** You know a lot; you'll be tempted to dump. Both rooms reward *structured* thinking-aloud, not volume. Answer the sub-question, narrate the plan, move. The think-aloud has a script (§3, §6) — follow it so "thinking out loud" doesn't become "rambling."
4. **Distributed-systems wildcard.** You flagged it. Neutralized in §5.

---

## 3. CODING ROUND — how to run the hour

### The 6-step loop (say each step out loud)
1. **Restate + clarify (60–90s).** Repeat the problem in your words. Ask 2–3 sharp questions: input size? value ranges? empty/null? duplicates? sorted? Unicode vs ASCII for strings? memory limit? "Can the graph have cycles / be disconnected?" *This is graded — it's the FDE clarifying muscle in miniature.*
2. **State the approach BEFORE coding (60s).** "Brute force is X, O(n²). I can do better with a hash map → O(n). I'll code the O(n)." Get a nod. **Brute-force-then-optimize out loud is the Google-sanctioned move.**
3. **Name your data structures + signature.** "I'll use a `deque` for the BFS frontier and a `visited` set." Write the function signature with a clear name.
4. **Code in small, composable functions** with readable names. They grade *function composition* — don't write one 40-line blob. A helper named `is_valid(r, c)` beats an inline boolean swamp.
5. **Narrate as you type.** Especially because there's no autocomplete: say "I'm importing deque from collections" as you write it — it keeps you and the interviewer synced and slows your own errors.
6. **Dry-run on a small input + edge cases, out loud.** Walk the code line-by-line on one example. Then name edges: empty, single element, all-same, cycle, no path. Fix in place. **Ballpark the complexity** ("this is linear-ish, O(V+E)") — exact orders not required.

### What they're grading (the rubric, literally)
- ✅ **Readable variable names** — `neighbors`, `in_degree`, `window_start`; never `x`, `tmp`, `d2`.
- ✅ **Sensible function composition** — small helpers, single responsibility.
- ✅ **Appropriate control + data structures** — the *right* tool (set for membership, deque for queue, heap for top-k, dict for counts), not a forced one.
- ✅ **Correctness via hand dry-run** (no "run" button to lean on).
- ⚠️ Big-O: **ballpark only.** Don't burn time on tight proofs.
- ❌ Don't expect/force DP. If your instinct screams DP, there's almost certainly an intended greedy/graph/hashing solution — re-read the prompt.

### Topic map — what "medium-to-hard" looks like in their 4 buckets
- **Strings:** sliding window (longest substring w/o repeat, min window), two-pointer, anagram/frequency maps, parsing/tokenizing, encode/decode, edit-distance-*lite* (but not full DP tables). *Parsing & validation* show up a lot in FDE-land (think log lines, config, structured text).
- **Graphs:** BFS/DFS on grids and adjacency lists, connected components, shortest path (unweighted = BFS; weighted = Dijkstra with a heap), **topological sort (dependency resolution)**, cycle detection, union-find. Graphs are the highest-probability bucket for a multi-part question (Part A: build graph; Part B: traverse; Part C: add a constraint).
- **SRE-flavored:** **LRU cache**, rate counters over a time window, merge intervals (maintenance windows), parse & aggregate logs, retry/backoff logic, dedup a stream, top-K errors (heap), interval scheduling. These read like real ops problems wearing an algorithm costume.
- **Distributed-systems-flavored:** see §5.

### The no-AI environment protocol (drill this into reflex)
- **Practice in a bare editor** — Google Docs, Notepad, or LeetCode with autocomplete/Copilot OFF. No running until you've dry-run by hand. This is the closest match to their platform.
- **Memorize these idioms cold** (you WILL need them, no autocomplete to save you):
  ```python
  from collections import deque, defaultdict, Counter
  import heapq
  q = deque([start]); q.append(x); q.popleft()
  adj = defaultdict(list); adj[u].append(v)
  cnt = Counter(s)                      # frequency map in one line
  heapq.heappush(h, (dist, node)); heapq.heappop(h)
  for i, ch in enumerate(s): ...
  seen = set(); seen.add(x); x in seen
  arr.sort(key=lambda p: (p[1], -p[0])) # multi-key sort
  ```
- **Write the boilerplate from memory 10×** before Day 7 so your fingers produce it without thought.

---

## 4. Templates to memorize (your "muscle memory" set — keep these tiny and reflexive)

> Goal: you can reproduce each from a blank page in <2 min, narrating. These 5 cover ~80% of strings+graphs+SRE.

**BFS on a grid**
```python
from collections import deque

def bfs(grid, start):
    rows, cols = len(grid), len(grid[0])
    q = deque([start])
    visited = {start}
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append((nr, nc))
    return visited
```

**Topological sort (Kahn) — dependency/order resolution, very FDE**
```python
from collections import deque, defaultdict

def topo_sort(num_nodes, edges):          # edges: (u -> v) means u before v
    adj = defaultdict(list)
    in_degree = [0] * num_nodes
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
    q = deque(n for n in range(num_nodes) if in_degree[n] == 0)
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in adj[node]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                q.append(nxt)
    return order if len(order) == num_nodes else []   # [] = cycle
```

**Sliding window (longest substring without repeats)**
```python
def longest_unique(s):
    seen = {}
    window_start = best = 0
    for i, ch in enumerate(s):
        if ch in seen and seen[ch] >= window_start:
            window_start = seen[ch] + 1
        seen[ch] = i
        best = max(best, i - window_start + 1)
    return best
```

**Union-Find (connected components / dedup grouping)**
```python
def find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]   # path compression
        x = parent[x]
    return x

def union(parent, a, b):
    parent[find(parent, a)] = find(parent, b)
```

**LRU cache (the classic SRE-flavored one)**
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.store = OrderedDict()
    def get(self, key):
        if key not in self.store:
            return -1
        self.store.move_to_end(key)
        return self.store[key]
    def put(self, key, value):
        if key in self.store:
            self.store.move_to_end(key)
        self.store[key] = value
        if len(self.store) > self.cap:
            self.store.popitem(last=False)
```

---

## 5. The distributed-systems wildcard — neutralized

The recruiter couldn't give an example, so here's what "distributed systems in a *coding* round" actually means: **not** "design Spanner." It means a **single-machine coding problem that models a distributed concern** — usually concurrency, sharding, rate-limiting, deduplication, or ordering. High-probability forms:

1. **Token-bucket / sliding-window rate limiter** (per-user). Classic. Template below.
2. **Consistent hashing ring** — map keys to N nodes, add/remove a node with minimal remapping. (Hash ring + `bisect`.)
3. **Producer/consumer with a bounded queue** — thread-safe, using `queue.Queue` or a lock + condition.
4. **Deduplicate a stream / exactly-once** — seen-set or a time-windowed set.
5. **Merge K sorted streams** (like merging logs from K servers by timestamp) — heap.
6. **Design a thread-safe counter / KV store** with get/put and maybe TTL expiry.

**Token-bucket rate limiter (memorize this one):**
```python
import time

class RateLimiter:
    """Allow `rate` requests per `per` seconds, per key."""
    def __init__(self, rate, per):
        self.rate = rate
        self.per = per
        self.allowance = {}   # key -> (tokens, last_check)

    def allow(self, key, now=None):
        now = now if now is not None else time.time()
        tokens, last = self.allowance.get(key, (self.rate, now))
        tokens = min(self.rate, tokens + (now - last) * (self.rate / self.per))
        if tokens < 1:
            self.allowance[key] = (tokens, now)
            return False
        self.allowance[key] = (tokens - 1, now)
        return True
```

**How to talk about it (the systems-thinking layer they want):** after coding the single-node version, say the upgrade out loud — *"In a real distributed setting this counter can't live in one process; I'd move state to Redis keyed by user, use consistent hashing so each user maps to one shard, and watch for the race where requests fan out across servers and bypass a local counter — that's the classic globally-inconsistent rate-limiter bug."* That one sentence converts a coding answer into an FDE answer.

**Email to send the recruiter (you said you would):**
> Subject: Quick follow-up — distributed systems in the coding round
>
> Hi [Recruiter] — thanks again for the thorough walkthrough. I did some prep on the distributed-systems angle for the coding interview. My read is it means single-machine problems that model a distributed concern — e.g., a per-user rate limiter, consistent hashing, producer/consumer with a bounded queue, or merging K sorted log streams — rather than full distributed-systems design (that lives in the system design round). Does that match what your interviewers have in mind, or should I weight it differently? Want to make sure I focus the right way. Thanks!

Sending this does two things: gets you a real signal, and shows initiative/communication (an FDE trait). Send it Monday 6/29.

---

## 6. SYSTEM DESIGN ROUND — your repeatable framework

You will get a vague business prompt mentioning sensitive data, 10K→millions of users, and a need to catch bad model output. Run this **same skeleton every time** so you never freeze. Narrate the headers as you go.

### Phase 1 — Discovery & stakeholder alignment (~15 min). DO NOT SKIP. DO NOT RUSH.
Open with the recruiter's gift: *"Before I design anything, I want to take a minute and make sure I understand the problem and who it's for."* Then ask, grouped:
- **Users & job-to-be-done:** Who are the users? What's the one outcome that makes this a success? What do they do today without it?
- **Data:** What data do we have, where does it live, how clean/fresh is it? **What sensitive data / PII is in scope, and what compliance regime (HIPAA, GDPR, SOC2)?** Is data multi-tenant?
- **Constraints:** Latency budget? Accuracy bar / cost of a wrong answer? Cost ceiling? Existing stack / legacy systems to integrate?
- **Scale & growth:** Confirm the 10K→millions trajectory and over what timeline. Read-heavy or write-heavy?
- **Success metric & guardrails:** How will *they* measure it? What's "off-brand" or unacceptable output for them?

Then **state your assumptions out loud and get a nod** before designing. This phase alone is ~25% of the grade.

### Phase 2 — Architecture (~30 min). Walk the data, then the layers.
Sketch the happy path end to end, then layer in scale → security → monitoring.

**(a) Core AI approach — model selection / prompt / RAG / fine-tune.** State the decision tree explicitly:
- **Prompting first** — cheapest, fastest to iterate.
- **RAG** — when the answer needs **fresh or proprietary/customer knowledge** (most enterprise cases). Components: ingestion → chunking → embeddings → vector store → retrieval → **re-ranking** → grounded generation with citations.
- **Fine-tuning** — when you need **behavior/format/domain-style** consistency that prompting can't hold, and you have labeled data. More cost, more ops.
- **Model choice:** start with a strong managed model (Gemini on **Vertex AI**); justify by latency/cost/quality; keep the model behind an interface so you can swap it (Strategy pattern — your existing "single provider seam").

**(b) Reference architecture (say the GCP names):**
`Client → API Gateway / Load Balancer → stateless app tier (Cloud Run / GKE) → orchestration/agent layer → [retrieval: Vertex Vector Search/AlloyDB pgvector] + [Gemini on Vertex AI] → response with guardrails → cache → return.` Async/batch work on Pub/Sub + workers. Data in Cloud Storage / BigQuery. Secrets in Secret Manager.

**(c) Sensitive data — PII & isolation (they WILL push here; this is your Accenture story's home):**
- **Minimize & detect:** run **Cloud DLP** to detect/redact/tokenize PII before it hits the model or logs. Never log raw prompts containing PII.
- **Isolation:** **per-tenant data separation** — separate vector namespaces/indexes per customer, row-level access controls, **VPC Service Controls** to box the data perimeter, **CMEK** for customer-managed keys. Retrieval must be tenant-scoped so customer A can never retrieve customer B's docs (the #1 RAG leak).
- **Access:** least-privilege IAM, short-lived service-account tokens, audit logging on every data access.
- **At rest / in transit:** encryption by default; private endpoints; no PII in third-party calls.
- **Your one-liner:** *"audit-grade systems can't route trust through a non-deterministic layer — I put deterministic guardrails and access control around the model, not inside it."* (Straight from your pharma deployment.)

**(d) Scale 10K → millions (show it holds):**
- **Stateless app tier** → horizontal autoscaling. State in managed stores, not in the process.
- **Caching** — semantic/response cache for repeated queries (huge cost + latency win at LLM scale); embedding cache.
- **Async** everything non-interactive (ingestion, re-embedding) via queues.
- **Vector store sharding** + read replicas as corpus and QPS grow.
- **Cost control at scale** — this is the LLM-specific trap: cost scales with tokens × requests. Lever: cache, smaller/distilled models for easy queries (routing), batching, token budgets, **cost-per-request as a first-class metric**.
- **Rate limiting / quotas** per tenant (your §5 token bucket, distributed via Redis).
- **Graceful degradation** — fallback model or cached answer if the primary is overloaded.

**(e) Monitoring — catch hallucinations & off-brand content (don't forget this; it's explicitly graded):**
- **Offline eval harness** — golden dataset, run on every prompt/model change; track quality regression. (Your independent-referee / maker≠checker pattern.)
- **Groundedness / hallucination checks** — require citations; score answer-vs-retrieved-context overlap; flag/withhold low-groundedness answers. LLM-as-judge for a sampled %.
- **Off-brand / safety** — a classifier or policy model on outputs; block-list + tone check; human review queue for flagged content.
- **Online telemetry** — tracing per request (latency, tokens, cost, retrieval hits), p95s, thumbs-up/down feedback loop, drift dashboards.
- **Human-in-the-loop before any irreversible/customer-visible action.** Always name this.

### Worked example (rehearse this one end-to-end)
**Prompt:** *"A bank wants an AI assistant that answers customer questions over their account history and policy docs."*
→ Discovery: who (support agents vs. end customers?), PII = account data (GLBA/PCI), latency < 2s, must never invent account facts. → RAG over policy docs + **tool-call** (not RAG) for live account data via a permissioned API. → Gemini on Vertex; DLP redaction; per-customer retrieval scoping; VPC-SC perimeter. → Scale via stateless Cloud Run + semantic cache + sharded vector index; route trivial FAQs to a cheap model. → Monitor groundedness (must cite policy), hallucination guard on any numeric account claim (force tool-call, never generate numbers), off-brand classifier, human handoff on low confidence. Land it: *"the model never states an account fact it didn't retrieve from the system of record — that's the deterministic boundary."*

---

## 7. THE 7-WORK-DAY PLAN (dated, ~2–3 hrs/day)

> Front-loaded on hand-coding (your #1 risk). Each day: warm-up coding by hand, then a focused block. Track every problem in your tracker (build it Day 1).

**Day 1 — Mon 6/29 · Setup + hand-coding baseline**
- Build your **no-AI mock harness**: a bare editor setup (autocomplete OFF) + a `problems.md` tracker (problem, bucket, time, what broke). This is your build-while-prep artifact. *(Shipped as [`tools/coding-drill-kit/`](tools/coding-drill-kit/) — `drill.py start` → write from memory → `drill.py check`.)*
- Hand-write all 5 templates in §4 from memory, twice. Note what you fumbled.
- 2 LeetCode **medium graphs** (e.g., Number of Islands, Course Schedule) — by hand, narrate aloud, dry-run before running.
- **Send the recruiter email (§5).**

**Day 2 — Tue 6/30 · Strings + the think-aloud loop**
- Warm-up: re-write the BFS + sliding-window templates cold.
- 3 string problems: longest substring w/o repeat, min window substring, valid anagram / group anagrams. Hand-coded, narrated using the §3 6-step loop.
- Record yourself on ONE problem. Watch for: did you clarify first? did you ramble? did you dry-run?

**Day 3 — Wed 7/1 · Graphs deep (highest-probability bucket)**
- Warm-up: topo-sort template cold.
- 4 graph problems incl. one **multi-part** (clone graph; course schedule I→II; word ladder; number of connected components). Practice "Part A build, Part B traverse, Part C add constraint" — narrate the seams.
- Drill: convert each into clean helper functions (graded on composition).

**Day 4 — Thu 7/2 · SRE + distributed-systems coding**
- Warm-up: LRU template cold.
- Code by hand: token-bucket rate limiter, merge K sorted lists (log merge framing), LRU, dedup a stream, consistent-hashing sketch.
- For each, say the "now make it distributed" upgrade sentence (§5).

**Day 5 — Fri 7/3 (holiday — lighter, ~90 min) · System design framework**
- Read §6 until the skeleton is reflex. Write the 5 discovery question-groups + the 5 architecture layers from memory.
- Do the **worked example** (bank assistant) out loud, start to finish, timed to ~25 min.

**Day 6 — Mon 7/6 · Full mock day**
- **Mock 1 (coding, 45 min):** pick an unseen medium-hard graph or string problem, simulate the full room — clarify, narrate, hand-code, dry-run, ballpark Big-O. No AI, no autocomplete.
- **Mock 2 (system design, 45 min):** new prompt (e.g., "summarize millions of support tickets with sensitive data"). Run the §6 framework on the clock. Hit PII, scale, monitoring.
- Debrief each into your tracker: what wobbled? One fix each.

**Day 7 — Tue 7/7 · Interview day · light touch only**
- Morning: re-write the 5 templates cold one last time (15 min). Re-read §1, §3 6-step loop, §6 skeleton. **Do not learn anything new.**
- Warm your voice: say your "tell me about yourself" and one clarifying-question set out loud.
- Logistics: quiet room, stable internet, water, the §6 skeleton on a sticky note *in your head* (not on screen).

---

## 8. Day-of run-of-show (both rooms)

1. **First 60–90 seconds, every problem:** "Let me take a minute to make sure I understand and ask a couple of questions." → clarify → restate. (Graded behavior. Do it even when obvious.)
2. **Think out loud the whole time.** Silence reads as stuck. Narrate the plan, then execute.
3. **Coding:** approach → data structures → small functions → narrate typing → dry-run + edges → ballpark O. Readable names always.
4. **System design:** discovery first (15m, slow down), then layers: AI approach → architecture → PII/isolation → scale → monitoring. Land every section on the business outcome.
5. **If you blank:** say "let me start with the brute-force / simplest version and improve it" — sanctioned and resets you.
6. **Watch your tells:** no Azure-isms (say Vertex/GCP); punchline first; don't survey-dump; warmth in your voice.

---

## 9. Comp note (for awareness, not for these rooms)
*[Redacted for the public repo — born-clean rule. The benchmark and negotiation plan live in the private tracker.]* Don't negotiate now — nail the loop first; leverage comes after a strong panel.

---

## 10. Sources
- [Google SWE candidate prep — official (JS-rendered; tenets cross-checked below)](https://www.google.com/about/careers/applications/candidate-prep/swe)
- [Google coding interview prep guide — Educative](https://www.educative.io/blog/google-coding-interview)
- [Google Interview Prep Guide (SWE) — PDF mirror](https://soft-eng-practicum.github.io/assets/pdfs/Google%20Interview%20Prep%20Guide%20SWE%20.pdf)
- [Google FDE Interview Guide — Exponent](https://www.tryexponent.com/guides/google-forward-deployed-engineer-interview)
- [FDE interview: not just LeetCode — Medium (Jun 2026)](https://medium.com/@trivajay259/the-google-forward-deployed-engineer-interview-is-not-just-leetcode-heres-what-they-actually-384ebf2c0bb9)
- [google-fde-interview-guide — GitHub](https://github.com/YagyanshB/google-fde-interview-guide)
- [Design a Distributed Rate Limiter — Hello Interview](https://www.hellointerview.com/learn/system-design/problem-breakdowns/distributed-rate-limiter)
- [Consistent Hashing — GeeksforGeeks](https://www.geeksforgeeks.org/system-design/consistent-hashing/)
- [Google SRE interview — IGotAnOffer](https://igotanoffer.com/blogs/tech/google-site-reliability-engineer-interview)
