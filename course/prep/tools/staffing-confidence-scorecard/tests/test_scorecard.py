import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import scorecard as sc  # noqa: E402


def _ref(worked=True, again=True, dark=False, source="client_team"):
    return {"source": source, "worked_with": worked, "would_staff_again": again,
            "went_dark_or_noshow": dark, "communicated_proactively": True, "delivered_end_to_end": True}


def _cand(role="technical", refs=None, ws=(True, 0.84, 0.7), tb=(True, True, True)):
    c = {"role_type": role, "reliability": {"references": refs if refs is not None else [_ref()]}}
    if ws is not None:
        c["technical_competence"] = {"work_sample": {"observed": ws[0], "score": ws[1], "threshold": ws[2]}}
    if tb is not None:
        c["resourcefulness"] = {"teach_back": {"artifact_worked": tb[0], "teachback_clear": tb[1], "got_unstuck": tb[2]}}
    return c


class TestGate(unittest.TestCase):
    def test_full_evidence_go(self):
        r = sc.evaluate(_cand())
        self.assertTrue(r["go"], msg=[b.detail for b in r["blockers"]])

    def test_dark_flag_is_automatic_nogo(self):
        # one credible no-show/went-dark is never averaged away
        r = sc.evaluate(_cand(refs=[_ref(), _ref(dark=True)]))
        self.assertFalse(r["go"])
        self.assertTrue(any(b.name == "reliability" for b in r["blockers"]))

    def test_no_reference_from_someone_who_worked_with_them_blocks(self):
        r = sc.evaluate(_cand(refs=[_ref(worked=False)]))
        self.assertFalse(r["go"])

    def test_empty_references_blocks(self):
        r = sc.evaluate(_cand(refs=[]))
        self.assertFalse(r["go"])

    def test_would_not_staff_again_blocks(self):
        r = sc.evaluate(_cand(refs=[_ref(again=False)]))
        self.assertFalse(r["go"])

    def test_internal_team_vouch_counts(self):
        r = sc.evaluate(_cand(refs=[_ref(source="internal_team")]))
        self.assertTrue(r["go"])

    def test_unobserved_work_sample_blocks_technical(self):
        r = sc.evaluate(_cand(ws=(False, 0.9, 0.7)))
        self.assertFalse(r["go"])

    def test_work_sample_below_bar_blocks_technical(self):
        r = sc.evaluate(_cand(ws=(True, 0.55, 0.7)))
        self.assertFalse(r["go"])

    def test_weak_tech_is_informational_for_non_technical_role(self):
        # reliable + resourceful, weak tech, but role is non_technical → still GO
        r = sc.evaluate(_cand(role="non_technical", ws=(True, 0.4, 0.7)))
        self.assertTrue(r["go"])
        tech = next(a for a in r["axes"] if a.name == "technical_competence")
        self.assertFalse(tech.required)

    def test_reliable_but_not_technical_is_nogo_for_technical_role(self):
        # her exact point: reliable but no tech = useless for a technical role
        r = sc.evaluate(_cand(ws=(True, 0.3, 0.7)))
        self.assertFalse(r["go"])

    def test_made_it_work_but_cannot_teach_blocks(self):
        r = sc.evaluate(_cand(tb=(True, False, True)))
        self.assertFalse(r["go"])
        rr = next(a for a in r["axes"] if a.name == "resourcefulness")
        self.assertIn("teach", rr.detail)

    def test_pattern_needs_two_vouches(self):
        one = sc.evaluate(_cand(refs=[_ref()]))
        two = sc.evaluate(_cand(refs=[_ref(), _ref(source="internal_team")]))
        self.assertFalse(next(a for a in one["axes"] if a.name == "reliability").pattern)
        self.assertTrue(next(a for a in two["axes"] if a.name == "reliability").pattern)

    def test_bad_role_type_is_hard_error(self):
        with self.assertRaises(ValueError):
            sc.evaluate({"role_type": "wizard"})

    def test_example_candidate_passes(self):
        path = os.path.join(os.path.dirname(__file__), "..", "candidate.example.json")
        with open(path, encoding="utf-8") as f:
            self.assertTrue(sc.evaluate(json.load(f))["go"])


if __name__ == "__main__":
    unittest.main()
