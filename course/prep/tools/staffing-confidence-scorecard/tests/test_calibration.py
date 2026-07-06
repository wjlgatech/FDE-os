import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import calibration as cal  # noqa: E402


def recs(delivered=0, dark=0, under=0, rolled=0, pending=0, nogo=0):
    r = []
    r += [{"id": f"d{i}", "predicted_go": True, "outcome": "delivered"} for i in range(delivered)]
    r += [{"id": f"x{i}", "predicted_go": True, "outcome": "went_dark"} for i in range(dark)]
    r += [{"id": f"u{i}", "predicted_go": True, "outcome": "underperformed"} for i in range(under)]
    r += [{"id": f"r{i}", "predicted_go": True, "outcome": "rolled_off"} for i in range(rolled)]
    r += [{"id": f"p{i}", "predicted_go": True, "outcome": "pending"} for i in range(pending)]
    r += [{"id": f"n{i}", "predicted_go": False, "outcome": "pending"} for i in range(nogo)]
    return r


class TestCalibration(unittest.TestCase):
    def test_clean_history_validates(self):
        r = cal.calibrate(recs(delivered=9, dark=1))  # 10% false-GO, at the bar
        self.assertTrue(r["validated"])
        self.assertAlmostEqual(r["false_go_rate"], 0.10)
        self.assertAlmostEqual(r["go_precision"], 0.90)

    def test_high_false_go_fails(self):
        r = cal.calibrate(recs(delivered=5, dark=3, under=2))  # 50% false-GO
        self.assertFalse(r["validated"])
        self.assertAlmostEqual(r["false_go_rate"], 0.50)
        self.assertIn("Recalibrate", r["verdict"])

    def test_pending_is_excluded_never_a_pass(self):
        r = cal.calibrate(recs(delivered=9, dark=1, pending=100))
        self.assertTrue(r["validated"])            # pending doesn't dilute the rate
        self.assertLess(r["coverage"], 0.2)         # but coverage honestly reflects how little is known
        self.assertEqual(r["n_go_scored"], 10)

    def test_rolled_off_is_neutral(self):
        # rolled_off (left for non-performance reasons) must not count as a false-GO
        r = cal.calibrate(recs(delivered=9, dark=1, rolled=20))
        self.assertAlmostEqual(r["false_go_rate"], 0.10)
        self.assertEqual(r["n_go_scored"], 10)

    def test_insufficient_outcomes_is_not_validated(self):
        r = cal.calibrate(recs(delivered=3))       # below MIN_OUTCOMES
        self.assertFalse(r["validated"])
        self.assertFalse(r["measurable"])
        self.assertIn("Not measured", r["verdict"])

    def test_main_exit_nonzero_when_not_validated(self):
        import io, json, tempfile
        p = os.path.join(tempfile.mkdtemp(), "r.json")
        with open(p, "w") as f:
            json.dump(recs(delivered=5, dark=5), f)
        self.assertEqual(cal.main([p, "--json"]), 1)


if __name__ == "__main__":
    unittest.main()
