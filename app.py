from aws_cdk import Acknowledgment, App, Environment, Validations

from account_foundation.config import TARGET_ACCOUNT, TARGET_REGION
from account_foundation.stacks.account_foundation_stack import AccountFoundationStack

STACK_ID = "AccountFoundation"
STACK_NAME = "AccountFoundation"


def build_app() -> App:
    app = App()
    stack = AccountFoundationStack(
        app,
        STACK_ID,
        env=Environment(account=TARGET_ACCOUNT, region=TARGET_REGION),
        stack_name=STACK_NAME,
        termination_protection=True,
    )
    Validations.of(stack).acknowledge(
        Acknowledgment(
            id="CloudFormation-Validate::F0001",
            reason="A1 intentionally establishes an empty stack before resource adoption.",
        )
    )
    return app


def main() -> None:
    build_app().synth()


if __name__ == "__main__":
    main()
