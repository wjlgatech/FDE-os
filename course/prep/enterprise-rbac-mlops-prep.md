# Prep — Python Developer (RBAC on MLRun/Nuclio)

*Get ready to land and deliver this role. Knowledge graph + a leveled skills tree + the RBAC design
+ a portfolio build + interview prep. Grounded in the research vault
([`../../knowledge/vault/mlops-rbac-migration/`](../../knowledge/vault/mlops-rbac-migration/)) → knowledge graph
([`../../knowledge/mlops-rbac-migration-spine.html`](../../knowledge/mlops-rbac-migration-spine.html), 32 concepts /
35 edges via `knowledgefy`). JD: [`../target-jds/enterprise-rbac-mlops.md`](../target-jds/enterprise-rbac-mlops.md).*

## The role in one line
Replace a **sunset commercial vendor (Iguazio)** with its **open-source guts (MLRun + Nuclio)** and
rebuild the **access-control layer** you lose in the move — a **custom RBAC layer** you scope and
own end-to-end, in Python, on Kubernetes, delivered by Dec 2026.

## Knowledge map (own these cold — open the graph for the web of links)
- **The stack:** MLRun (MLOps orchestration: projects, functions, runs, models, artifacts, feature store) + Nuclio (serverless functions on K8s). What OSS gives you vs. what Iguazio's commercial layer added (project isolation, SSO, per-resource authZ) — the gap you fill.
- **RBAC/IAM:** authN vs authZ; the subject→role→permission(action×resource×scope) model; least privilege / deny-by-default; **OIDC/OAuth2/JWT** identity; **Kubernetes RBAC** (Role/ClusterRole/RoleBinding/ServiceAccount).
- **Enforcement:** PDP vs PEP; **policy-as-data** (OPA/Rego, Casbin) so policy is versioned + testable; ABAC as the "extend" stretch; audit trails.
- **The design:** identity → PEP at the MLRun API + Nuclio gateway → PDP over policy-as-data → deny-by-default, project-scoped, audited. (Full: [`custom-rbac-design`](../../knowledge/vault/mlops-rbac-migration/30-custom-rbac-design.md).)

## Skills tree (skillfy-style — level up each, with a drill)

| Skill | L1 (know) | L2 (do) | L3 (own) | Drill |
|---|---|---|---|---|
| **Backend + systems design** | REST/services, data modeling | design a service with a clean seam | design the PDP/PEP boundary + policy schema | sketch the RBAC layer's components + data flow on one page |
| **Python (production)** | idioms, typing | a tested FastAPI service + middleware | a policy-eval middleware with a test table | build an auth middleware from a blank page (coding-drill-kit habit) |
| **RBAC / IAM** | authN vs authZ, RBAC model | write roles/permissions as data | OIDC→roles mapping + deny-by-default + ABAC | encode the 4 seed roles + a (subject,action,resource)→allow/deny test table |
| **MLRun / Nuclio** | projects, functions, Nuclio-on-K8s | deploy a function; call the MLRun API | find where OSS auth ends and yours begins | stand up MLRun + Nuclio locally (minikube), deploy one function |
| **Kubernetes RBAC** | Role/Binding/ServiceAccount | write a namespaced Role + Binding | map project→namespace for tenant isolation | give a ServiceAccount least privilege for one task |
| **Policy-as-data** | why externalize policy | write OPA/Rego or Casbin rules | rules + CI test gate ("no policy without its test") | a Rego policy + a table test that fails on a wrong allow |
| **Own ambiguity** | ask the right Qs | produce a 1-page scope | name the smallest end-to-end win + risks | run the delta-discovery-protocol on this migration |

## The 2–4 week ramp (before/at start)
1. **Local stack:** MLRun + Nuclio on minikube; deploy one function; poke the MLRun API. Read where its auth begins/ends.
2. **Policy engine:** pick OPA/Rego or Casbin; encode `role→permission(action×resource_kind×scope)`; seed **viewer / developer / project-admin / platform-admin**.
3. **The vertical slice:** MLRun API **PEP middleware** validates a JWT → calls the **PDP** → *developer may `run` a `function` in `demo`; viewer may not* — with a **CI test table** proving both allow and deny. Deny-by-default.
4. **Extend outward:** more verbs/resources → Nuclio gateway edge → K8s namespace mapping → audit log.

## Portfolio proof — build the deliverable in miniature (observed > claimed)
Ship a **public `rbac-mlrun-demo`**: policy schema (data) + a PDP (OPA/Rego or Casbin) + a
FastAPI PEP middleware + the 4 seed roles + a **CI `(subject,action,resource)→allow/deny` test
table that fails loudly**. That single repo is the strongest possible signal for this role — it *is*
the deliverable, and it clears the evidence ladder: *a linked repo isn't proof; a passing authZ
eval-gate in CI is.* (Then run it through [portfolio-trust](https://portfolio-trust.vercel.app) and
get a **vouch** — the rung you can't self-issue.)

## Interview prep (likely questions → the strong answer)
- *"How would you rebuild the RBAC we lose leaving Iguazio?"* → the one-sentence architecture: identity (OIDC/JWT) → PEP at MLRun API + Nuclio gateway → PDP over policy-as-data → deny-by-default, project-scoped, audited. Name the smallest slice you'd ship week one.
- *"Where do you enforce?"* → every entry point, not the UI; API middleware is primary; K8s RBAC is the floor; UI reflects the API.
- *"Policy in code or data?"* → data (OPA/Casbin), versioned + unit-tested; no policy merges without its test.
- *"Multi-tenancy?"* → `scope` on every permission; project→namespace mapping so isolation holds at app + cluster layers.
- *"It's ambiguous — how do you start?"* → inventory Iguazio's actual behavior → 1-page scope → smallest end-to-end win → sequence + name the risks (IdP/claims mapping, double-auth with MLRun, per-request PDP latency→cache, policy drift).

## Honest gap check
Cross the JD against yourself: **backend/systems + Python** (strong), **RBAC/IAM + K8s** (study the map above + do the drills), **MLRun/Nuclio hands-on** (the JD's "comparable platforms" clause — the *local-stack drill + the demo repo* is how you convert "comparable" into "hands-on, here's the repo"). Owning-ambiguity is proven by the 1-page scope you bring unprompted.
