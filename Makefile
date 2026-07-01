# FDE-os — one finish line for humans, CI, and agents alike.
# `make check` is the repo's discoverable verification harness (anyagent, goal-10x,
# and CI all key off the same command — no drift between what each of them runs).

PY ?= python3
TEST_DIRS = skills/*/tests workflows/*/tests tests

.PHONY: check test freshness

check: test  ## everything that must be green before a merge (fast, offline)

test:  ## the full unit-test suite (same globs as CI)
	$(PY) -m pytest $(TEST_DIRS) -q

freshness:  ## networked link-freshness probe (CI runs this weekly; not part of `check`)
	$(PY) scripts/check_freshness.py README.md field-kits/README.md FDE-research-synthesis.md
