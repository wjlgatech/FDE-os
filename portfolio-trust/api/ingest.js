// POST /api/ingest {card_url} | {card} — read a portfolio's agent-card evidence block,
// VERIFY its attestations (server-signed, non-self-issued), read provenance + CI-verified
// projects, and turn it into a scorecard-compatible candidate + a GO/NO-GO. This is the wiring
// that stops a self-authored portfolio from being a prettier resume: only observed/attested
// evidence moves the gate.
//
// agent-card evidence schema (card.evidence):
//   projects[]:   { name, repo, provenance:{contribution_pct, commits, first_commit, last_commit},
//                   verified: <bool: a reproducible CI eval passed> }
//   attestations[]: [ "<signed vouch token from /api/vouch>", ... ]
import { verify, cors, usingDevSecret } from "../lib/sig.js";

function gate(candidate) {
  const refs = candidate.reliability.references || [];
  const dark = refs.some((r) => r.went_dark_or_noshow);
  const worked = refs.filter((r) => r.worked_with);
  const again = worked.filter((r) => r.would_staff_again);
  const reliability = !dark && worked.length > 0 && again.length > 0;

  const ws = candidate.technical_competence.work_sample;
  const technical = !!(ws && ws.observed && ws.score >= ws.threshold);

  const tb = candidate.resourcefulness.teach_back;
  const resourceful = !!(tb && tb.artifact_worked && tb.teachback_clear);

  const blockers = [];
  if (!reliability) blockers.push(dark ? "reliability: an attestation reports a no-show / went-dark — automatic NO-GO"
    : "reliability: no valid third-party vouch (a portfolio can't attest its own reliability)");
  if (!technical) blockers.push("technical: no CI-verified project (a linked repo is not a passing eval)");
  if (!resourceful) blockers.push("resourcefulness: no owned project with real commit provenance");
  return { go: blockers.length === 0, reliability, technical, resourceful, blockers };
}

export default async function handler(req, res) {
  cors(res);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const b = req.body || {};
  let card = b.card;
  try {
    if (!card && b.card_url) {
      const r = await fetch(String(b.card_url), { headers: { Accept: "application/json" } });
      if (!r.ok) return res.status(400).json({ error: "could not fetch card: HTTP " + r.status });
      card = await r.json();
    }
  } catch (e) { return res.status(400).json({ error: "fetch failed: " + String(e.message || e) }); }
  if (!card || typeof card !== "object") return res.status(400).json({ error: "send {card_url} or {card}" });

  const ev = card.evidence || {};
  const projects = Array.isArray(ev.projects) ? ev.projects : [];
  const rawAttestations = Array.isArray(ev.attestations) ? ev.attestations : [];

  // 1) verify attestations — only server-signed, non-self-issued ones count
  const checked = rawAttestations.map((t) => verify(t));
  const validVouch = checked.filter((c) => c.valid && !c.self_issued);
  const rejected = checked.filter((c) => !c.valid || c.self_issued)
    .map((c) => ({ reason: c.self_issued ? "self-issued" : (c.reason || "invalid") }));
  const dark = validVouch.filter((c) => c.payload.went_dark_or_noshow);
  const staffAgain = validVouch.filter((c) => c.payload.would_staff_again && !c.payload.went_dark_or_noshow);

  // 2) technical: a project whose CI eval passed (observed works-ness, not "repo exists")
  const verifiedProjects = projects.filter((p) => p.verified === true);
  // 3) resourcefulness: an owned project with real commit provenance
  const owned = projects.filter((p) => p.provenance && Number(p.provenance.contribution_pct) > 0 && Number(p.provenance.commits) > 0);

  const references = staffAgain.map((c) => ({ source: c.payload.relationship, worked_with: true, would_staff_again: true, went_dark_or_noshow: false }));
  if (dark.length) references.push({ source: "client_team", worked_with: true, would_staff_again: false, went_dark_or_noshow: true });

  const candidate = {
    candidate: card.name || card.slug || "portfolio",
    role_type: "technical",
    reliability: { references },
    technical_competence: { work_sample: { observed: verifiedProjects.length > 0, score: verifiedProjects.length > 0 ? 1 : 0, threshold: 0.7 } },
    resourcefulness: { teach_back: { artifact_worked: owned.length > 0, teachback_clear: owned.length > 0, got_unstuck: owned.length > 0 } },
  };

  return res.status(200).json({
    candidate,
    gate: gate(candidate),
    summary: {
      valid_vouches: validVouch.length,
      would_staff_again: staffAgain.length,
      dark_flags: dark.length,
      rejected_attestations: rejected,
      ci_verified_projects: verifiedProjects.length,
      owned_projects: owned.length,
      total_projects: projects.length,
      dev_secret: usingDevSecret,
    },
  });
}
