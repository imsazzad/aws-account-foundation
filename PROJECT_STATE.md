# Project state

Last updated: 7 October 2026. Live AWS and GitHub state was last verified on
7 October 2026.

This document records current evidence and decisions. It does not authorize a
deployment, import, deletion, credential change, policy change, bootstrap
change, or GitHub configuration change.

## A1 status

- A1 is complete locally; nothing was deployed or imported.
- Target AWS account: `954637862788`.
- Target region for this CDK app: `eu-west-1`.
- Local stack name: `AccountFoundation`.
- The A1 commit contained no resources. The current A2 template contains the
  two IAM resources imported into `AccountFoundation` on 7 October 2026.
- Terraform is outside this repository and was not inspected or changed during
  A1. Removal of Terraform-managed resources is not part of this plan.
- The owner directed this repository to remain CDK-only and approved excluding
  Terraform from its ownership boundary.

Local verification on 3 October 2026 passed:

- The `uv` lockfile is current and resolves 26 packages.
- Ruff formatting and lint checks pass.
- Strict mypy checking passes for all six Python source files.
- The unit test passes and confirms the explicit account, region, stack name,
  termination protection, and empty A1 template.
- Strict CDK CLI synthesis passes offline without credentials or context
  lookups.

The pinned CDK CLI reports that optional feature flags are not explicitly
configured. Exact library and CLI pins make current synthesis repeatable; the
flags must be reviewed when either CDK version is upgraded.

## A2 adoption status

A2 is implemented, imported, and verified. The owner explicitly authorized the
import into account `954637862788` in `eu-west-1` on 7 October 2026.

- Change set `a2-import-20261007` was created with `--no-execute` and reviewed
  before execution. Its ARN is
  `arn:aws:cloudformation:eu-west-1:954637862788:changeSet/a2-import-20261007/090a4cb7-8381-4680-9e14-284ec955534c`.
- The reviewed change set contained exactly two `Import` actions:
  `GitHubOidcProvider` and `PortfolioGitHubDevDeployRole`. It contained no
  update, replacement, or deletion action.
- `AccountFoundation` reached `IMPORT_COMPLETE` at
  `2026-10-07T21:22:31.966000+00:00`. Termination protection is enabled.
- The imported physical IDs are the existing provider ARN and role name; no
  replacement resource was created.
- Drift detection ID `682e81b0-c295-11f1-83a2-0205504497d1` completed at
  `2026-10-07T21:23:57.899000+00:00` with stack status `IN_SYNC` and zero
  drifted resources.
- Post-import IAM reads confirmed that the provider configuration, role trust,
  role ID, inline-policy inventory, and lack of attached managed policies were
  preserved. The import itself changed no GitHub setting or application stack.
- A post-import `cdk diff --change-set=false` reported no resource or IAM
  differences. It reported only the standard CDK `BootstrapVersion` SSM
  parameter, marked `[cdk:skip]`, which CDK omits from the resource-import
  template. A prepared ordinary deployment change set
  `a2-bootstrap-baseline-20261007` failed as empty because CloudFormation
  received no deployable change. No baseline update remains pending.
- Portfolio workflow run `37694036430` succeeded from `main` commit `a565c5b`
  after the import. It verified AWS identity, completed CDK diff and deploy,
  published the static artifact, invalidated CloudFront, and uploaded the
  release manifest. This satisfies the final A2 operational gate.

- The template models `AWS::IAM::OIDCProvider` and `AWS::IAM::Role` with stable
  logical IDs, exact live properties, and both deletion and replacement set to
  `Retain`.
- The two existing inline policies are embedded in `AWS::IAM::Role`, matching
  Cloud Control's normalized role model. No overlapping
  `AWS::IAM::RolePolicy` resource is defined.
- CloudFormation's current resource support matrix reports import and drift
  support for `AWS::IAM::OIDCProvider`, `AWS::IAM::Role`, and
  `AWS::IAM::RolePolicy`.
- Registry identifiers are provider `Arn`, role `RoleName`, and the composite
  `PolicyName` plus `RoleName` for a separate role-policy resource.
- Strict synthesis, formatting, linting, mypy, and three template tests pass.
- Before import, a template-only `cdk diff` ran with `--change-set=false`.
  Because the stack did not yet exist, it correctly reported the two resources
  and their existing IAM permissions as additions; it could not by itself prove
  import equivalence.
- The executed import procedure, review gates, and rollback path are in
  `docs/A2_IMPORT_PLAN.md`.

An attempted CDK `--record-resource-mapping` run was canceled at the first
identifier prompt, before any identifier or import was submitted. Contrary to
the help text's implication that the mode performs no import operation, its
preparation step uploaded this encrypted template object to the existing CDK
asset bucket:

