# A2 GitHub deployment IAM import plan

Status: prepared and locally verified on 7 October 2026. This plan is not
authorization to create a change set, import, deploy, delete, or modify AWS or
GitHub resources.

## Proposed ownership

Import exactly two existing physical resources into the new
`AccountFoundation` stack in account `954637862788`, region `eu-west-1`:

| Logical ID | CloudFormation type | Import identifier |
| --- | --- | --- |
| `GitHubOidcProvider` | `AWS::IAM::OIDCProvider` | `Arn=arn:aws:iam::954637862788:oidc-provider/token.actions.githubusercontent.com` |
| `PortfolioGitHubDevDeployRole` | `AWS::IAM::Role` | `RoleName=PortfolioGitHubDevDeployRole` |

The role owns its two existing inline policies through the role's `Policies`
property. Do not also import them as `AWS::IAM::RolePolicy`: Cloud Control
reports both policies in the normalized role model, so separate resources would
overlap ownership and could create drift or destructive update behavior.

Both resources use `DeletionPolicy: Retain` and
`UpdateReplacePolicy: Retain`. The provider URL and role name/path are
replacement-sensitive properties and must not change during adoption.

## Verified compatibility

- CloudFormation currently supports import and drift detection for the provider,
  role, and role-policy types.
- The provider template matches the live URL, STS audience, thumbprint, and
  empty tag set.
- The role template matches its physical name, path `/`, empty description,
  3,600-second maximum session duration, no tags, no attached managed policies,
  exact trust, and exact inline policies.
- The IAM trust matches GitHub's live immutable repository subject and the
  `development` environment.
- The GitHub environment variable points to the same role ARN, and the active
  deployment workflow consumes it through `aws-actions/configure-aws-credentials`.

## Security and compatibility observations

- Preserve-first adoption avoids changing the working permission path during
  import. Policy narrowing belongs to a later, separately reviewed change.
- `cloudformation:CreateStack` currently uses `Resource: "*"`. AWS cannot scope
  creation to an ARN for a stack that does not yet exist, but this combines with
  permission to pass the bootstrap CloudFormation execution role.
- The bootstrap execution role currently has `AdministratorAccess`; therefore,
  the effective deployment path is broader than the entry role's direct policy.
- CloudFront invalidation currently uses a distribution wildcard. Narrowing it
  to the current distribution would be a policy change, not an import-only
  operation.
- The GitHub `development` environment currently has no protection rules or
  deployment branch policy. The AWS trust is environment-scoped, so GitHub-side
  protection is an important separate control. On 7 October 2026, the owner
  accepted direct pushes to `main` and the current environment configuration
  for this personal account. Reassess that boundary before adding collaborators,
  production workloads, or broader permissions.
- The portfolio repository's documented branch subject and environment
  protections do not match live state and need correction in that repository.

## Required pre-import review

1. Start with a clean working tree and a reviewed commit containing only the A2
   import model and tests.
2. Reconfirm caller account `954637862788`, region `eu-west-1`, the two physical
   identifiers, trust, policies, tags, and GitHub OIDC/environment state.
3. Run all offline checks and strict synthesis.
4. Run `cdk diff` with `--change-set=false`; do not treat its additions for an
   unmanaged stack as proof that the import is safe.
5. Obtain explicit authorization to import into account `954637862788`, region
   `eu-west-1`.
6. Create and review the import change set without executing it. Confirm it
   contains only imports for the two logical IDs, with no creation, update,
   deletion, replacement, trust widening, or policy change.

The resource mapping for an authorized import is:

```json
{
  "GitHubOidcProvider": {
    "Arn": "arn:aws:iam::954637862788:oidc-provider/token.actions.githubusercontent.com"
  },
  "PortfolioGitHubDevDeployRole": {
    "RoleName": "PortfolioGitHubDevDeployRole"
  }
}
```

Do not run the import command from this document without satisfying the gates
above. The mapping must be passed to the pinned CDK CLI with lookups disabled.

## Post-import verification

1. Confirm both stack resources resolve to the original physical IDs and that
   no duplicate provider or role exists.
2. Re-read the IAM provider, role trust, attached policies, inline policies,
   tags, and Cloud Control models before any subsequent update.
3. Run CloudFormation drift detection and review every property.
4. Run the portfolio repository's current `development` deployment workflow
   through an explicitly authorized path and confirm OIDC assumption, CDK diff,
   deployment, static publishing, and invalidation all succeed.
5. Record the import change-set ID, stack events, drift result, workflow run ID,
   and remaining risks in `PROJECT_STATE.md`.

## Rollback

- Before import execution, cancel or delete the unexecuted change set; the IAM
  resources remain unmanaged and unchanged.
- If import execution fails, inspect stack events before taking action. Do not
  alter the live IAM resources to force a retry.
- If a successful import must be reversed, an authorized owner can delete the
  `AccountFoundation` stack. Both resources have `Retain`, so the physical
  provider and role should remain. Verify their existence, trust, policies, and
  workflow operation immediately afterward. Stack deletion is a separate
  destructive action and requires explicit authorization.
