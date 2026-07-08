# RBAC & IAM foundations (the vocabulary you must own)

## Authentication vs authorization
**Authentication (authN)** answers *who are you* — establish identity (token, SSO). **Authorization
(authZ)** answers *what are you allowed to do* — decide if that identity may perform an action on a
resource [https://kubernetes.io/docs/reference/access-authn-authz/authorization/]. RBAC is an authZ
model; identity comes from an IdP.

## RBAC core model
**Role-Based Access Control** binds **subjects** (users/groups/service accounts) → **roles** → a set
of **permissions**, where a permission is an **action** (verb) on a **resource** (object), optionally
**scoped** (namespace / project / tenant). Keep roles few and composable; prefer *deny-by-default*
and least privilege [https://kubernetes.io/docs/concepts/security/rbac-good-practices/].

## Kubernetes RBAC (the primitive under Nuclio/MLRun)
K8s RBAC uses the `rbac.authorization.k8s.io` API with four objects: **Role** and **ClusterRole**
(permission sets, namespaced vs cluster-wide) and **RoleBinding** / **ClusterRoleBinding** (bind a
subject to a role) [https://kubernetes.io/docs/reference/access-authn-authz/rbac/]. Verbs
(get/list/create/update/delete) on resources; bound to users, groups, or **ServiceAccounts**.

## Identity: OIDC / OAuth2 / SSO
Enterprise identity flows through an **IdP** via **OIDC** (OpenID Connect on OAuth2): the user
authenticates once, receives a signed **JWT** carrying claims (subject, groups/roles), and services
validate it. K8s can authenticate users via an OIDC provider; your custom layer should accept the
same tokens so identity is consistent across UI, MLRun API, and Nuclio.

## Enforcement patterns (where the check happens)
- **Policy Decision Point (PDP)** vs **Policy Enforcement Point (PEP)**: decide centrally, enforce at
  each entry. A middleware/interceptor at the MLRun API is a PEP calling a PDP.
- **Policy-as-data engines**: Open Policy Agent (**OPA**) / Rego, or Casbin — externalize policy so
  it's testable and auditable (the eval-as-gate instinct, applied to authZ).
- **ABAC** as an extension: attributes (project sensitivity, data classification) refine role
  decisions — the "extend what we're losing" half of the JD.

## Related
The concrete design that assembles these into a layer for MLRun/Nuclio: [[custom-rbac-design]].
