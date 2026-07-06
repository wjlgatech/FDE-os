// sig.js — the trust primitive. A vouch is a server-signed, tamper-evident token that binds
// voucher → subject → claim → time. You cannot forge one client-side (needs the HMAC secret),
// and you cannot edit a field without breaking the signature. Storage-free: the token IS the record.
import crypto from "node:crypto";

const SECRET = process.env.VOUCH_SECRET || "dev-insecure-secret";
export const usingDevSecret = !process.env.VOUCH_SECRET;

// canonical form: sorted keys, so the signature is stable regardless of field order
function canon(o) {
  return JSON.stringify(Object.keys(o).sort().reduce((a, k) => ((a[k] = o[k]), a), {}));
}

export function sign(payload) {
  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const sig = crypto.createHmac("sha256", SECRET).update(canon(payload)).digest("hex");
  return body + "." + sig;
}

export function verify(token) {
  if (typeof token !== "string" || !token.includes(".")) return { valid: false, reason: "malformed" };
  const [body, sig] = token.split(".");
  let payload;
  try { payload = JSON.parse(Buffer.from(body, "base64url").toString()); }
  catch (_) { return { valid: false, reason: "unparseable" }; }
  const expect = crypto.createHmac("sha256", SECRET).update(canon(payload)).digest("hex");
  const ok = typeof sig === "string" && sig.length === expect.length &&
    crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expect));
  if (!ok) return { valid: false, reason: "bad signature", payload };
  const self_issued = norm(payload.subject) === norm(payload.voucher);
  return { valid: true, self_issued, payload };
}

export function norm(s) { return String(s || "").trim().toLowerCase(); }

export function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}
