# The MLRun + Nuclio stack (the substrate you're securing)

## MLRun — the MLOps orchestration framework
**MLRun** is an open-source AI/MLOps orchestration framework for building and managing ML and
generative-AI applications across their lifecycle: projects, functions, runs, pipelines, artifacts,
models, and a feature store [https://github.com/mlrun/mlrun]. It exposes an **API service**
(`mlrun-api` / httpdb) and a Python SDK; work is organized under **projects** — the natural unit to
scope access around.

## Nuclio — the serverless function engine
**Nuclio** is a high-performance open-source serverless platform; MLRun deploys real-time and
serving functions as **Nuclio functions** [https://docs.mlrun.org/en/v1.10.0/concepts/nuclio-real-time-functions.html].
Nuclio runs on Kubernetes: its resources live in a `nuclio` namespace and it ships a
`nuclio-rbac.yaml` that creates the K8s RBAC roles Nuclio needs to operate [https://nuclio.io/docs/latest/setup/minikube/getting-started-minikube/].
Nuclio API gateways can carry authorization at the function edge.

## The access-control gap in the OSS stack
Kubernetes RBAC (below) governs *cluster* operations, and Nuclio/MLRun components use it to run. But
**application-level authorization** — "user U with role R may run functions in project P but only
read models in project Q" — is exactly what the Iguazio commercial layer added and what OSS MLRun
does not fully provide. The custom layer lives **at the MLRun API and Nuclio gateway**, mapping an
identity to permitted actions on MLRun/Nuclio resources. See [[custom-rbac-design]].

## Deployment reality
Everything runs on **Kubernetes**; MLRun and Nuclio are Helm-deployed services. Familiarity with K8s
(namespaces, service accounts, RBAC objects, admission) is the "plus" in the JD and the medium your
enforcement lives in. See [[rbac-iam-foundations]].
