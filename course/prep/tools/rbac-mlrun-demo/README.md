# rbac-mlrun-demo — a custom RBAC layer for MLRun/Nuclio, in miniature

The **working proof** for the [RBAC-on-MLRun/Nuclio prep](../../prep/enterprise-rbac-mlops-prep.md):
the deliverable (replace a commercial platform's lost access control with a custom layer on the
open-source stack) built as the smallest real, tested slice. Policy-as-data, deny-by-default,
project-scoped — and it **passes its own eval-gate**.

**▶ Try it live (no clone):** [`wjlgatech.github.io/FDE-os/rbac-demo.html`](https://wjlgatech.github.io/FDE-os/rbac-demo.html) — same policy.json, client-side.

## The pieces (the architecture, runnable)
- **`policy.json`** — policy as **data**: the four seed roles (`viewer`, `developer`,
  `project-admin`, `platform-admin`) → permissions (`action × resource × scope`). Single source of
  truth; extend by editing data, not code.
- **`pdp.py`** — the **Policy Decision Point**: *may this subject do this action on this resource in
  this project?* Deny-by-default; multi-tenant scope (a grant's project must match, unless the role
  is cluster-wide).
- **`pep.py`** — the **Policy Enforcement Point**: identity (OIDC/JWT claims → roles) → PDP → allow
  or 403, **audited** (who / action / resource / decision / policy_version). Framework-agnostic
  `enforce()` + a stdlib `http.server` you can curl (the MLRun-API/Nuclio-gateway seam).

## Run it
```bash
# one decision from the CLI
python3 pdp.py developer@demo run function demo      # ALLOW
python3 pdp.py viewer@demo    run function demo      # DENY (deny-by-default)

# the enforcement point over HTTP
python3 pep.py                                        # serves on :8099
TOK=$(python3 -c "import base64,json;print(base64.urlsafe_b64encode(json.dumps({'sub':'alice','groups':['developer:demo']}).encode()).decode().rstrip('='))")
curl "http://localhost:8099/function?action=run&project=demo" -H "Authorization: Bearer $TOK"   # 200 allow
curl "http://localhost:8099/model?action=delete&project=demo" -H "Authorization: Bearer $TOK"   # 403 deny
```

## The eval-gate (why this is *proof*, not a claim)
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
A **(subject, action, resource, project) → allow/deny table** (14 cases) + deny-by-default
properties + the PEP allow/deny/audit path. The article's line — *"a working proof that actually ran
and passed its own test"* — **is this.** No policy change merges without the table going green.

## How it maps to the real engagement
- **MLRun API**: `pep.enforce()` is the middleware you drop in front of project/function/model/
  artifact operations (the primary enforcement point).
- **Nuclio gateway**: the same `enforce()` at the function edge (invoke/deploy).
- **Kubernetes RBAC**: the floor — ServiceAccounts + Roles; map project → namespace for isolation.
- **Identity**: `parse_claims` decodes demo claims; in production, verify a JWT against the IdP's
  JWKS (OIDC) *before* trusting the roles. That swap is the one seam left to production-harden.

_Pure stdlib, offline. Anonymized/demo data only. Extend the policy in `policy.json`; the gate keeps you honest._
