# The engagement — migrate off Iguazio, rebuild RBAC on OSS

## The migration
The client runs an ML platform on **Iguazio**, a commercial MLOps platform whose offering is being
sunset (Iguazio was acquired by McKinsey). The platform is being rebuilt on the **open-source
components Iguazio was built on — MLRun and Nuclio** [https://www.iguazio.com/questions/iguazio-vs-mlrun-vs-nuclio-whats-the-difference/].

## The core problem — the lost access-control layer
Iguazio's *commercial* platform provided the enterprise access-control layer: project-scoped
permissions, SSO, multi-tenancy, and per-resource authorization on top of MLRun/Nuclio. Moving to
the raw open-source stack **loses that layer**. The engagement is to **design and implement a custom
RBAC layer** on MLRun + Nuclio that **replicates and extends** those capabilities.

## What "done" means
A working authorization layer where an authenticated identity's **role** determines which
**actions** (run, read, deploy, delete) it may take on which **resources** (projects, functions,
models, artifacts, Nuclio functions) — enforced at every entry point, not just the UI.

## Why it's ambiguous (and why they want an owner)
There is no vendor spec for "the RBAC we lost" — you reconstruct the requirement from how Iguazio
behaved, decide the policy model, choose enforcement points, and sequence delivery. The JD says it
plainly: *own ambiguous problems; scope your own work.* [the JD]

## Related
The [[custom-rbac-design]] reconstructs the layer; [[rbac-iam-foundations]] is the vocabulary;
[[mlrun-nuclio-stack]] is the substrate; [[scoping-and-portfolio-proof]] is how to de-risk it.
