"""
Input Validator Node - Validates function signature and plan structure.
"""

import re
from src.core.multi_agent.agents.coder.state import CoderAgentState


def _validate_function_signature(signature: str) -> list:
    """
    Validate Python function signature syntax.

    Args:
        signature: Function signature to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not signature or len(signature.strip()) == 0:
        errors.append("Signature cannot be empty")
        return errors

    # Check if signature starts with 'def'
    if not signature.strip().startswith("def "):
        errors.append("Signature must start with 'def'")

    # Check for function name and parentheses
    if not re.search(r"def\s+\w+\s*\(", signature):
        errors.append("Invalid function name or missing parentheses")

    # Check for return type annotation or colon
    if not signature.rstrip().endswith(":"):
        errors.append("Signature must end with ':'")

    return errors


def _validate_plan_structure(plan: str) -> list:
    """
    Validate implementation plan structure.

    Args:
        plan: Implementation plan to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not plan or len(plan.strip()) == 0:
        errors.append("Plan cannot be empty")
        return errors

    if len(plan.strip()) < 20:
        errors.append("Plan seems too brief (< 20 characters) - needs more detail")

    return errors


def input_validator_node(state: CoderAgentState) -> CoderAgentState:
    """
    Validate input signature and plan before processing.

    PHASE 1: INPUT VALIDATION

    Checks:
    - Function signature syntax
    - Plan structure and clarity
    - Required fields presence

    Args:
        state: Current agent state

    Returns:
        Updated state with validation results
    """
    validation_errors = []

    # Validate function signature
    sig_errors = _validate_function_signature(state.get("signature", ""))
    validation_errors.extend(sig_errors)

    # Validate plan
    plan_errors = _validate_plan_structure(state.get("plan", ""))
    validation_errors.extend(plan_errors)

    # Check required fields
    if not state.get("task_id"):
        validation_errors.append("task_id is required")

    if not state.get("model"):
        validation_errors.append("model is required")

    state["input_validation_errors"] = validation_errors
    state["should_proceed"] = len(validation_errors) == 0

    if state.get("show_node_info"):
        if state["should_proceed"]:
            print(f"\nInput validation passed")
            print(f"   • Signature: valid")
            print(f"   • Plan: {len(state.get('plan', '').split())} words")
            print(f"   • Task ID: {state.get('task_id')}\n")
        else:
            print(f"\nInput validation failed:")
            for error in validation_errors:
                print(f"   ✗ {error}")
            print()

    return state
