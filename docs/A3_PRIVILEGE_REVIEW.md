# A3 privilege-path review

Status: read-only baseline and design prepared on 7 October 2026. No IAM,
bootstrap, access-key, MFA, or GitHub setting was changed.

## Verified scope

- AWS account: `954637862788`
- Region: `eu-west-1`
- Caller: `arn:aws:iam::954637862788:user/sazzad`
- Application stack: `PortfolioDev`
- Account stack: `AccountFoundation`
- Standard bootstrap stack: `CDKToolkit`

## Current effective path

```text
GitHub OIDC token for imsazzad.com:development
  -> PortfolioGitHubDevDeployRole
     -> cdk-hnb659fds-deploy-role-954637862788-eu-west-1
        -> iam:PassRole
           -> cdk-hnb659fds-cfn-exec-role-954637862788-eu-west-1
              -> AWS-managed AdministratorAccess
     -> shared file-publishing role (bootstrap S3 bucket)
     -> shared image-publishing role (bootstrap ECR repository)
     -> shared lookup role (AWS-managed ReadOnlyAccess, with KMS decrypt denied)
```

The GitHub entry role is narrowly trusted, but its effective deployment power
is not narrow. It can assume the standard deployment role. That role can
operate CloudFormation stacks with `Resource: "*"` and pass the administrator
CloudFormation execution role. A compromised trusted workflow could therefore
submit a template that acts outside `PortfolioDev`; limiting only the entry
role's direct permissions does not close this path.

## Live findings

### Bootstrap roles

- The CloudFormation execution role trusts only
  `cloudformation.amazonaws.com`, has no permissions boundary or inline
  policy, and has AWS-managed `AdministratorAccess` attached.
- `CDKToolkit` parameter `CloudFormationExecutionPolicies` is
  `arn:aws:iam::aws:policy/AdministratorAccess`.
- The bootstrap deployment role trusts this account root and has an inline
  policy that can create, update, execute, roll back, and delete CloudFormation
  stacks on `*`, and can pass the administrator execution role.
- The file-publishing role is scoped to the bootstrap asset bucket and its KMS
  key. The image-publishing role is scoped to the bootstrap ECR repository,
  except for the required account-wide `ecr:GetAuthorizationToken` action.
- The lookup role has AWS-managed `ReadOnlyAccess` and an explicit deny for
  `kms:Decrypt`. It is broad read access and should remain a conscious choice,
  even though this application currently synthesizes with lookups disabled.
- `CDKToolkit` has termination protection disabled and drift status
  `NOT_CHECKED`. Its lifecycle remains the standard `cdk bootstrap` lifecycle.

### Portfolio workload

The deployed `PortfolioDev` stack currently contains only:

- two named S3 buckets and their bucket policies;
- one CloudFront distribution, response-headers policy, origin access control,
  and CloudFront Function; and
- the named `portfolio-dev-monthly` budget.

IAM service-last-accessed evidence for the execution role shows authenticated
use of Budgets, CloudFormation, and CloudFront. Action-level history includes
`budgets:ModifyBudget` and CloudFront create, get, describe, publish, and update
operations. This history is evidence, not a complete policy specification:
rollback, deletion, replacement, and S3 lifecycle operations must also be
covered when applicable.

### Human administration

- User `sazzad` belongs to `AlexAccess`, `AIEngineerAccess`, and
  `ControlledAdminAccess`.
- `ControlledAdminAccess` has AWS-managed `AdministratorAccess`, so it is the
  current emergency administration path.
- IAM reports zero MFA devices for the user.
- The user has one active access key, created 10 September 2026. Its identifier
  and secret were not retrieved or recorded.
- `AIEngineerAccess` still has the inline
  `PortfolioCdkBootstrapOperator` policy. It grants `cloudformation:*`,
  `ecr:*`, `ssm:*`, and `s3:*` on `*`, plus bootstrap-role IAM mutation. Removing
  it would reduce redundant permissions but would not remove the user's
  effective administrator access while `ControlledAdminAccess` remains.

## Recommended target design

Do not narrow the shared bootstrap execution role first. Instead, create a
portfolio-specific CDK deployment path owned by `AccountFoundation`, while
continuing to use the standard bootstrap asset publishing infrastructure:

