from typing import cast

from aws_cdk.assertions import Template

from account_foundation.config import TARGET_ACCOUNT, TARGET_REGION
from account_foundation.constructs.portfolio_github_deployment_iam import (
    GITHUB_OIDC_PROVIDER_LOGICAL_ID,
    PORTFOLIO_DEPLOY_ROLE_LOGICAL_ID,
)
from account_foundation.stacks.account_foundation_stack import AccountFoundationStack
from app import STACK_ID, STACK_NAME, build_app


def _stack() -> AccountFoundationStack:
    app = build_app()
    stack = app.node.find_child(STACK_ID)
    assert isinstance(stack, AccountFoundationStack)
    return stack


def test_app_uses_explicit_target_and_protection() -> None:
    stack = _stack()

    assert stack.account == TARGET_ACCOUNT
    assert stack.region == TARGET_REGION
    assert stack.stack_name == STACK_NAME
    assert stack.termination_protection is True


def test_oidc_provider_matches_live_configuration_and_is_retained() -> None:
    template = Template.from_stack(_stack()).to_json()
    resource = cast(dict[str, object], template["Resources"][GITHUB_OIDC_PROVIDER_LOGICAL_ID])

    assert resource == {
        "Type": "AWS::IAM::OIDCProvider",
        "Properties": {
            "ClientIdList": ["sts.amazonaws.com"],
            "ThumbprintList": ["1b511abead59c6ce207077c0bf0e0043b1382612"],
            "Url": "https://token.actions.githubusercontent.com",
        },
        "UpdateReplacePolicy": "Retain",
        "DeletionPolicy": "Retain",
    }


def test_role_trust_and_inline_policies_match_live_configuration() -> None:
    template = Template.from_stack(_stack()).to_json()
    resources = cast(dict[str, dict[str, object]], template["Resources"])
    role = resources[PORTFOLIO_DEPLOY_ROLE_LOGICAL_ID]

    assert role == {
        "Type": "AWS::IAM::Role",
        "Properties": {
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "GitHubActionsAwsDevBranch",
                        "Effect": "Allow",
                        "Principal": {"Federated": {"Ref": GITHUB_OIDC_PROVIDER_LOGICAL_ID}},
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                            },
                            "StringLike": {
                                "token.actions.githubusercontent.com:sub": (
                                    "repo:imsazzad@9584472/imsazzad.com@1370652664:"
                                    "environment:development"
                                )
                            },
                        },
                    }
                ],
            },
            "Description": "",
            "MaxSessionDuration": 3600,
            "Path": "/",
            "Policies": [
                {
                    "PolicyName": "PortfolioCdkRoleAssumption",
                    "PolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "AssumeCdkBootstrapRoles",
                                "Effect": "Allow",
                                "Action": ["sts:AssumeRole", "sts:TagSession"],
                                "Resource": [
                                    "arn:aws:iam::954637862788:role/"
                                    "cdk-hnb659fds-deploy-role-954637862788-eu-west-1",
                                    "arn:aws:iam::954637862788:role/"
                                    "cdk-hnb659fds-file-publishing-role-"
                                    "954637862788-eu-west-1",
                                    "arn:aws:iam::954637862788:role/"
                                    "cdk-hnb659fds-image-publishing-role-"
                                    "954637862788-eu-west-1",
                                    "arn:aws:iam::954637862788:role/"
                                    "cdk-hnb659fds-lookup-role-954637862788-eu-west-1",
                                ],
                            }
                        ],
                    },
                },
                {
                    "PolicyName": "PortfolioGitHubDevDeployRolePolicy",
                    "PolicyDocument": {
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
                                "Resource": (
                                    "arn:aws:cloudformation:eu-west-1:954637862788:"
                                    "stack/PortfolioDev/*"
                                ),
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
                                    "arn:aws:iam::954637862788:role/"
                                    "cdk-hnb659fds-cfn-exec-role-"
                                    "954637862788-eu-west-1"
                                ),
                            },
                            {
                                "Sid": "ReadBootstrapVersion",
                                "Effect": "Allow",
                                "Action": ["ssm:GetParameter", "ssm:GetParameters"],
                                "Resource": (
                                    "arn:aws:ssm:eu-west-1:954637862788:parameter/cdk-bootstrap/*"
                                ),
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
                                "Resource": ("arn:aws:cloudfront::954637862788:distribution/*"),
                            },
                        ],
                    },
                },
            ],
            "RoleName": "PortfolioGitHubDevDeployRole",
        },
        "UpdateReplacePolicy": "Retain",
        "DeletionPolicy": "Retain",
    }

    assertions = Template.from_stack(_stack())
    assertions.resource_count_is("AWS::IAM::Role", 1)
    assertions.resource_count_is("AWS::IAM::RolePolicy", 0)
