# delta-guide proxy — give *every* visitor the LLM (no key of their own)

A single Vercel serverless function (`api/guide.js`) that lets the static
[`contribute.html`](../../contribute.html) Delta guide answer through a **shared free LLM**.

The page is static (GitHub Pages, no backend), so it can't safely hold an API key. This proxy
holds the key(s) **server-side** (Vercel env vars, never shipped to the browser) and runs a
**fallback chain** so one throttled free tier doesn't take the guide down. It's the "Option B" to
the page's built-in "Option A" (each visitor brings their own key — that needs no proxy).

It still stays grounded: the page does the RAG (retrieves Delta facts, sends them as the only
context with a "never invent" prompt); the proxy just forwards the chat completion.

## What it protects

The shared key is the thing worth guarding, so the function enforces:
- **Origin allow-list** — only your site may spend the key (`ALLOW_ORIGIN`, default the FDE-os Pages URL).
- **Hard caps** — `max_tokens ≤ 400`, prompt `≤ 8000` chars.
- **Fallback chain** — tries NVIDIA NIM → Groq → Gemini, whichever keys you set, in that order.

## Deploy (≈5 min)

```bash
cd proxy/delta-guide
npx vercel deploy --prod --yes          # first run links/creates the project
```

Then set env vars (at least one key) in the Vercel dashboard → Settings → Environment Variables,
or via CLI:

```bash
npx vercel env add GEMINI_API_KEY production   # free: aistudio.google.com/apikey
# optional extra rungs:
npx vercel env add NVIDIA_API_KEY production   # free: build.nvidia.com/models
npx vercel env add GROQ_API_KEY production     # free: console.groq.com
npx vercel env add ALLOW_ORIGIN production     # e.g. https://wjlgatech.github.io
npx vercel --prod                              # redeploy so env vars take effect
```

Optional model overrides: `MODEL_NIM`, `MODEL_GROQ`, `MODEL_GEMINI` (verify ids live first —
`python3 ~/.claude/skills/free-llm/scripts/nim.py list <family>`).

## Wire it into the page

Set one constant in [`contribute.html`](../../contribute.html):

```js
var GUIDE_PROXY = "https://<your-project>.vercel.app/api/guide";
```

Once set, the guide uses the hosted model **by default for everyone** (badge: `hosted · live`),
and still falls back to the offline grounded guide if the proxy is unreachable. Visitors can also
override with their own key via ⚡ Power mode.

`.vercel/` (project linkage) and any `.env` are intentionally gitignored.
