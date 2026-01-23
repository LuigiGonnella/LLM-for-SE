"""
Code Generator Node - Generates Python code using CoT and plan.
"""

from src.core.multi_agent.agents.coder.state import CoderAgentState
from src.core.multi_agent.agents.coder.llm import generate_code
from src.utils.code_parser import extract_python_code


def code_generator_node(state: CoderAgentState) -> CoderAgentState:
    """
    Generate Python code based on plan and chain-of-thought reasoning.

    PHASE 4: CODE GENERATION

    Uses:
    - Function signature
    - Implementation plan
    - Edge cases identified
    - CoT reasoning for structured guidance
    - Previous iteration feedback (if any)
    - Execution summary from failures (if any)

    Args:
        state: Current agent state

    Returns:
        Updated state with generated code
    """
    # Skip if validation failed
    if not state.get("should_proceed"):
        state["raw_code"] = None
        return state

    try:
        # Generate code with all context from previous phases
        raw_code = generate_code(
            signature=state.get("signature"),
            plan=state.get("plan"),
            cot_reasoning=state.get("cot_reasoning", ""),
            edge_cases=state.get("edge_cases", []),
            model=state.get("model"),
            critic_feedback=state.get("critic_feedback"),
            exec_summary=state.get("exec_summary"),
        )

        # Extract Python code from the response
        extracted = extract_python_code(raw_code)
        if extracted is None:
            error_msg = "Failed to extract valid Python code from generation output"
            state["errors"] = state.get("errors", []) + [error_msg]
            state["raw_code"] = None
            if state.get("show_node_info"):
                print(f"  {error_msg}\n")
            return state

        state["raw_code"] = extracted

        if state.get("show_node_info"):
            lines = extracted.split("\n")
            preview = "\n".join(lines[:5])
            if len(lines) > 5:
                preview += f"\n... ({len(lines)} lines total)"
            print(f"\nGenerated Code ({len(lines)} lines):")
            print(preview)
            print()

    except Exception as e:
        error_msg = f"Code generation error: {str(e)}"
        state["errors"] = state.get("errors", []) + [error_msg]
        state["raw_code"] = None
        if state.get("show_node_info"):
            print(f"  {error_msg}\n")

    return state
