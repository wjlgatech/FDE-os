// interview-agent — the COLLECT stage as a conversational evidence collector.
//
// Evidence-based trait inference: instead of asking a candidate to self-rate,
// an interviewer AGENT probes for specific PAST BEHAVIOR, then infers signals from what they
// actually said. The honest posture (same as the gate): an interview can only produce CLAIMED-
// tier signal + a list of what to verify next — it never fabricates observed evidence and never
// on its own yields a GO. Inference here → validation (work sample / reference) downstream.
//
// Two actions:
//   POST {action:"turn",    messages:[...]}  -> { content, done }        (next interviewer question)
//   POST {action:"extract", messages:[...]}  -> { dossier, candidate }   (structured evidence)
//
// LLM backend: direct provider keys if present, else the shared delta-guide proxy (no new secrets).

const CHAIN = [
  { name: "nvidia", base: "https://integrate.api.nvidia.com/v1", key: process.env.NVIDIA_API_KEY, model: process.env.MODEL_NIM || "z-ai/glm-5.1" },
  { name: "groq", base: "https://api.groq.com/openai/v1", key: process.env.GROQ_API_KEY, model: process.env.MODEL_GROQ || "llama-3.3-70b-versatile" },
  { name: "gemini", base: "https://generativelanguage.googleapis.com/v1beta/openai", key: process.env.GEMINI_API_KEY, model: process.env.MODEL_GEMINI || "gemini-2.5-flash" },
].filter((p) => p.key);

const PROXY = process.env.GUIDE_PROXY || "https://delta-guide-eosin.vercel.app/api/guide";
const ALLOW = (process.env.ALLOW_ORIGIN || "*").split(",").map((s) => s.trim());
const MAX_TURNS = 8;   // hard cap on interviewer questions before we force extraction

const AREAS = ["reliability", "resourcefulness", "technical"];

const INTERVIEWER_SYS =
  "You are a warm, sharp staffing intake interviewer. Assess THREE things ONLY by asking about " +
  "the candidate's SPECIFIC PAST BEHAVIOR (never hypotheticals or self-ratings):\n" +
  "1) reliability — did they show up, communicate proactively, and deliver end-to-end;\n" +
  "2) resourcefulness — learning an unfamiliar tool fast and shipping (outcome over method);\n" +
  "3) technical depth — the hardest agent/RAG/Python problem they personally solved.\n" +
  "Rules: ONE question at a time. Open with reliability. Ask at most ONE probing follow-up per area " +
  "to pull out a concrete story (who / what / when / the result). Then move to the next area. " +
  "When you have a specific story for all THREE areas, reply with a one-line thank-you and the exact " +
  "token [[COMPLETE]] on its own line. Keep every message under 40 words. No preamble, no lists.";

const EXTRACT_SYS =
  "From the interview transcript ONLY, infer evidence for three criteria. Do NOT invent anything.\n" +
  "For each criterion return a tier:\n" +
  "  observed_story = a specific past story with who/what and a concrete result;\n" +
  "  claimed        = a generic assertion with no specifics;\n" +
  "  not_evidenced  = they did not substantiate it.\n" +
  "When unsure, choose the LOWER tier. Quote the single strongest supporting line from the candidate.\n" +
  'Output ONLY strict JSON, no prose, no code fence:\n' +
  '{"reliability":{"tier":"...","quote":"...","note":"..."},' +
  '"resourcefulness":{"tier":"...","quote":"...","note":"..."},' +
  '"technical":{"tier":"...","quote":"...","note":"..."}}';

async function callLLM(messages, { temperature = 0.4, max_tokens = 320 } = {}) {
  // Direct provider chain (if this project has its own keys)…
  for (const p of CHAIN) {
    try {
      const r = await fetch(p.base.replace(/\/$/, "") + "/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + p.key },
        body: JSON.stringify({ model: p.model, messages, temperature, max_tokens }),
      });
      if (!r.ok) continue;
      const d = await r.json();
      const t = d?.choices?.[0]?.message?.content;
      if (t) return t;
    } catch (_) { /* try next */ }
  }
  // …else the shared proxy (server-to-server: no Origin header, so its allow-list passes).
  // Free-tier providers are intermittent, so retry a few times before giving up.
  let lastErr = "proxy failed";
  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      const r = await fetch(PROXY, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages, temperature, max_tokens }),
      });
      if (r.ok) {
        const d = await r.json();
        const t = d?.choices?.[0]?.message?.content;
        if (t) return t;
        lastErr = "empty";
      } else {
        lastErr = "HTTP " + r.status;
      }
    } catch (e) {
      lastErr = String(e.message || e);
    }
    if (attempt < 3) await new Promise((res) => setTimeout(res, 1200 * (attempt + 1)));
  }
  throw new Error("llm backend unavailable (" + lastErr + "). Set a provider key (GROQ_API_KEY / GEMINI_API_KEY) on this project for reliability.");
}

