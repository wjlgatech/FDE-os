/* Single source of truth for the /FDE-os master-tool brief (window.BRIEF_DATA) and the
   /api/chat corpus. Generated 2026-07-21. Every terminal output below is REAL — captured
   from actual runs at the repo root, and the same commands are re-executed by CI on every
   push (skills/fde-os/tests/test_master_examples.py): if a demo rots, the build goes red. */
const BRIEF_DATA = {
  stats: { skills: 13, tests: 208, demos: 14 },

  repo: "https://github.com/wjlgatech/FDE-os",

  install: [
    { title: "Claude Code plugin", text: "/plugin marketplace add wjlgatech/FDE-os — the repo root IS the plugin; 13 skills auto-discover, the MCP server wires via plugin.json." },
    { title: "Codex", text: ".codex-plugin/plugin.json points at the same skills/ tree — one source, two runtimes; CI keeps the manifests in lockstep." },
    { title: "Any agent with a shell", text: "git clone github.com/wjlgatech/FDE-os && make check — one finish line for humans, CI, and agents alike (208 tests, offline, stdlib-only)." },
    { title: "Any MCP client", text: "python3 skills/fde-mcp-server/scripts/server.py — stdio JSON-RPC; 8 tools including true_score, rag_eval, hub_find." },
  ],

  engines: [
    ["fde-os (master)", "the front door — routes any ask to the right engine; its own demos are CI-tested"],
    ["true-scorer", "TRUE rubric ship gate (Teach/Reproduce/Understand/Engage) — exit 1 on BLOCK"],
    ["criteria-scorer", "your rubric as data → binary gate"],
    ["rag-eval-harness", "precision/recall/MRR + grounding + citation coverage, gated"],
    ["outcome-contract", "engagement GO/NO-GO on measured outcomes — claimed never passes"],
    ["knowledgefy", "prose vault → provenance-pinned knowledge graph + HTML"],
    ["jd-compiler", "job description → competency clusters + prep plan"],
    ["repo-compiler + hub", "top-rated cited repos compiled into knowledge + integration recipes"],
    ["doc-understanding", "DOCX/XLSX/MD → gated canonical JSON; refuses PDFs honestly"],
    ["eval-loop", "edit → score → keep-if-strictly-better / revert; git is the memory"],
    ["invisible-workflow-mapper", "reconstruct an org's decision workflow from signals"],
    ["field-kit-generator", "posts → forkable field kits, convention-linted"],
    ["fde-mcp-server", "everything above as MCP tools over stdio"],
  ],

  features: [
    {
      title: "Ship gates — score before you ship",
      intro: "The founding move: content, code, or claims pass a deterministic gate or they don't ship. A BLOCK is a working feature.",
      examples: [
        { cmd: "python3 skills/true-scorer/scripts/score.py docs/marketing/context-starved-short-post.md",
          out: "  T = 3  (named-model=True, diagram/quote=True)\n  R = 0  (kit-linked=False, run-instructions=False)\n  U = 2  (jargon-density=0.0000, concrete-open=False)\n  E = 1  (try-this=False)\n  total = 6 / 12\nVERDICT: BLOCK — total 6 < 10; R=0 < 2; E=1 < 2   → exit 1",
          note: "A real draft from this repo failing its own gate — the tool blocks its own author's marketing." },
        { cmd: "python3 skills/true-scorer/scripts/score.py --scores T=3,R=2,U=3,E=2",
          out: "  total = 10 / 12\nVERDICT: PASS — clears the ship gate (>=10 and every letter >=2).   → exit 0",
          note: "Scores mode for when a human already judged the letters." },
        { cmd: "python3 skills/criteria-scorer/scripts/criteria_score.py score docs/marketing/context-starved-short-post.md docs/marketing/viral-post-criteria.json",
          out: "criteria score: 0.75 (3/4 passed)\n  [PASS] Leads with / contains a concrete number?\n  [PASS] Closes with a real question?\n  [FAIL] Under the ~230-word feed sweet spot?\n  [PASS] Free of 2026-suppressed engagement-bait?\nVERDICT: BLOCK   → exit 1",
          note: "Rubric-as-data: swap the JSON, same engine gates anything." },
      ],
    },
    {
      title: "Evals — retrieval, grounding, outcomes",
      intro: "Two layers the JD-world calls 'evaluation': does retrieval work, and did the engagement actually deliver? Both are gates, not dashboards.",
      examples: [
        { cmd: "python3 skills/rag-eval-harness/scripts/rag_eval.py score skills/rag-eval-harness/examples/pharmacy-rag-eval.json --k 5",
          out: "RAG eval — 2 items, k=5:\n  precision@k        0.5\n  recall@k           1.0\n  mrr                1.0\n  hit_rate@k         1.0\n  grounding          1.0\n  citation_coverage  1.0   → exit 0",
          note: "Grounding is a lexical-overlap proxy — stated in the skill's own notGoodAt, not hidden." },
        { cmd: "python3 skills/outcome-contract/scripts/outcome_score.py score skills/outcome-contract/examples/acme-receptionist.json",
          out: "outcome-contract: acme-hotel-ai-receptionist — verdict: GO\n  [✓ PASS] (blocking) call-answer-rate: measured 72.5 vs target >= 60\n  [✓ PASS] (blocking) median-wait-seconds: measured 12 vs target <= 30\n  [~ CLAIMED] (advisory) guest-satisfaction: claimed, not independently sourced — reported but never counts as a pass\n  totals: 2 pass · 0 fail · 1 claimed · 0 not measured\nVERDICT: GO   → exit 0",
          note: "Claimed ≠ measured: a stakeholder's assertion is reported but can never flip a verdict." },
      ],
    },
    {
      title: "Knowledge compilers — prose and JDs become structures",
      intro: "Notes become provenance-pinned graphs; job descriptions become competency maps. Both deterministic, both offline.",
      examples: [
        { cmd: "python3 skills/knowledgefy/scripts/knowledgefy.py build knowledge/vault/snowflake-summit-2026 --out /tmp/graph",
          out: "spine: /tmp/graph — 16 concepts, 17 evidence, 32 edges   → exit 0",
          note: "Concept nodes from headings, evidence nodes from citations — no citation, no evidence node." },
        { cmd: "python3 skills/jd-compiler/scripts/jd_compile.py compile course/target-jds/agentic-ai-engineer-senior-consultant.md",
          out: "- **languages**: python.\n- **agent frameworks**: langchain, langgraph.\n- **vector dbs**: milvus, pinecone, weaviate.\n- **eval obs**: evaluation, observability, tracing.\n- **patterns**: multi-agent, orchestrat.   → exit 0",
          note: "The exact JD this repo later answered with a built take-home — compiled first, built second." },
      ],
    },
    {
      title: "The hub — external tooling on trigger, never in context",
      intro: "Seven top-rated cited repos compiled into knowledge graphs + integration recipes. An agent queries on need instead of carrying seven repos of context.",
      examples: [
        { cmd: "python3 skills/repo-compiler/scripts/hub_query.py find observability evals",
          out: "langfuse/langfuse (⭐31426, platform, match 1.0)\n  integrate as: workflow-organ — wire as a swappable organ behind an interface — never hard-couple\n  not good at: zero-ops adoption — a deployable platform carries real operational cost\n  source: github.com/langfuse/langfuse @ 1cb1bbcf   → exit 0",
          note: "Every entry carries an honest notGoodAt edge and a SHA-pinned source." },
        { cmd: "python3 skills/repo-compiler/scripts/hub_query.py recipe fastmcp",
          out: "PrefectHQ/fastmcp (⭐26292, framework)\n  integrate as: plugin-dependency — build-time dependency (pin the version; probe actual behavior with one small build before adopting)\n  not good at: being a finished app — you still own design, evals, and deployment   → exit 0",
          note: "A recipe, not a bookmark: how to integrate, what it won't do." },
        { cmd: "python3 skills/repo-compiler/scripts/hub_query.py find quantum knitting",
          out: "no match in the hub registry.\n  kinds available: curated-index, framework, learning-resource, platform, registry, tool\n  repos compiled: awesome-mcp-servers, servers, ai-engineering-from-scratch, langfuse, fastmcp, registry, mlrun\n  (add the repo to knowledge/hub/repos.yml and run repo_compile.py all)   → exit 2",
          note: "Zero matches never fail silent — the diagnostic names the vocabulary, and exit 2 makes it gateable." },
      ],
    },
    {
      title: "The reference runtime — an agent with receipts",
      intro: "A complete agent (durable graph, gated tools, hybrid retrieval with verifiable citations, session memory, guardrails) that grades itself against labeled ground truth.",
      examples: [
        { cmd: "python3 take-home/deloitte-agentic-triage/scripts/run.py --out runs/latest",
          out: "R-001  approve\nR-002  escalate spend-committee   → gate: spend-committee\nR-003  deny\nR-004  escalate cto\n…\nR-012  escalate vendor-onboarding\nwrote decisions.json, traces.jsonl, checkpoints/   → exit 0",
          note: "12 requests through checkpointed nodes; escalations pause at the human gate — the pause is the answer." },
        { cmd: "python3 take-home/deloitte-agentic-triage/scripts/eval.py --run-dir runs/latest",
          out: "{\n  \"decision_accuracy\": 1.0,\n  \"escalation_recall\": 1.0,\n  \"citation_doc_coverage\": 1.0,\n  \"citation_validity\": 1.0,\n  \"trace_completeness\": 1.0\n}\nVERDICT: PASS   → exit 0",
          note: "Escalation recall is gated at exactly 1.0 — one missed escalation fails the build." },
      ],
    },
    {
      title: "Composition + MCP — gates chain, tools surface",
      intro: "Workflows AND gates together instead of re-implementing them; the MCP server exposes the whole toolkit to any client.",
      examples: [
        { cmd: "python3 workflows/engagement-readiness/run.py workflows/engagement-readiness/examples/engagement.json",
          out: "…adoption-fit gate: PASS · correctness gate: PASS\n_Ship only when both stages pass: a great answer that doesn't fit the decision workflow never gets adopted; a well-adopted answer that doesn't work is worse._   → exit 0",
          note: "Composition rule: import skill cores, never re-implement their logic." },
        { cmd: "printf '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}' | python3 skills/fde-mcp-server/scripts/server.py",
          out: "tools: hub_find · true_score · rag_eval · criteria_score · eval_loop · invisible_workflow_map · jd_compile · doc_gate   → exit 0",
          note: "Hand-rolled stdio JSON-RPC, stdlib-only — no SDK dependency to rot." },
      ],
    },
  ],

  contract: [
    { k: "No evidence ⇒ No", v: "outcome-contract can't pass a claimed result; knowledgefy won't mint an evidence node without a citation; the triage reasoner escalates rather than guess when the governing clause wasn't retrieved." },
    { k: "Claimed ≠ measured", v: "A stakeholder's assertion is recorded and reported — and never counts toward a verdict. Only measured evidence with a source moves a gate." },
    { k: "Exit codes gate CI", v: "PASS/BLOCK, GO/NO-GO, drift, zero-match — every verdict is an exit code, so the same command a human runs is the command CI enforces. make check = 208 tests, offline, no keys." },
    { k: "Demos that can't rot", v: "Every fenced command in the master skill is parsed and re-executed by CI with its documented exit code asserted (skills/fde-os/tests/test_master_examples.py). This page's outputs are those runs." },
    { k: "Honest edges everywhere", v: "Each hub entry carries notGoodAt; each skill states what it refuses (doc-understanding refuses PDFs; grounding is a lexical proxy and says so). The tool's marketing is gated by the tool." },
  ],

  corpus: [
    "WHAT /FDE-os IS: the master tool over the FDE-os toolkit — one front door (skills/fde-os/SKILL.md) that routes any forward-deployed-engineering ask to the right engine. The repo is simultaneously a Claude Code plugin (marketplace add wjlgatech/FDE-os), a Codex plugin, a clonable toolkit gated by make check (208 offline stdlib tests), and an MCP server (8 tools over stdio JSON-RPC). 13 skills, 2 MCP servers, a compiled external-tooling hub, and a reference agent runtime.",
    "THE MASTER-TOOL ANSWER, HONESTLY: before 2026-07-21 there was no single /FDE-os entry point — the plugin exposed 12 skills individually. The master skill now exists as a thin router: all logic stays in the tested engines; the router only maps asks to engines. Its own demo examples are parsed out of the SKILL.md and re-executed by CI with documented exit codes asserted — a demo that rots turns the build red.",
    "THE 13 ENGINES: fde-os (master router), true-scorer (TRUE rubric ship gate), criteria-scorer (rubric-as-data gate), rag-eval-harness (retrieval + grounding metrics, gated), outcome-contract (GO/NO-GO on measured outcomes), knowledgefy (prose to provenance-pinned knowledge graph), jd-compiler (JD to competency map), repo-compiler + hub (external repos compiled into knowledge and integration recipes), doc-understanding (enterprise docs to gated canonical JSON, refuses PDFs), eval-loop (keep-if-strictly-better with revert, git as memory), invisible-workflow-mapper (org decision-workflow reconstruction), field-kit-generator (posts to forkable kits), fde-mcp-server (everything as MCP tools).",
    "SHIP GATES DEMO (real outputs): true-scorer scored this repo's own short post 6/12 — VERDICT BLOCK, exit 1 (R=0: no kit link, no run instructions; the tool blocks its own author's marketing). Scores-mode T=3,R=2,U=3,E=2 gives total 10/12 PASS exit 0. criteria-scorer against viral-post-criteria.json: 0.75 (3/4 passed), one FAIL (over the ~230-word feed sweet spot) makes the verdict BLOCK, exit 1. Rubric-as-data means you swap the JSON and the same engine gates anything.",
    "EVALS DEMO (real outputs): rag-eval-harness on the pharmacy example at k=5: precision 0.5, recall 1.0, MRR 1.0, hit-rate 1.0, grounding 1.0, citation coverage 1.0, exit 0. The grounding metric is a lexical-overlap proxy and the skill says so. outcome-contract on the acme-receptionist example: two blocking KRs measured and passed (call-answer-rate 72.5 vs >=60; median wait 12s vs <=30), one advisory KR claimed-only (guest satisfaction — reported, never counts), VERDICT GO, exit 0. Claimed never passes: that is the honesty core.",
    "KNOWLEDGE COMPILERS DEMO (real outputs): knowledgefy built the Snowflake Summit vault into a graph — 16 concepts, 17 evidence nodes, 32 edges, every evidence node provenance-pinned (no citation, no node). jd-compiler compiled the Deloitte-class agentic-AI JD into clusters: languages (python), agent frameworks (langchain, langgraph), vector DBs (milvus, pinecone, weaviate), eval-obs (evaluation, observability, tracing), patterns (multi-agent, orchestration). That same JD was later answered with the built take-home.",
    "HUB DEMO (real outputs): hub_query find 'observability evals' returns langfuse/langfuse (31.4k stars, platform, match 1.0) with integration guidance (wire as a swappable workflow-organ behind an interface, never hard-couple) and an honest notGoodAt (zero-ops adoption — a platform carries real operational cost), SHA-pinned @ 1cb1bbcf. recipe fastmcp returns the plugin-dependency recipe (pin the version, probe actual behavior with one small build). A zero-match query ('quantum knitting') never fails silent: it prints the available kinds and compiled repos and exits 2 so even 'not found' is CI-gateable. The hub refreshes itself weekly: a cron detects upstream SHA drift, rebuilds, and opens a bot PR.",
    "REFERENCE RUNTIME DEMO (real outputs): the triage agent runs 12 procurement requests through a durable graph (checkpoint per step, human-gate interrupts, retries, bounded self-correction) — 3 approvals, 1 deny, 7 escalations each routed to the right human, 1 invalid. Its eval grades against labeled ground truth: decision_accuracy 1.0, escalation_recall 1.0 (gated at exactly 1.0 — one missed escalation fails the build), citation_doc_coverage 1.0, citation_validity 1.0 (every cited quote exists verbatim in the policy corpus), trace_completeness 1.0. VERDICT PASS, exit 0. Presented in full at deloitte-triage-brief.vercel.app.",
    "COMPOSITION + MCP DEMO (real outputs): workflows/engagement-readiness AND-s two skill gates (adoption-fit AND correctness) into one GO/NO-GO — composition imports skill cores, never re-implements them. The MCP server exposes 8 tools over stdio JSON-RPC: hub_find, true_score, rag_eval, criteria_score, eval_loop, invisible_workflow_map, jd_compile, doc_gate — hand-rolled stdlib JSON-RPC, no SDK dependency to rot.",
    "THE CONTRACT (why trust it): no evidence means No; claimed is not measured; every verdict is an exit code so the command a human runs is the command CI enforces; every fenced demo in the master skill is re-executed by CI with its documented exit code asserted; each skill and hub entry states what it is NOT good at. The toolkit's own marketing is gated by the toolkit — and sometimes blocked by it, which is the proof it works.",
    "GET IT: Claude Code — /plugin marketplace add wjlgatech/FDE-os (skills auto-discover, MCP server wires via plugin.json). Codex — .codex-plugin/plugin.json, same skills tree. Shell — git clone github.com/wjlgatech/FDE-os and make check. MCP — python3 skills/fde-mcp-server/scripts/server.py. Related live surfaces: fde-os-journey.vercel.app (graded delivery history, auto-deployed report cards), deloitte-triage-brief.vercel.app (the reference runtime presented term-by-term against a real JD).",
    "HONEST BOUNDARIES: everything is deterministic, offline, stdlib-only by design — no embeddings, no live LLM calls inside the engines (the delta-guide proxy and brief copilots call LLMs, the skills do not); grounding checks are lexical proxies and say so; the hub compiles 7 repos today (spec-as-data, add more in repos.yml); doc-understanding refuses PDFs rather than parse them badly. The 83-percent-style vendor numbers quoted anywhere carry their sources; this corpus quotes only the repo's own measured outputs.",
  ],
};

if (typeof window !== "undefined") window.BRIEF_DATA = BRIEF_DATA;
if (typeof module !== "undefined") module.exports = { BRIEF_DATA };
