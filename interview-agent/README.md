# interview-agent — conversational evidence collector (Vercel)

An agentic intake webapp: a short interviewer that probes past behavior and infers
reliability / resourcefulness / technical signals, then names exactly what to verify next.
It **infers**; the work sample and reference **validate**. See [`SPEC.md`](SPEC.md).

- `index.html` — the chat UI + intake-dossier card (static, served by Vercel).
- `api/interview.js` — the agent: `action:"turn"` (next question) and `action:"extract"`
  (schema-validated evidence). LLM via provider keys or the shared proxy fallback.

## Deploy

```bash
cd interview-agent
vercel --prod            # first run links/creates the project; deploys to a *.vercel.app URL
```

### Reliability (recommended)
The proxy fallback uses shared free-tier keys that throttle. For a solid demo, give this project
its own key (Groq's free tier is fast and generous):

```bash
vercel env add GROQ_API_KEY production      # paste a key from console.groq.com
vercel --prod                                # redeploy to pick it up
```

With a key set, `api/interview.js` uses it directly and ignores the proxy.

## Verify locally (no deploy, no live LLM needed)
The handler's logic (turn flow, `[[COMPLETE]]`, JSON extract, honest tier→scorecard mapping) is
verified by mocking the LLM — see the repo's `/tmp` harness pattern. The intake record it produces
scores **NO-GO** through `staffing-confidence-scorecard/scorecard.py` by design (a chat can't be a
vouch or a graded build).
