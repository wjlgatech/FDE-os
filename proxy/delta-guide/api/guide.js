// delta-guide proxy — gives the static contribute.html Delta guide a SHARED free LLM,
// so every visitor gets real answers without bringing their own key.
//
// Unlike the BYO-key nim-bridge (which holds nothing), this function HOLDS the keys as
// Vercel env vars (server-side, never shipped to the browser) and tries a fallback chain
// so one throttled free tier doesn't kill the guide. Abuse guards: origin allow-list +
// hard caps on tokens and message size (the shared key is the thing worth protecting).
//
// Deploy: see ../README.md. The browser calls POST /api/guide with {messages,...} and NO key.

const CHAIN = [
  { name: "nvidia", base: "https://integrate.api.nvidia.com/v1",
    key: process.env.NVIDIA_API_KEY, model: process.env.MODEL_NIM || "z-ai/glm-5.1" },
  { name: "groq", base: "https://api.groq.com/openai/v1",
    key: process.env.GROQ_API_KEY, model: process.env.MODEL_GROQ || "llama-3.3-70b-versatile" },
  { name: "gemini", base: "https://generativelanguage.googleapis.com/v1beta/openai",
    key: process.env.GEMINI_API_KEY, model: process.env.MODEL_GEMINI || "gemini-2.5-flash" },
].filter((p) => p.key);

// Restrict who may spend the shared key. Set ALLOW_ORIGIN to your site (comma-separated ok).
const ALLOW = (process.env.ALLOW_ORIGIN || "https://wjlgatech.github.io")
  .split(",").map((s) => s.trim());

const MAX_TOKENS = 400;        // cap the spend per call
const MAX_CHARS = 8000;        // cap total prompt size

function cors(res, origin) {
  const ok = ALLOW.includes("*") ? "*" : (ALLOW.includes(origin) ? origin : ALLOW[0]);
  res.setHeader("Access-Control-Allow-Origin", ok);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Vary", "Origin");
}

export default async function handler(req, res) {
  const origin = req.headers.origin || "";
  cors(res, origin);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  if (!ALLOW.includes("*") && origin && !ALLOW.includes(origin)) {
    return res.status(403).json({ error: "origin not allowed" });
  }
  if (!CHAIN.length) {
    return res.status(503).json({ error: "no provider configured — set NVIDIA_API_KEY / GROQ_API_KEY / GEMINI_API_KEY" });
  }

  const body = req.body || {};
  const messages = Array.isArray(body.messages) ? body.messages : null;
  if (!messages) return res.status(400).json({ error: "send {messages:[...]}" });
  const chars = JSON.stringify(messages).length;
  if (chars > MAX_CHARS) return res.status(413).json({ error: "prompt too large" });

  const payload = {
    messages,
    temperature: typeof body.temperature === "number" ? body.temperature : 0.3,
    max_tokens: Math.min(body.max_tokens || 300, MAX_TOKENS),
  };

  let lastErr = "all providers failed";
  for (const p of CHAIN) {
    try {
      const r = await fetch(p.base.replace(/\/$/, "") + "/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + p.key },
        body: JSON.stringify({ ...payload, model: p.model }),
      });
      if (!r.ok) { lastErr = `${p.name}: HTTP ${r.status}`; continue; }
      const data = await r.json();
      const text = data?.choices?.[0]?.message?.content || "";
      if (!text) { lastErr = `${p.name}: empty`; continue; }
      // normalize to a minimal OpenAI-shaped response + which rung answered
      return res.status(200).json({
        choices: [{ message: { role: "assistant", content: text } }],
        provider: p.name, model: p.model,
      });
    } catch (e) {
      lastErr = `${p.name}: ${String(e).slice(0, 120)}`;
    }
  }
  return res.status(502).json({ error: lastErr });
}
