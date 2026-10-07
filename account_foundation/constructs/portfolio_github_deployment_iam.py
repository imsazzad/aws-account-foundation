from aws_cdk import RemovalPolicy, aws_iam
from constructs import Construct

GITHUB_OIDC_PROVIDER_LOGICAL_ID = "GitHubOidcProvider"
PORTFOLIO_DEPLOY_ROLE_LOGICAL_ID = "PortfolioGitHubDevDeployRole"

GITHUB_OIDC_URL = "https://token.actions.githubusercontent.com"
GITHUB_OIDC_AUDIENCE = "sts.amazonaws.com"
GITHUB_OIDC_THUMBPRINT = "1b511abead59c6ce207077c0bf0e0043b1382612"
GITHUB_OIDC_SUBJECT = "repo:imsazzad@9584472/imsazzad.com@1370652664:environment:development"

PORTFOLIO_DEPLOY_ROLE_NAME = "PortfolioGitHubDevDeployRole"
CDK_ROLE_ASSUMPTION_POLICY_NAME = "PortfolioCdkRoleAssumption"
DEPLOYMENT_POLICY_NAME = "PortfolioGitHubDevDeployRolePolicy"

CDK_ROLE_ASSUMPTION_POLICY_DOCUMENT: dict[str, object] = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AssumeCdkBootstrapRoles",
            "Effect": "Allow",
            "Action": ["sts:AssumeRole", "sts:TagSession"],
            "Resource": [
                "arn:aws:iam::954637862788:role/cdk-hnb659fds-deploy-role-954637862788-eu-west-1",
                "arn:aws:iam::954637862788:role/"
                "cdk-hnb659fds-file-publishing-role-954637862788-eu-west-1",
                "arn:aws:iam::954637862788:role/"
                "cdk-hnb659fds-image-publishing-role-954637862788-eu-west-1",
                "arn:aws:iam::954637862788:role/cdk-hnb659fds-lookup-role-954637862788-eu-west-1",
            ],
        }
    ],
}

DEPLOYMENT_POLICY_DOCUMENT: dict[str, object] = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudFormationDevStack",
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateChangeSet",
                "cloudformation:DescribeChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackEvents",
                "cloudformation:GetTemplate",
                "cloudformation:ListStackResources",
                "cloudformation:DeleteStack",
            ],
            "Resource": ("arn:aws:cloudformation:eu-west-1:954637862788:stack/PortfolioDev/*"),
        },
        {
            "Sid": "CloudFormationCreateStack",
            "Effect": "Allow",
            "Action": "cloudformation:CreateStack",
            "Resource": "*",
        },
        {
            "Sid": "ReadCdkBootstrapAssets",
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
            ],
            "Resource": [
                "arn:aws:s3:::cdk-hnb659fds-assets-954637862788-eu-west-1",
                "arn:aws:s3:::cdk-hnb659fds-assets-954637862788-eu-west-1/*",
            ],
        },
        {
            "Sid": "PassOnlyCdkExecutionRole",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": (
                "arn:aws:iam::954637862788:role/cdk-hnb659fds-cfn-exec-role-954637862788-eu-west-1"
            ),
        },
        {
            "Sid": "ReadBootstrapVersion",
            "Effect": "Allow",
            "Action": ["ssm:GetParameter", "ssm:GetParameters"],
            "Resource": "arn:aws:ssm:eu-west-1:954637862788:parameter/cdk-bootstrap/*",
        },
        {
            "Sid": "PublishDevSite",
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
            ],
            "Resource": [
                "arn:aws:s3:::portfolio-resume-site-954637862788-eu-west-1",
                "arn:aws:s3:::portfolio-resume-site-954637862788-eu-west-1/*",
            ],
        },
        {
            "Sid": "InvalidateDevDistribution",
            "Effect": "Allow",
            "Action": "cloudfront:CreateInvalidation",
            "Resource": "arn:aws:cloudfront::954637862788:distribution/*",
        },
    ],
}


class PortfolioGitHubDeploymentIam(Construct):
    """Exact import model for the portfolio GitHub OIDC provider and role."""

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.provider = aws_iam.CfnOIDCProvider(
            self,
            "GitHubOidcProvider",
            client_id_list=[GITHUB_OIDC_AUDIENCE],
            thumbprint_list=[GITHUB_OIDC_THUMBPRINT],
            url=GITHUB_OIDC_URL,
        )
        self.provider.override_logical_id(GITHUB_OIDC_PROVIDER_LOGICAL_ID)
        self.provider.apply_removal_policy(RemovalPolicy.RETAIN)

        self.role = aws_iam.CfnRole(
            self,
            "PortfolioGitHubDevDeployRole",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "GitHubActionsAwsDevBranch",
                        "Effect": "Allow",
                        "Principal": {"Federated": self.provider.ref},
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                "token.actions.githubusercontent.com:aud": GITHUB_OIDC_AUDIENCE
                            },
                            "StringLike": {
                                "token.actions.githubusercontent.com:sub": GITHUB_OIDC_SUBJECT
                            },
                        },
                    }
                ],
            },
            description="",
            max_session_duration=3600,
            path="/",
            policies=[
                aws_iam.CfnRole.PolicyProperty(
                    policy_document=CDK_ROLE_ASSUMPTION_POLICY_DOCUMENT,
                    policy_name=CDK_ROLE_ASSUMPTION_POLICY_NAME,
                ),
                aws_iam.CfnRole.PolicyProperty(
                    policy_document=DEPLOYMENT_POLICY_DOCUMENT,
                    policy_name=DEPLOYMENT_POLICY_NAME,
                ),
            ],
            role_name=PORTFOLIO_DEPLOY_ROLE_NAME,
        )
        self.role.override_logical_id(PORTFOLIO_DEPLOY_ROLE_LOGICAL_ID)
        self.role.apply_removal_policy(RemovalPolicy.RETAIN)