- Bucket: `cdk-hnb659fds-assets-954637862788-eu-west-1`
- Key: `26901c44f17ef74cbe404e49393d4d7fc597f3044fe926ffae295d5b0fc4bb6e.json`
- Version ID: `b27TLVQxhbJaaoL7ay.7fGRrwahMdCel`
- Uploaded: `2026-10-07T20:54:53Z`; size: 5,304 bytes; KMS encrypted

Post-cancellation checks at that time confirmed that `AccountFoundation` did
not exist and no stack was in an import or review state. The later authorized
import created the stack. The object has not been deleted; cleanup requires an
explicit owner decision.

## Live verification

Read-only AWS CLI queries refreshed on 7 October 2026 confirmed:

- Caller: `arn:aws:iam::954637862788:user/sazzad` in account `954637862788`.
- `eu-west-1` has `PortfolioDev` (`UPDATE_COMPLETE`) and `CDKToolkit`
  (`CREATE_COMPLETE`). After the authorized import, it also has
  `AccountFoundation` (`IMPORT_COMPLETE`).
- No active CloudFormation stacks were returned in the other 16 enabled
  regions, including `us-east-1`.
- IAM has one GitHub OIDC provider for `token.actions.githubusercontent.com`,
  audience `sts.amazonaws.com`, with no tags.
- `PortfolioGitHubDevDeployRole` exists with path `/`, maximum session duration
  3,600 seconds, no tags, and no attached managed policies.
- The role has two inline policies: `PortfolioCdkRoleAssumption` and
  `PortfolioGitHubDevDeployRolePolicy`.
- Its trust remains restricted to audience `sts.amazonaws.com` and subject
  `repo:imsazzad@9584472/imsazzad.com@1370652664:environment:development`.
- The live provider thumbprint is
  `1b511abead59c6ce207077c0bf0e0043b1382612`.
- Cloud Control returns the provider URL normalized as
  `https://token.actions.githubusercontent.com` and returns both inline
  policies as properties of the role.

Post-import drift detection completed with `AccountFoundation` `IN_SYNC` and
zero drifted resources. Application resources and budget notification details
were not re-inventoried because they remain outside A2.

Read-only GitHub queries confirmed:

- `imsazzad/imsazzad.com` is private, repository ID `1370652664`, with default
  branch `main`.
- Its OIDC configuration uses the immutable subject prefix
  `repo:imsazzad@9584472/imsazzad.com@1370652664` and the live IAM trust adds
  `:environment:development`.
- The `development` environment has no protection rules and no deployment
  branch policy. On 7 October 2026, the owner explicitly accepted direct pushes
  to `main` and the current environment configuration for now because this is a
  personal account. Revisit this decision if collaborators, production
  workloads, or a broader deployment scope are introduced.
- The environment variable `AWS_DEV_DEPLOY_ROLE_ARN` points to the live role.
- The active deployment workflow requests `id-token: write`, uses the
  `development` environment, and currently triggers on pushes to `main` or
  manual dispatch.
- The portfolio repository's trust-policy JSON and bootstrap runbook were
  corrected in commit `56a26f6` to record the immutable environment subject,
  current environment controls, and account-foundation ownership.
- The post-import deployment-role consumer baseline is successful workflow run
  `37694036430` on 7 October 2026 from `main` commit `a565c5b`.

## Ownership boundary

| Resource or lifecycle | Owner | Ownership decision |
| --- | --- | --- |
| `AccountFoundation` CDK app and future explicitly approved account-level resources | This repository | In scope |
| GitHub OIDC provider and `PortfolioGitHubDevDeployRole` | This repository | Adopted into `AccountFoundation` by the authorized A2 import on 7 October 2026 |
| `PortfolioDev`, website resources, and `portfolio-dev-monthly` | `imsazzad/imsazzad.com` | Out of scope |
| `CDKToolkit` | Standard CDK bootstrap lifecycle | Document here; do not duplicate in a custom stack |
| Other budgets, IAM identities, service-linked roles, and AWS defaults | Existing or undetermined owners | Out of scope without an explicit ownership decision |
| Terraform-managed resources | Outside this repository | Excluded; no inspection, adoption, or removal |

## Completed gates for A2

- Caller identity and live configuration were reconfirmed immediately before
  import.
- CloudFormation import support and identifiers were verified for both resource
  types.
- Complete policies, consumers, physical identifiers, and rollback path were
  recorded before import.
- Exact template assertions and all local quality gates passed.
- The CDK diff and unexecuted CloudFormation import change set were reviewed.
- The owner explicitly authorized the import into account `954637862788` and
  region `eu-west-1`.
- A real post-import portfolio deployment succeeded through the imported role,
  and the related stale portfolio documentation was corrected.
