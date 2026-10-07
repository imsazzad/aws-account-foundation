from aws_cdk import Environment, Stack
from constructs import Construct


class AccountFoundationStack(Stack):
    """Owns explicitly approved account-level resources.

    A1 intentionally defines no resources. Existing resources are added only
    after their ownership and CloudFormation import path have been reviewed.
    """

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
