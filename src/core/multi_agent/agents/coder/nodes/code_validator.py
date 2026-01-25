"""
Code Validator Node - Validates Python syntax and basic logic.
"""

import ast
from src.core.multi_agent.agents.coder.state import CoderAgentState


def _validate_syntax(code: str) -> list:
    """
    Validate Python syntax by parsing with AST.

    Args:
        code: Python code to validate

    Returns:
        List of syntax errors (empty if valid)
    """
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
    except Exception as e:
        errors.append(f"Parse error: {str(e)}")

    return errors


def _basic_logic_checks(code: str) -> list:
    """
    Perform basic logic validation checks.

    Detects:
    - Infinite loops (basic heuristic)
    - Unreachable code after return

    Args:
        code: Python code to check

    Returns:
        List of logic warnings
    """
    warnings = []

    # Check for infinite loops (basic heuristic)
    if "while True" in code and "break" not in code:
        warnings.append("Potential infinite loop detected (while True without break)")

    # Check for unreachable code after return
    lines = code.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("return"):
            # Check if there's code after return in same block
            indent = len(line) - len(line.lstrip())
            for next_line in lines[i + 1 :]:
                if next_line.strip() and not next_line.strip().startswith("#"):
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent >= indent:
                        warnings.append(f"Potential unreachable code at line {i+2}")
                        break

    return warnings


def code_validator_node(state: CoderAgentState) -> CoderAgentState:
    """
    Validate generated code for syntax and basic logic errors.

    PHASE 5: CODE VALIDATION

    Performs:
    - Python syntax validation (AST parsing)
    - Basic logic checks (infinite loops, unreachable code)
    - Warning identification

    Code is accepted with warnings but rejected with syntax errors.

    Args:
        state: Current agent state

    Returns:
        Updated state with validation results
    """

    print("\n  - PHASE 6: CODE VALIDATION")

    # Skip if no code was generated
    if not state.get("raw_code"):
        state["validated_code"] = None
        state["validation_errors"] = ["No code to validate"]
        if state.get("show_node_info"):
            print("    No code to validate\n")
        return state

    syntax_errors = _validate_syntax(state["raw_code"])
    logic_warnings = _basic_logic_checks(state["raw_code"])

    # Code is valid even with warnings, but invalid with syntax errors
    is_valid = len(syntax_errors) == 0

    if is_valid:
        state["validated_code"] = state["raw_code"]
        state["validation_errors"] = logic_warnings  # Store warnings
    else:
        state["validated_code"] = None
        state["validation_errors"] = syntax_errors
        state["errors"] = state.get("errors", []) + syntax_errors

    if state.get("show_node_info"):
        if is_valid:
            if logic_warnings:
                print(f"    Code validated with {len(logic_warnings)} warning(s):")
                for warning in logic_warnings[:3]:
                    print(f"      - {warning}")
                if len(logic_warnings) > 3:
                    print(f"      - ... and {len(logic_warnings) - 3} more")
            else:
                print("    Code validated (no syntax errors)")
            print()
        else:
            print(f"    Syntax errors found ({len(syntax_errors)}):")
            for error in syntax_errors[:3]:
                print(f"      - {error}")
            if len(syntax_errors) > 3:
                print(f"      - ... and {len(syntax_errors) - 3} more")
            print()

    return state
