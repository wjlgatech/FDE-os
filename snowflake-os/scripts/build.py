#!/usr/bin/env python3
"""snowflake-os · build — compile the curated YAML spec into a stdlib-readable artifact.

    python3 snowflake-os/scripts/build.py            # compile
    python3 snowflake-os/scripts/build.py --check    # exit 3 if the artifact is stale

WHY A BUILD STEP. FDE-os's CI installs nothing — the offline engines must be
pure stdlib, and `import yaml` is not. So the human-authored source of truth
stays YAML (`data/competencies.yml`, comments and all) and this tool compiles it
to `snapshot/competencies.json`, which every engine and gate reads.

The compiled artifact records the sha256 of its YAML source, so `--check` — and
the offline gate — can prove the JSON still matches the YAML using nothing but
hashlib. Edit the YAML, forget to rebuild, and the build goes red.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "competencies.yml"
OUT = ROOT / "snapshot" / "competencies.json"
SAT_SRC = ROOT / "data" / "satellites.yml"
SAT_OUT = ROOT / "snapshot" / "satellites.json"


def source_sha256(path: Path = SRC) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compile(src: Path, rel: str) -> dict:
    import yaml  # deferred: authoring-time only, never on the offline read path

    spec = yaml.safe_load(src.read_text(encoding="utf-8"))
    spec["source"] = {
        "file": rel,
        "sha256": source_sha256(src),
        "compiled_by": "snowflake-os/scripts/build.py",
    }
    return spec


def compile_spec() -> dict:
    return _compile(SRC, "snowflake-os/data/competencies.yml")


def compile_satellites() -> dict:
    return _compile(SAT_SRC, "snowflake-os/data/satellites.yml")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="verify the artifact is current; exit 3 if stale")
    args = p.parse_args(argv)

    pairs = ((SRC, OUT), (SAT_SRC, SAT_OUT))

    if args.check:
        stale = []
        for src, out in pairs:
            if not out.exists():
                stale.append(f"{out.name} missing")
                continue
            recorded = json.loads(out.read_text(encoding="utf-8")).get("source", {}).get("sha256")
            actual = source_sha256(src)
            if recorded != actual:
                stale.append(f"{src.name} changed (artifact {recorded[:12]}… ≠ source {actual[:12]}…)")
        if stale:
            print("STALE: " + "; ".join(stale) + "\n  fix: python3 snowflake-os/scripts/build.py",
                  file=sys.stderr)
            return 3
        print("FRESH: compiled artifacts match their YAML sources")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    spec = compile_spec()
    OUT.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sats = compile_satellites()
    SAT_OUT.write_text(json.dumps(sats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n_map = sum(len(c["courses"]) + len(c["exams"]) for c in spec["competencies"])
    quarantined = sum(1 for s in sats["satellites"] if not s.get("vendorable", True))
    print(
        f"compiled {SRC.name} -> {OUT}\n"
        f"  {len(spec['competencies'])} competencies · {len(spec['roles'])} roles · {n_map} mappings\n"
        f"compiled {SAT_SRC.name} -> {SAT_OUT}\n"
        f"  {len(sats['satellites'])} satellites · {quarantined} quarantined (licence)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