```text
PortfolioGitHubDevDeployRole
  -> PortfolioDevCdkDeployRole
     -> CloudFormation operations restricted to PortfolioDev
     -> iam:PassRole restricted to PortfolioDevCloudFormationExecutionRole
  -> existing file/image publishing roles
  -> lookup role only if a future reviewed lookup requires it

CloudFormation
  -> PortfolioDevCloudFormationExecutionRole
     -> S3 permissions for the two named portfolio buckets
     -> CloudFront permissions for the named portfolio resources
     -> Budgets permissions for portfolio-dev-monthly
```

The portfolio CDK app can select the dedicated roles through
`DefaultStackSynthesizer` role ARN properties. This avoids creating a competing
bootstrap stack and avoids changing the shared `CDKToolkit` execution policy
before every other consumer is known.

### Candidate execution-policy boundary

The exact policy must be generated and tested as a separate reviewable change.
Its intended boundary is:

| Service | Intended operations | Resource boundary |
| --- | --- | --- |
| S3 | Read and manage bucket configuration, lifecycle, versioning, encryption, ownership controls, public-access block, tags, and bucket policies; creation/deletion only where CloudFormation requires them | `portfolio-resume-site-954637862788-eu-west-1` and `portfolio-resume-access-logs-954637862788-eu-west-1`, including object ARNs only when required |
| CloudFront | Create/get/update/delete the distribution, function, origin access control, and response-headers policy; publish the function; manage tags | Existing named/physical portfolio resources; use `*` only for operations that do not support resource-level permissions, with account/request-tag conditions where supported |
| Budgets | `ModifyBudget`, `ViewBudget`, and required tag operations | `portfolio-dev-monthly` budget ARN where supported |

Do not add IAM, Lambda, API Gateway, DynamoDB, Bedrock, or other application
services until an approved `PortfolioDev` template actually requires them.
Every unavoidable wildcard must identify the unsupported resource-level action
and any compensating condition.

### Deployment-role boundary

`PortfolioDevCdkDeployRole` should:

- trust only `PortfolioGitHubDevDeployRole`;
- operate only `arn:aws:cloudformation:eu-west-1:954637862788:stack/PortfolioDev/*`,
  except for the minimum create-stack case if future recreation is explicitly
  approved;
- pass only `PortfolioDevCloudFormationExecutionRole`, conditioned on
  `iam:PassedToService = cloudformation.amazonaws.com`;
- read only the bootstrap version and required bootstrap asset objects; and
- have no direct application-service mutation permissions.

After migration, remove the standard bootstrap deployment role and
administrator execution role from the GitHub entry role's assumption/pass-role
paths. Keeping either path would preserve the escalation route.

## Alternative and tradeoff

The alternative is to replace `CDKToolkit`'s
`CloudFormationExecutionPolicies=AdministratorAccess` with a custom managed
policy. This has fewer roles, but it changes the shared bootstrap lifecycle and
can break every stack using the default qualifier. It also tends to accumulate
the union of permissions for unrelated applications. Do not select this option
until all bootstrap consumers are inventoried and the owner explicitly accepts
the shared boundary.

## Safe migration sequence

1. Inventory every current consumer of the default bootstrap deployment and
   execution roles.
2. Add the dedicated portfolio execution policy, execution role, and deployment
   role to `AccountFoundation`; use stable names and retention policies.
3. Use IAM policy simulation for the full create/update/delete/rollback action
   matrix before deployment.
4. Add the new role ARNs to the portfolio synthesizer and inspect its CDK diff
   and CloudFormation change set. Preserve the old path temporarily for
   rollback.
5. Run an explicitly authorized portfolio deployment using the dedicated path.
   Do not create chargeable resources solely as a permission test.
6. After successful deployment and recovery checks, remove the old bootstrap
   deploy/execution assumptions from `PortfolioGitHubDevDeployRole` in a
   separate change. Verify both the allowed path and expected denials.
7. Review removal of `PortfolioCdkBootstrapOperator`, MFA enrollment, and
   access-key replacement or retirement as separate owner-approved changes.

No step above is authorization to deploy or change IAM.

## References

- AWS CloudFormation service roles:
  https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-servicerole.html
- AWS least-privilege CloudFormation guidance:
  https://docs.aws.amazon.com/prescriptive-guidance/latest/least-privilege-cloudformation/service-roles-for-cloudformation.html
- AWS service authorization reference:
  https://docs.aws.amazon.com/service-authorization/latest/reference/
