from aws_cdk.assertions import Template

from account_foundation.config import TARGET_ACCOUNT, TARGET_REGION
from account_foundation.stacks.account_foundation_stack import AccountFoundationStack
from app import STACK_ID, STACK_NAME, build_app


def test_app_uses_explicit_target_and_defines_no_resources_in_a1() -> None:
    app = build_app()
    stack = app.node.find_child(STACK_ID)

    assert isinstance(stack, AccountFoundationStack)
    assert stack.account == TARGET_ACCOUNT
    assert stack.region == TARGET_REGION
    assert stack.stack_name == STACK_NAME
    assert stack.termination_protection is True
    assert Template.from_stack(stack).to_json().get("Resources", {}) == {}
