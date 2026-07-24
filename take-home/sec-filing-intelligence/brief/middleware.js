// Edge middleware: password gate for the whole deployment — page, data.js, and
// both API routes alike. The password lives ONLY in the Vercel env
// (GATE_PASSWORD); this file is public repo content and contains no secret.
// Unlock: the gate page posts /unlock?pw=… → on match, an HMAC-derived cookie
// (unforgeable without the password) admits the browser for 30 days.

export const config = { matcher: "/((?!favicon.ico).*)" };

async function token(secret) {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign(
    "HMAC", key, new TextEncoder().encode("sec-filing-brief-gate-v1"));
  return Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, "0")).join("");
}

const GATE_HTML = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Private case study</title>
<style>body{background:#f0ede4;color:#46423a;font-family:"Hanken Grotesk",-apple-system,sans-serif;
display:grid;place-items:center;min-height:100vh;margin:0}
.card{background:#faf8f2;border:1px solid #e6e1d3;border-radius:16px;padding:34px 38px;max-width:400px;text-align:center}
h1{font-family:Georgia,serif;font-weight:500;font-size:26px;margin:0 0 8px}h1 em{font-style:italic;color:#cc785c}
p{font-size:14px;color:#7d776b;margin:0 0 18px}
input{width:100%;box-sizing:border-box;padding:11px 15px;border:1px solid #ddd7c8;border-radius:999px;font-size:14px;margin-bottom:10px}
button{width:100%;background:#cc785c;color:#fff;border:none;border-radius:999px;padding:11px;font-weight:700;font-size:14px;cursor:pointer}
.err{color:#b0452f;font-size:13px;min-height:18px;margin-top:8px}</style></head><body>
<div class="card"><h1>Founding members <em>only</em></h1>
<p>This case study is password-protected. Seats + password: see the Case-Study Vault offer on the FDE-os community page.</p>
<input id="pw" type="password" placeholder="Password" onkeydown="if(event.key==='Enter')go()">
<button onclick="go()">Unlock</button><div class="err" id="err"></div></div>
<script>function go(){var p=document.getElementById('pw').value;if(!p)return;
fetch('/unlock?pw='+encodeURIComponent(p)).then(function(r){if(r.ok){location.href='/';}
else{document.getElementById('err').textContent='Wrong password.';}});}
</script></body></html>`;

export default async function middleware(req) {
  const secret = process.env.GATE_PASSWORD;
  if (!secret) {
    return new Response("gate misconfigured: GATE_PASSWORD env missing", { status: 503 });
  }
  const expected = await token(secret);
  const cookies = req.headers.get("cookie") || "";
  if (cookies.includes(`csgate=${expected}`)) {
    return; // admitted — fall through to the deployment
  }
  const url = new URL(req.url);
  if (url.pathname === "/unlock") {
    if (url.searchParams.get("pw") === secret) {
      return new Response(null, {
        status: 204,
        headers: {
          "Set-Cookie": `csgate=${expected}; Path=/; Max-Age=2592000; HttpOnly; Secure; SameSite=Lax`,
        },
      });
    }
    return new Response("no", { status: 401 });
  }
  return new Response(GATE_HTML, {
    status: 401,
    headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
  });
}
