# Designing the custom RBAC layer (the deliverable)

## The one-sentence architecture
An **identity** (OIDC/JWT from the IdP) hits a **Policy Enforcement Point** at the MLRun API and the
Nuclio gateway; the PEP asks a **Policy Decision Point** *"may role R do action A on resource
(project P, kind K)?"*; the PDP evaluates policy-as-data and returns allow/deny; deny-by-default.

## The policy model (data, single source of truth)
Model it as **data**, not scattered `if`s (the same discipline as an eval rubric — one source →
generate any contract). A minimal schema:
`role → [permission]`, `permission = {action ∈ (read, run, deploy, delete, admin), resource_kind ∈ (project, function, model, artifact, feature_set, nuclio_function), scope}`.
Bind subjects/groups → roles. Seed roles that replicate Iguazio: **viewer, developer, project-admin,
platform-admin**. Extend with attributes (data classification) for the ABAC stretch.

## The enforcement points (PEPs)
1. **MLRun API middleware** — an interceptor validating the JWT and calling the PDP before any
   project/function/model/artifact operation. This is the primary PEP; OSS MLRun's own checks are thin.
2. **Nuclio API gateway** — authorization at the function edge (invoke/deploy) [Nuclio gateway].
3. **Kubernetes RBAC** — the floor: ServiceAccounts + Roles/RoleBindings so the *platform components*
   have least privilege, and a namespace/project mapping so cluster ops respect tenancy [https://kubernetes.io/docs/reference/access-authn-authz/rbac/].
4. **UI** — the *last* place to enforce (never the only place); it reflects the API's decisions.

## The decision engine
Prefer **policy-as-data** — **OPA/Rego** or **Casbin** — so policy is externalized, versioned, and
**unit-testable**. Every rule ships with a test (an authZ eval-gate): a table of (subject, action,
resource) → expected allow/deny, run in CI. *No policy merges without its test.*

## Multi-tenancy / project scoping
Iguazio's value was **project isolation**: users see and act only within permitted projects. Encode
`scope` on every permission and map project → K8s namespace where cluster resources are involved, so
isolation holds at both the app and cluster layers.

## Auditability (the "extend" half)
Log every decision (who, action, resource, allow/deny, policy version) → an **audit trail**. This is
observed evidence of access, and the thing enterprises actually ask for beyond the vendor baseline.

## Related
Foundations: [[rbac-iam-foundations]]. Substrate: [[mlrun-nuclio-stack]]. How to de-risk and prove:
[[scoping-and-portfolio-proof]].