function parseJSON(text) {
  const a = text.indexOf("{"), b = text.lastIndexOf("}");
  if (a < 0 || b < 0) return null;
  try { return JSON.parse(text.slice(a, b + 1)); } catch (_) { return null; }
}

const TIERS = new Set(["observed_story", "claimed", "not_evidenced"]);
function validDossier(o) {
  return o && AREAS.every((k) => o[k] && TIERS.has(o[k].tier) && typeof o[k].quote === "string");
}

// Map inferred interview signal → a scorecard-compatible partial record. HONEST by design:
// an interview is intake, so reliability/technical land at CLAIMED at best (they still need a
// real reference / observed work sample); only resourcefulness can be evidenced by an artifact-
// style story here. Every area also emits the concrete next evidence to collect.
function toCandidateAndNext(dossier) {
  const next = [];
  if (dossier.reliability.tier !== "observed_story") next.push("reliability: get a structured reference from someone who ran a project with them");
  else next.push("reliability: confirm the story with a structured reference (a claimed story is not yet a vouch)");
  if (dossier.technical.tier !== "observed_story") next.push("technical: run the 90-minute observed work sample");
  else next.push("technical: verify with the observed work sample (an interview story is not a graded build)");
  if (dossier.resourcefulness.tier !== "observed_story") next.push("resourcefulness: give them an unfamiliar tool for a day + a teach-back");

  const candidate = {
    candidate: "interview-intake",
    role_type: "technical",
    reliability: { references: [] },                                   // interview ≠ a vouch → left empty on purpose
    technical_competence: { work_sample: { observed: false, score: 0, threshold: 0.7 } },  // still needs the graded build
    resourcefulness: { teach_back: {
      artifact_worked: dossier.resourcefulness.tier === "observed_story",
      teachback_clear: dossier.resourcefulness.tier === "observed_story",
      got_unstuck: dossier.resourcefulness.tier !== "not_evidenced",
    } },
  };
  return { candidate, next_evidence: next };
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", ALLOW.includes("*") ? "*" : ALLOW[0]);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const body = req.body || {};
  const action = body.action || "turn";
  const messages = Array.isArray(body.messages) ? body.messages : [];

  try {
    if (action === "turn") {
      const asked = messages.filter((m) => m.role === "assistant").length;
      if (asked >= MAX_TURNS) return res.status(200).json({ content: "Thanks — that's everything I need. [[COMPLETE]]", done: true });
      const content = await callLLM([{ role: "system", content: INTERVIEWER_SYS }, ...messages], { temperature: 0.5, max_tokens: 120 });
      return res.status(200).json({ content: content.replace("[[COMPLETE]]", "").trim(), done: /\[\[COMPLETE\]\]/.test(content) });
    }

    if (action === "extract") {
      const transcript = messages.map((m) => (m.role === "assistant" ? "Interviewer: " : "Candidate: ") + m.content).join("\n");
      let out = await callLLM([{ role: "system", content: EXTRACT_SYS }, { role: "user", content: transcript }], { temperature: 0.1, max_tokens: 360 });
      let dossier = parseJSON(out);
      if (!validDossier(dossier)) {
        out = await callLLM([{ role: "system", content: EXTRACT_SYS },
          { role: "user", content: transcript },
          { role: "user", content: "Return ONLY the JSON object, nothing else." }], { temperature: 0, max_tokens: 360 });
        dossier = parseJSON(out);
      }
      if (!validDossier(dossier)) return res.status(502).json({ error: "could not extract structured evidence" });
      const { candidate, next_evidence } = toCandidateAndNext(dossier);
      return res.status(200).json({ dossier, candidate, next_evidence });
    }

    return res.status(400).json({ error: "action must be 'turn' or 'extract'" });
  } catch (e) {
    return res.status(502).json({ error: String(e.message || e) });
  }
}
