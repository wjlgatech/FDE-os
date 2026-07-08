# Owning the ambiguity — scoping + portfolio proof

## Scope it yourself (what the JD is really testing)
No one hands this to you in pieces. Run a discovery pass and produce a one-page scope before writing
code: (1) **inventory** what Iguazio's RBAC actually did (roles, project isolation, SSO) by watching
current behavior; (2) name the **smallest end-to-end slice** — one role, one action, one resource,
enforced at the MLRun API with a passing authZ test; (3) sequence outward (more verbs → more resource
kinds → Nuclio edge → K8s mapping → audit). Deny-by-default from day one.

## The smallest end-to-end win (ship this first)
`developer` may `run` a `function` in project `demo`, and `viewer` may not. Enforced at an MLRun API
middleware calling an OPA/Casbin PDP, with a policy-as-data file and a test table proving both the
allow and the deny. That single vertical slice de-risks the whole design and is demoable in week one.

## Portfolio proof (make the capability observed, not claimed)
Build a **minimal RBAC-on-MLRun/Nuclio demo** as a public artifact: a policy schema, a PDP
(OPA/Rego or Casbin), a FastAPI-style PEP middleware, a seed of the four roles, and a **CI test
table** of (subject, action, resource) → allow/deny that fails loudly. That is the exact deliverable
in miniature — the strongest possible signal for this role, and it maps to the evidence ladder:
*a repo isn't proof; a passing authZ eval-gate in CI is.*

## Risks to name early (senior signal)
Token/identity source (which IdP? OIDC claims → roles mapping), where MLRun's own auth ends and
yours begins (avoid double or conflicting checks), performance of a per-request PDP call (cache
decisions), and policy drift (tests + versioned policy). Surfacing these unprompted is the
"comfortable owning ambiguous problems" the JD screens for.

## Related
Design: [[custom-rbac-design]]. The engagement: [[domain-map]].
