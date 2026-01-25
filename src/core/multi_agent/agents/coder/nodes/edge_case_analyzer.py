"""
Edge Case Analyzer Node - Identifies potential edge cases and boundary conditions.
"""

import re
from src.core.multi_agent.agents.coder.state import CoderAgentState
from src.core.multi_agent.agents.coder.llm import analyze_edge_cases


def _extract_type_hints(signature: str) -> dict:
    """
    Extract type hints from function signature.

    Args:
        signature: Function signature

    Returns:
        Dict with parameter and return types
    """
    types = {"params": [], "return": None}

    # Extract parameters with types
    params_match = re.search(r"\((.*?)\)", signature)
    if params_match:
        params_str = params_match.group(1)
        # Extract type hints like "n: int" or "arr: List[int]"
        type_matches = re.findall(r"(\w+):\s*(\w+(?:\[[\w\,\s]+\])?)", params_str)
        types["params"] = type_matches

    # Extract return type like "-> int" or "-> List[str]"
    return_match = re.search(r"->\s*(\w+(?:\[[\w\,\s]+\])?)", signature)
    if return_match:
        types["return"] = return_match.group(1)

    return types


def edge_case_analyzer_node(state: CoderAgentState) -> CoderAgentState:
    """
    Analyze potential edge cases and boundary conditions.

    PHASE 2: EDGE CASE ANALYSIS

    Considers:
    - Input type constraints
    - Boundary values (empty, zero, negative, very large)
    - Special cases mentioned in plan
    - Type-specific edge cases

    Args:
        state: Current agent state

    Returns:
        Updated state with identified edge cases
    """

    # Skip if validation failed
    if not state.get("should_proceed"):
        state["edge_cases"] = []
        return state

    print("\n  - PHASE 2: EDGE CASE ANALYSIS")

    try:
        # Extract type information from signature
        type_hints = _extract_type_hints(state.get("signature", ""))

        # Use LLM to analyze edge cases
        edge_cases_text = analyze_edge_cases(
            signature=state.get("signature"),
            plan=state.get("plan"),
            type_hints=type_hints,
            model=state.get("model"),
        )

        # Parse edge cases into a list
        edge_cases = [
            case.strip()
            for case in edge_cases_text.split("\n")
            if case.strip() and not case.startswith("#")
        ]

        state["edge_cases"] = edge_cases

        if state.get("show_node_info"):
            print(f"    Identified {len(edge_cases)} edge cases:")
            for i, case in enumerate(edge_cases[:5], 1):
                print(f"      - {i}. {case}")
            if len(edge_cases) > 5:
                print(f"      - ... and {len(edge_cases) - 5} more")
            print()

    except Exception as e:
        error_msg = f"Edge case analysis error: {str(e)}"
        state["errors"] = state.get("errors", []) + [error_msg]
        state["edge_cases"] = []
        if state.get("show_node_info"):
            print(f"    {error_msg}\n")

    return state
