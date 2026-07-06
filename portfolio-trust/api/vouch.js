// POST /api/vouch — a DIFFERENT person signs a structured reference. Non-self-issuable:
// voucher must not equal subject. Returns a signed token the subject embeds in their agent-card.
import { sign, norm, cors, usingDevSecret } from "../lib/sig.js";

const RELS = new Set(["client_team", "internal_team"]);

export default function handler(req, res) {
  cors(res);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const b = req.body || {};
  const subject = String(b.subject || "").trim();
  const voucher = String(b.voucher || "").trim();
  if (!subject || !voucher) return res.status(400).json({ error: "subject and voucher are required" });
  if (norm(subject) === norm(voucher)) return res.status(400).json({ error: "a vouch cannot be self-issued: voucher must differ from subject" });
  const relationship = RELS.has(b.relationship) ? b.relationship : "internal_team";

  const payload = {
    subject, voucher, relationship,
    worked_with: b.worked_with !== false,                 // they attest they actually worked together
    would_staff_again: !!b.would_staff_again,
    went_dark_or_noshow: !!b.went_dark_or_noshow,
    engagement: String(b.engagement || "").slice(0, 160),
    iat: Date.now(),
  };
  return res.status(200).json({ token: sign(payload), payload, dev_secret: usingDevSecret });
}
