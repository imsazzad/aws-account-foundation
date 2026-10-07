# Account infrastructure repository handoff

Repository name: **`imsazzad/aws-account-foundation`**. The name
describes my personal AWS account setup and keeps it distinct from any
application infrastructure.

The `docs/` folder contains `FINDINGS.md` and `IMPLEMENTATION_PLAN.md`, the
initial inventory and work plan. `PROJECT_STATE.md` records the latest verified
state and decisions.

Start with [FINDINGS.md](docs/FINDINGS.md), then follow
[IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md). The observations are a
snapshot from 2 October 2026 and must be rechecked before changing AWS.

## Intended ownership

This repository should own shared or administrative infrastructure for AWS
account `954637862788`. Its `AccountFoundation` stack owns the existing GitHub
OIDC provider and portfolio GitHub deployment role and policies. It may later
own other explicitly approved account-level resources. It must not take
ownership of any application stack, the Terraform state resources, or
service-managed defaults simply because they appear in an account inventory.

The existing `CDKToolkit` stack is managed by the standard `cdk bootstrap`
process. Keep its lifecycle documented here but do not define a second copy of
its resources in a custom stack. The portfolio `PortfolioDev` stack and its
budget remain in `imsazzad/imsazzad.com`.

## Establish the new repository

1. Create the private `imsazzad/aws-account-foundation` repository, keep
   `AGENTS.md` and `README.md` at its root, and keep the findings and plan under
   `docs/`. Protect its default branch before configuring CI trust. Do not copy
   AWS credential files, local CDK output, or generated cloud assembly files.
2. Initialize a Python 3.14 project with `uv`, Python CDK v2 (`aws-cdk-lib`),
   `constructs`, a pinned CDK CLI, a lockfile, and a `.gitignore` for `.venv/`,
   `cdk.out/`, caches, and local credential or output files. Use versions tested
   together in this new repository; the portfolio repository is a reference,
   not a dependency.
3. Create a small CDK app with explicit account and region configuration.
   Synthesis should work without AWS credentials or live context lookups.
   Add template assertions for OIDC audience, trust subject, role name, policy
   scope, and retention/protection settings where applicable.
4. Re-inventory AWS, confirm the owner of each target, and follow the import
   gates in `IMPLEMENTATION_PLAN.md`. A successful local synth is not evidence
   that a live resource has been adopted.
5. Add CI for lint, type checking, tests, and offline synthesis first. Add an
   AWS deployment workflow only after its OIDC trust, permission path, and
   protected environment are reviewed. The new repository needs its own
   deployment trust and role; the existing portfolio role must not be reused
   merely because it can deploy CDK. Never place long-lived AWS keys in CI.

## Local verification

Install the locked Python and Node dependencies, then run the same checks as CI:

```shell
uv sync --frozen --all-groups
npm ci
uv run --frozen ruff format --check .
uv run --frozen ruff check .
uv run --frozen mypy .
uv run --frozen pytest
npm run synth
```

Synthesis uses the explicit account `954637862788` and region `eu-west-1`. It
does not use AWS credentials or live context lookups. The A2 template models
the GitHub OIDC provider and portfolio deployment role imported into
`AccountFoundation` on 7 October 2026. See
[A2_IMPORT_PLAN.md](docs/A2_IMPORT_PLAN.md) for the completed import record and
rollback procedure.
