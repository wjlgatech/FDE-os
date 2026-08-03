# FDE-os — one finish line for humans, CI, and agents alike.
# `make check` is the repo's discoverable verification harness (anyagent, goal-10x,
# and CI all key off the same command — no drift between what each of them runs).

PY ?= python3
TEST_DIRS = skills/*/tests workflows/*/tests take-home/*/tests snowflake-os/tests tests

.PHONY: check test freshness snowflake-gate snowflake-sync

check: test snowflake-gate  ## everything that must be green before a merge (fast, offline)

test:  ## the full unit-test suite (same globs as CI)
	$(PY) -m pytest $(TEST_DIRS) -q

snowflake-gate:  ## snowflake-os knowledge-base integrity (10 checks) + build freshness
	$(PY) snowflake-os/scripts/build.py --check
	$(PY) snowflake-os/scripts/gate.py

snowflake-sync:  ## NETWORKED — refresh the catalogue snapshot from learn.snowflake.com
	$(PY) snowflake-os/scripts/sync.py fetch
	$(PY) snowflake-os/scripts/build.py
	$(PY) snowflake-os/scripts/graph.py build \
	  --out knowledge/snowflake-catalog.graph.json --html knowledge/snowflake-catalog.html

freshness:  ## networked link-freshness probe (CI runs this weekly; not part of `check`)
	$(PY) scripts/check_freshness.py README.md field-kits/README.md FDE-research-synthesis.md
