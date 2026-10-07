from aws_cdk import Environment, Stack
from constructs import Construct

from account_foundation.constructs.portfolio_github_deployment_iam import (
    PortfolioGitHubDeploymentIam,
)


class AccountFoundationStack(Stack):
    """Owns explicitly approved account-level resources."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        env: Environment,
        stack_name: str,
        termination_protection: bool,
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            env=env,
            stack_name=stack_name,
            termination_protection=termination_protection,
        )

        PortfolioGitHubDeploymentIam(self, "PortfolioGitHubDeploymentIam")
