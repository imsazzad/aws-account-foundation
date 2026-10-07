from aws_cdk import App, Environment

from account_foundation.config import TARGET_ACCOUNT, TARGET_REGION
from account_foundation.stacks.account_foundation_stack import AccountFoundationStack

STACK_ID = "AccountFoundation"
STACK_NAME = "AccountFoundation"


def build_app() -> App:
    app = App()
    AccountFoundationStack(
        app,
        STACK_ID,
        env=Environment(account=TARGET_ACCOUNT, region=TARGET_REGION),
        stack_name=STACK_NAME,
        termination_protection=True,
    )
    return app


def main() -> None:
    build_app().synth()


if __name__ == "__main__":
    main()
