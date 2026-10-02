# Instructions for `imsazzad/aws-account-foundation`

## Mission and scope

Use Python AWS CDK to manage explicitly assigned account-level infrastructure
for account `954637862788`. Read `README.md`, `docs/FINDINGS.md`, and
`docs/IMPLEMENTATION_PLAN.md` before implementation. The findings are dated
evidence, not permanent truth: verify live state, account identity, and target
region before each adoption or deployment.

Start with the GitHub OIDC provider and `PortfolioGitHubDevDeployRole` only
after confirming import support and the exact current configuration. The
portfolio application, its `PortfolioDev` stack, website resources, and
`portfolio-dev-monthly` budget belong to `imsazzad/imsazzad.com`. The
`CDKToolkit` stack belongs to the standard CDK bootstrap lifecycle. The
`twin-terraform-*` resources are Terraform-owned. Do not absorb unrelated IAM
groups, users, budgets, service-linked roles, defaults, or other projects
without an explicit ownership decision.

## Before changing code or AWS

- Inspect `git status --short`, the relevant code and tests, the deployed
  CloudFormation stacks, and the live configuration of each proposed target.
- Confirm the caller identity is account `954637862788`. Use an explicit region
  for regional queries and deployments; the known portfolio region is
  `eu-west-1`. IAM, Budgets, and CloudFront have different scope semantics.
- Record the current physical ID, owner, trust policy, attached and inline
  policies, consumers, and rollback path for every existing resource proposed
  for adoption. Never infer ownership from a name or tag alone.
- Check current AWS CloudFormation import support for each resource type. An
  import or update can change a working permission path; prepare a reviewed
  change set and preserve stable physical names.
- Preserve user work and do not store secrets, access keys, tokens, or policy
  material containing credentials in source, logs, CI artifacts, or output.

## CDK design and verification

- Use focused constructs and deployment stacks. Keep account-level roles and
  provider configuration separate from application resource stacks.
- Make offline synth deterministic. Pin Python, CDK library and CLI versions,
  and dependencies. Put account/region selection at the app entrypoint.
- Use least privilege and document every wildcard action or resource. Review
  the full role chain, including assumed bootstrap roles and the CloudFormation
  execution role; scoping only the GitHub entry role is insufficient.
- Assert the exact intended GitHub OIDC audience and subject format against
  the live GitHub environment and current IAM trust before changing them.
- Add meaningful template assertions and run format, lint, type, test, and
  synth checks. Inspect `cdk diff` and the CloudFormation change set for
  replacement, removal, or broader IAM access before deployment.
- Treat resource adoption, role-policy changes, access-key changes, and
  bootstrap changes as separate reviewable slices. Record commands, results,
  owner decisions, and remaining risks in this repository's state document.

## Deployment control

Do not deploy, import, delete, rotate credentials, detach policies, or alter
GitHub settings merely because a plan lists those steps. A local agent needs an
explicit deployment request for the target account and region. Honor an
authorization already given for the same action and target. Before an
authorized deployment, verify caller identity and review the exact diff or
change set. Never create chargeable resources solely to test permissions.

For a consequential choice with two sound approaches, present both with
security, compatibility, and migration effects and let the owner select the
boundary before implementing it. Do not silently widen this repository's
ownership to satisfy a goal of "everything in CDK"; AWS-managed defaults and
GitHub-side settings have separate lifecycles.
