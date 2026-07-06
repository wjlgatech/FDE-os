// POST /api/verify {token} — recompute the HMAC; report valid / self_issued / tampered.
import { verify, cors, usingDevSecret } from "../lib/sig.js";

export default function handler(req, res) {
  cors(res);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  const r = verify((req.body || {}).token);
  return res.status(200).json({ ...r, dev_secret: usingDevSecret });
}
