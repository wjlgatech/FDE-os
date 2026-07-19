"""outcome-contract tests — the honesty rules are the spec."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from outcome_score import (  # noqa: E402
    ContractError, score_contract, score_outcome, main,
    PASS, FAIL, CLAIMED, NOT_MEASURED,
)


def outcome(**kw):
    base = {"id": "o1", "metric": "m", "target": 60, "direction": ">=", "blocking": True}
    base.update(kw)
    return base


def contract(*outcomes):
    return {"engagement": "acme-test", "outcomes": list(outcomes)}


# --- outcome-level rules -------------------------------------------------

def test_measured_meeting_target_passes():
    r = score_outcome(outcome(evidence={"kind": "measured", "value": 72.5, "source": "https://x/y.csv"}))
    assert r["status"] == PASS


def test_measured_missing_target_fails():
    r = score_outcome(outcome(evidence={"kind": "measured", "value": 41, "source": "https://x"}))
    assert r["status"] == FAIL


def test_direction_lte():
    r = score_outcome(outcome(target=5, direction="<=",
                              evidence={"kind": "measured", "value": 3, "source": "https://x"}))
    assert r["status"] == PASS


def test_claimed_never_passes_even_if_it_meets_target():
    r = score_outcome(outcome(evidence={"kind": "claimed", "value": 99}))
    assert r["status"] == CLAIMED


def test_measured_without_source_downgrades_to_claimed():
    r = score_outcome(outcome(evidence={"kind": "measured", "value": 99}))
    assert r["status"] == CLAIMED
    assert "downgraded" in r["detail"]


def test_no_evidence_is_not_measured_never_fake_pass():
    r = score_outcome(outcome())
    assert r["status"] == NOT_MEASURED


def test_baseline_delta_reported():
    r = score_outcome(outcome(baseline=10,
                              evidence={"kind": "measured", "value": 70, "source": "https://x"}))
    assert r["delta_vs_baseline"] == 60


# --- gate rules ----------------------------------------------------------

def test_go_requires_all_blocking_pass():
    rep = score_contract(contract(
        outcome(id="a", evidence={"kind": "measured", "value": 70, "source": "https://x"}),
        outcome(id="b", target=5, direction="<=",
                evidence={"kind": "measured", "value": 2, "source": "https://x"}),
    ))
    assert rep["verdict"] == "GO"


@pytest.mark.parametrize("bad_evidence", [
    None,                                         # not measured
    {"kind": "claimed", "value": 99},             # claimed
    {"kind": "measured", "value": 1, "source": "https://x"},  # measured fail
])
def test_gate_cannot_pass_on_non_passing_blocking_outcome(bad_evidence):
    o = outcome(id="bad") if bad_evidence is None else outcome(id="bad", evidence=bad_evidence)
    rep = score_contract(contract(
        outcome(id="good", evidence={"kind": "measured", "value": 70, "source": "https://x"}),
        o,
    ))
    assert rep["verdict"] == "NO-GO"


def test_advisory_outcome_does_not_block():
    rep = score_contract(contract(
        outcome(id="good", evidence={"kind": "measured", "value": 70, "source": "https://x"}),
        outcome(id="fyi", blocking=False),
    ))
    assert rep["verdict"] == "GO"
    assert rep["counts"][NOT_MEASURED] == 1


# --- malformed contracts fail loudly, never silently ---------------------

@pytest.mark.parametrize("bad", [
    {},                                            # no engagement
    {"engagement": "x"},                           # no outcomes
    {"engagement": "x", "outcomes": []},           # empty outcomes
    {"engagement": "x", "outcomes": [{"id": "a", "metric": "m", "target": 1, "direction": "up"}]},
    {"engagement": "x", "outcomes": [                       # duplicate ids
        {"id": "a", "metric": "m", "target": 1, "direction": ">="},
        {"id": "a", "metric": "m", "target": 1, "direction": ">="}]},
])
def test_malformed_contract_raises(bad):
    with pytest.raises(ContractError):
        score_contract(bad)


def test_all_advisory_contract_rejected():
    with pytest.raises(ContractError):
        score_contract(contract(outcome(id="a", blocking=False)))


# --- CLI exit codes are the CI gate --------------------------------------

def _write(tmp_path, data):
    p = tmp_path / "c.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_cli_go_exits_zero(tmp_path, capsys):
    p = _write(tmp_path, contract(
        outcome(evidence={"kind": "measured", "value": 70, "source": "https://x"})))
    assert main(["score", p]) == 0
    assert "VERDICT: GO" in capsys.readouterr().out


def test_cli_nogo_exits_two(tmp_path, capsys):
    p = _write(tmp_path, contract(outcome()))
    assert main(["score", p]) == 2
    assert "NO-GO" in capsys.readouterr().out


def test_cli_malformed_exits_one(tmp_path, capsys):
    p = _write(tmp_path, {"engagement": "x"})
    assert main(["score", p]) == 1
    assert "error:" in capsys.readouterr().err
