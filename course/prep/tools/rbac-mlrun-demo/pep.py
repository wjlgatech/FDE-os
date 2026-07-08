#!/usr/bin/env python3
"""pep.py — the Policy Enforcement Point.

Framework-agnostic middleware that sits in front of the MLRun API / Nuclio gateway: it takes an
identity + the requested (action, resource, project), asks the PDP, and allows or blocks — logging
every decision to an audit trail. In production the identity is a **verified OIDC/JWT** (validated
against the IdP's JWKS); here we decode a demo claims token (base64 JSON) and DO NOT verify the
signature — that's the one seam you'd wire to real OIDC. Everything else is production-shaped.

`enforce()` is a pure function (testable offline). `PEPHandler` shows the same logic wired into a
stdlib http.server so you can curl it — no third-party web framework required.
"""
from __future__ import annotations

import base64
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import pdp

AUDIT: list[dict] = []


def parse_claims(token: str) -> dict:
    """Demo token = base64url(JSON claims). PROD: verify a JWT signature (OIDC/JWKS) first."""
    try:
        pad = "=" * (-len(token) % 4)
        return json.loads(base64.urlsafe_b64decode(token + pad).decode("utf-8"))
    except Exception:
        return {}


def _subject_from_claims(claims: dict) -> dict:
    """Map IdP claims → an authZ subject. Accept explicit grants, or map groups → (role, project)
    of the form 'role:project' (how an IdP would hand you group memberships)."""
    if claims.get("grants"):
        return {"sub": claims.get("sub", "anon"), "grants": claims["grants"]}
    grants = []
    for g in claims.get("groups", []):
        role, _, proj = str(g).partition(":")
        grants.append({"role": role, "project": proj or "*"})
    return {"sub": claims.get("sub", "anon"), "grants": grants}


def enforce(policy: dict, claims: dict, action: str, resource: str, project: str) -> dict:
    """The enforcement call. Returns {allow, status, reason, audit}. Deny-by-default via the PDP."""
    subject = _subject_from_claims(claims)
    d = pdp.decide(policy, subject, action, resource, project)
    entry = {
        "sub": subject.get("sub"), "action": action, "resource": resource, "project": project,
        "decision": "allow" if d.allow else "deny", "reason": d.reason,
        "matched": d.matched, "policy_version": d.policy_version,
    }
    AUDIT.append(entry)
    return {"allow": d.allow, "status": 200 if d.allow else 403, "reason": d.reason, "audit": entry}


class PEPHandler(BaseHTTPRequestHandler):  # pragma: no cover - the live http demo
    """GET /<resource>?action=..&project=..  with  Authorization: Bearer <base64 claims>."""
    policy = None

    def do_GET(self):
        if PEPHandler.policy is None:
            PEPHandler.policy = pdp.load_policy()
        u = urlparse(self.path)
        resource = u.path.strip("/") or "project"
        q = parse_qs(u.query)
        action = (q.get("action") or ["read"])[0]
        project = (q.get("project") or ["demo"])[0]
        auth = self.headers.get("Authorization", "")
        token = auth[7:] if auth.lower().startswith("bearer ") else ""
        res = enforce(PEPHandler.policy, parse_claims(token), action, resource, project)
        body = json.dumps(res).encode()
        self.send_response(res["status"])
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # quiet
        pass


def serve(port: int = 8099):  # pragma: no cover
    print(f"PEP demo on http://localhost:{port}  (try: curl with Authorization: Bearer <base64 claims>)")
    HTTPServer(("", port), PEPHandler).serve_forever()


if __name__ == "__main__":  # pragma: no cover
    serve()
