# Project state

Last updated: 3 October 2026. Live AWS state was last verified on 2 October
2026.

This document records current evidence and decisions. It does not authorize a
deployment, import, deletion, credential change, policy change, bootstrap
change, or GitHub configuration change.

## A1 status

- A1 is complete locally; nothing was deployed or imported.
- Target AWS account: `954637862788`.
- Target region for this CDK app: `eu-west-1`.
- Local stack name: `AccountFoundation`.
- The A1 stack intentionally contains no resources.
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

## Live verification

Read-only AWS CLI queries on 2 October 2026 confirmed:

- Caller: `arn:aws:iam::954637862788:user/sazzad` in account `954637862788`.
- `eu-west-1` has `PortfolioDev` (`UPDATE_ROLLBACK_COMPLETE`) and `CDKToolkit`
  (`CREATE_COMPLETE`).
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
- The four budget names remain `AWS Monthly Cost Check`, `My Monthly Cost
  Budget`, `Zero-Spend check`, and `portfolio-dev-monthly`.

No drift detection was initiated. IAM policy documents, GitHub-side environment
configuration, budget notification details, and application resources were not
re-inventoried in A1; those checks belong to the relevant later stage before a
change is proposed.

## Ownership boundary

| Resource or lifecycle | Owner | A1 decision |
| --- | --- | --- |
| `AccountFoundation` CDK app and future explicitly approved account-level resources | This repository | In scope |
| GitHub OIDC provider and `PortfolioGitHubDevDeployRole` | Candidate for this repository | No adoption until A2 import review and explicit deployment approval |
| `PortfolioDev`, website resources, and `portfolio-dev-monthly` | `imsazzad/imsazzad.com` | Out of scope |
| `CDKToolkit` | Standard CDK bootstrap lifecycle | Document here; do not duplicate in a custom stack |
| Other budgets, IAM identities, service-linked roles, and AWS defaults | Existing or undetermined owners | Out of scope without an explicit ownership decision |
| Terraform-managed resources | Outside this repository | Excluded; no inspection, adoption, or removal |

## Required gates for A2

- Reconfirm caller identity and live configuration immediately before work.
- Verify current CloudFormation import support and import identifiers for every
  proposed resource type.
- Record complete policies, consumers, physical identifiers, and rollback path.
- Add exact template assertions before proposing an import.
- Review the CDK diff and CloudFormation import change set.
- Obtain explicit deployment authorization for account `954637862788` and the
  applicable region before any import or deployment.
