# Staged work for the new repository

This is an adoption plan, not authorization to deploy. Complete one slice at
a time, preserve the live deployment path, and record exact evidence in a
`PROJECT_STATE.md` created in the new repository.

## A1 — Establish the repository and repeat the inventory

- Create the Python CDK project described in `README.md`; add locked
  dependencies, deterministic offline synthesis, checks, and a state file.
- Confirm `aws sts get-caller-identity` reports account `954637862788`.
  Inventory CloudFormation, IAM, budgets, and the regional resources relevant
  to proposed ownership. Compare with `FINDINGS.md`, noting changes since
  2 October 2026. Inventory other enabled regions before claiming account-wide
  completeness.
- Draw an ownership table: this repo, portfolio repo, `CDKToolkit`, Terraform,
  other owner, and AWS service-managed. Get an explicit decision for ambiguous
  resources.
- Exit: the repo checks pass offline and the owner has approved the initial
  ownership list. No AWS deployment is needed for A1.

## A2 — Adopt GitHub deployment IAM safely

- Read the live OIDC provider configuration, role trust, inline policies,
  tags, consumers, and GitHub environment/subject format. Preserve the
  `PortfolioGitHubDevDeployRole` physical name and working OIDC claim match.
- Verify current CloudFormation import support and the required import
  identifiers for `AWS::IAM::OIDCProvider`, `AWS::IAM::Role`, and any separate
  policy resources. Choose a supported import design; if a policy or provider
  cannot be imported safely, document that exception instead of creating a
  duplicate. An `AWS::IAM::Policy` or `AWS::IAM::RolePolicy` representation
  needs separate compatibility review before replacing live inline policies.
- Add template assertions for the audience, exact subject constraint, role
  name, and permission scope. Review `cdk diff` and the proposed CloudFormation
  import change set for any role replacement, trust widening, policy removal,
  or IAM privilege increase. Plan a rollback that keeps the portfolio workflow
  operational.
- If the new repository later deploys through GitHub Actions, establish a
  separate role trusted only for that repository and its protected environment.
  Bootstrap this trust through the authorized administrative path; do not let
  the portfolio deployment role administer its own replacement.
- Exit: after an explicit deployment request, the existing physical provider
  and role are owned by this stack where supported, a real portfolio
  `development` workflow succeeds, and no duplicate provider/role appears.

## A3 — Review privilege paths and bootstrap policy

- Map the GitHub role to CDK deploy/publishing roles and the CloudFormation
  execution role. The latter currently has `AdministratorAccess`. Design a
  narrower execution policy and test its required CDK operations before any
  bootstrap update. Keep this as a separate, owner-reviewed change because it
  can break all CDK deployments.
- Review the `PortfolioCdkBootstrapOperator` policy still on
  `AIEngineerAccess`, the `ControlledAdminAccess` membership, the active human
  access key, and IAM MFA state. Confirm other workloads and an emergency
  administration path. Propose least-privilege/federated access and MFA, then
  make each approved change independently with verification.
- Exit: effective privilege paths and explicit decisions are documented;
  any approved removal or narrowing has been verified with the required
  deployment and recovery checks.

## A4 — Coordinate portfolio budget reconciliation

The `portfolio-dev-monthly` budget belongs to the portfolio repository. Open
a separate task there to reconcile its live notifications with the deployed
template. Preserve the alert subscriber and coverage during the migration.
Do not move or recreate the budget from this account repository. Review
CloudFormation's notification replacement behavior and the earlier failed
update before proposing a change.

## Ongoing rules

- `CDKToolkit` upgrades use the documented `cdk bootstrap` process under an
  authorized administrator session; inspect its change set and execution-role
  policy first. Do not create a custom competing bootstrap stack.
- Service-linked roles, AWS defaults, GitHub environment settings, and
  Terraform-owned resources retain their own lifecycles unless their owners
  explicitly transfer them.
- Do not add production, Bedrock, application backends, new budgets, or other
  resources solely to make the account appear fully CDK-managed.
