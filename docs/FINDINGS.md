# AWS infrastructure ownership findings

Snapshot: 2 October 2026. Account `954637862788`; caller
`arn:aws:iam::954637862788:user/sazzad`; configured region `eu-west-1`.
These results came from read-only AWS CLI calls and inspection of the
`imsazzad/imsazzad.com` repository. No drift detection was initiated and no
AWS resource was changed.

## Confirmed CloudFormation ownership

| Owner | Live resources | Status |
| --- | --- | --- |
| `PortfolioDev` in `eu-west-1` | Two portfolio S3 buckets and their policies, CloudFront distribution, response headers policy, origin access control, routing function, and `portfolio-dev-monthly` budget | `UPDATE_ROLLBACK_COMPLETE`; all nine resources listed by CloudFormation |
| `CDKToolkit` in `eu-west-1` | CDK asset bucket, ECR repository, bootstrap SSM parameter, five bootstrap roles, and supporting policies | `CREATE_COMPLETE`; created by `cdk bootstrap` |

There were no active CloudFormation stacks in `us-east-1` at the time of the
check. `PortfolioDev` drift status was `NOT_CHECKED`. The standard CDK
bootstrap execution role had the AWS-managed `AdministratorAccess` policy.
This matters because a deployment that can pass that role to CloudFormation
can have broader effective power than the entry role's direct policy suggests.

## Existing resources outside those stacks

| Resource or setting | Evidence and proposed owner |
| --- | --- |
| GitHub IAM OIDC provider `token.actions.githubusercontent.com` | Exists in IAM with audience `sts.amazonaws.com`; no CloudFormation stack resource. Candidate for this new repository after verifying import support. |
| `PortfolioGitHubDevDeployRole` | Exists in IAM with two inline policies, `PortfolioGitHubDevDeployRolePolicy` and `PortfolioCdkRoleAssumption`; no CloudFormation stack resource. Candidate for this new repository. Its live trust uses the custom subject `repo:imsazzad@9584472/imsazzad.com@1370652664:environment:development`; preserve and verify it against GitHub before any edit. |
| Portfolio budget notifications | Live `portfolio-dev-monthly` has 20%, 60%, and 100% forecast alerts with an email subscriber. The deployed CloudFormation template has `NotificationsWithSubscribers: []`. This is a portfolio-stack reconciliation task, not a transfer to the new repository. A prior CDK update for alerts failed and rolled back. |
| Human IAM identity | One IAM user, `sazzad`, belongs to `AlexAccess`, `AIEngineerAccess`, and `ControlledAdminAccess`. The latter has `AdministratorAccess`. The user has one active access key and no IAM MFA device listed. These facts warrant a separate access review; they do not authorize automatic changes. |
| Temporary CDK bootstrap operator policy | `PortfolioCdkBootstrapOperator` remains an inline policy on `AIEngineerAccess`, despite the portfolio runbook saying to remove it after bootstrap. It allows broad CloudFormation, S3, ECR, and SSM actions plus scoped bootstrap-role operations. Confirm other consumers and a recovery path before removal. |
| Other budgets | `AWS Monthly Cost Check`, `My Monthly Cost Budget`, and `Zero-Spend check` exist outside `PortfolioDev`. Ownership and notification consumers have not been established. |
| Other project resources | `twin-terraform-state-954637862788` S3 bucket and `twin-terraform-locks` DynamoDB table are tagged `ManagedBy=terraform`. Other IAM roles and account-local policies exist for unrelated work. Keep them with their owners. |
| Service-managed/default resources | Several AWS service-linked roles and default VPC/service objects appear in inventory. Their presence alone does not make them targets for custom CDK ownership. |
| GitHub configuration | The `development` environment and `AWS_DEV_DEPLOY_ROLE_ARN` variable are used by the portfolio workflow. They are GitHub-side settings, outside AWS CDK ownership. |

The live `PortfolioGitHubDevDeployRolePolicy` matches the policy document in
the portfolio repository's `docs/github-oidc-deployment-policy.json`; its
second inline policy permits assumption of the four named CDK bootstrap
deploy/publishing/lookup roles. The portfolio workflow assumes that role and
deploys `PortfolioDev` on pushes to `development`.

## Inventory coverage and limits

Queries covered CloudFormation in `eu-west-1` and `us-east-1`; global IAM,
Budgets, S3, and CloudFront; Resource Explorer's local indexes in those two
regions; and Lambda, API Gateway, RDS, DynamoDB, and EC2 instances in
`eu-west-1`. No Lambda functions, REST/HTTP APIs, RDS clusters/instances, or
EC2 instances were returned in `eu-west-1`; the DynamoDB table above was
returned. Resource Explorer contains defaults and possibly stale records, and
its indexes are local rather than account-wide aggregators. This is not an
exhaustive scan of every service and region. Re-inventory before assigning
ownership or asserting that a resource does not exist.

## Source records and AWS references

The source portfolio repository is `imsazzad/imsazzad.com`. Relevant paths are
`infrastructure/stacks/portfolio_dev.py`,
`infrastructure/constructs/budget.py`, `docs/github-oidc-bootstrap.md`,
`docs/github-oidc-trust-policy.json`,
`docs/github-oidc-deployment-policy.json`, and
`docs/cdk-bootstrap-operator-policy.json`.

- [CDK bootstrap resources and roles](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping-env.html)
- [CDK bootstrap execution policy implications](https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-bootstrap.html)
- [CloudFormation resource import](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/import-resources.html)
- [Resource type import and drift support](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import-supported-resources.html)
- [Budget notification replacement semantics](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-budgets-budget-notificationwithsubscribers.html)
