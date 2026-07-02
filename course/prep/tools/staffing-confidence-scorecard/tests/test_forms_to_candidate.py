import os
import sys
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
import forms_to_candidate as f2c  # noqa: E402
import scorecard as sc  # noqa: E402

EX = os.path.join(HERE, "..", "examples")


class TestConverter(unittest.TestCase):
    def test_example_csvs_build_a_go_candidate(self):
        cand = {
            "candidate": "anon-0042", "role_type": "technical",
            "reliability": f2c.build_reliability(os.path.join(EX, "reference.csv"), "anon-0042"),
            "technical_competence": f2c.build_technical(os.path.join(EX, "worksample.csv"), "anon-0042"),
            "resourcefulness": f2c.build_resourcefulness(os.path.join(EX, "teachback.csv"), "anon-0042"),
        }
        self.assertEqual(len(cand["reliability"]["references"]), 2)
        self.assertTrue(sc.evaluate(cand)["go"])

    def test_worksample_score_is_sum_over_15(self):
        ws = f2c.build_technical(os.path.join(EX, "worksample.csv"), "anon-0042")["work_sample"]
        self.assertAlmostEqual(ws["score"], round((3 + 3 + 2 + 3 + 2) / 15, 2))
        self.assertTrue(ws["observed"])

    def test_no_show_answer_sets_dark_flag(self):
        import csv, tempfile
        path = os.path.join(tempfile.mkdtemp(), "r.csv")
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["Candidate id", "Your relationship", "When something slipped did they flag it?",
                        "Would you staff them again?", "Did they ever no-show or go dark?"])
            w.writerow(["x1", "Client-team lead", "Flagged it proactively", "Yes", "Repeatedly"])
        rel = f2c.build_reliability(path, "x1")
        self.assertTrue(rel["references"][0]["went_dark_or_noshow"])

    def test_missing_required_column_is_hard_error(self):
        import csv, tempfile
        path = os.path.join(tempfile.mkdtemp(), "bad.csv")
        with open(path, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(["Candidate id", "Random column"])
        with self.assertRaises(KeyError):
            f2c.build_reliability(path, "x1")

    def test_id_filter_selects_only_matching_rows(self):
        rel = f2c.build_reliability(os.path.join(EX, "reference.csv"), "does-not-exist")
        self.assertEqual(rel["references"], [])


if __name__ == "__main__":
    unittest.main()
