#!/usr/bin/env python3
"""pdp.py — the Policy Decision Point.

Answers one question: *may this subject take this action on this resource in this project?*
Policy is DATA (policy.json), not scattered ``if``s, so it's versioned, auditable, and unit-tested.
**Deny-by-default**: anything the policy doesn't explicitly grant is denied.

A subject carries **grants** — (role, project) bindings, e.g. developer on project "demo". A grant's
project may be "*" (cluster-wide, e.g. platform-admin). A permission's ``scope`` of "*" means the
role is cluster-wide regardless of the binding. Otherwise the grant's project must equal the
requested project — that's the multi-tenant isolation Iguazio gave us and we're rebuilding.

Pure + stdlib. The PEP (pep.py) calls ``decide``; the whole thing is offline-testable.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

_HERE = os.path.dirname(os.path.abspath(__file__))
_POLICY_PATH = os.path.join(_HERE, "policy.json")


def load_policy(path: str | None = None) -> dict:
    with open(path or _POLICY_PATH, encoding="utf-8") as f:
        return json.load(f)


@dataclass
class Decision:
    allow: bool
    reason: str
    matched: str | None = None      # "role@project via <perm>" when allowed
    policy_version: str = ""


def _matches(pattern: str, value: str) -> bool:
    return pattern == "*" or pattern == value


def decide(policy: dict, subject: dict, action: str, resource: str, project: str) -> Decision:
    """subject = {"sub": str, "grants": [{"role": str, "project": str}]}."""
    pv = policy.get("policy_version", "")
    roles = policy.get("roles", {})
    for grant in subject.get("grants", []):
        role, gproject = grant.get("role"), grant.get("project")
        perms = roles.get(role)
        if perms is None:
            continue  # unknown role → contributes nothing (deny-by-default)
        for p in perms:
            if not (_matches(p.get("action", ""), action) and _matches(p.get("resource", ""), resource)):
                continue
            # scope: cluster-wide permission, or cluster-wide grant, or same-project grant
            if p.get("scope") == "*" or gproject == "*" or gproject == project:
                return Decision(True, "granted", f"{role}@{gproject} via {p.get('action')}:{p.get('resource')}", pv)
    return Decision(False, "deny-by-default: no grant permits this", None, pv)


if __name__ == "__main__":  # tiny CLI: pdp.py <role@project> <action> <resource> <project>
    import sys
    role_proj, action, resource, project = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    role, _, gp = role_proj.partition("@")
    subj = {"sub": "cli", "grants": [{"role": role, "project": gp or "*"}]}
    d = decide(load_policy(), subj, action, resource, project)
    print(("ALLOW" if d.allow else "DENY") + f" — {d.reason}" + (f" ({d.matched})" if d.matched else ""))
    raise SystemExit(0 if d.allow else 3)
