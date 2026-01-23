"""
Chain-of-Thought (CoT) Generator Node - Creates structured reasoning for code generation.
"""

from src.core.multi_agent.agents.coder.state import CoderAgentState
from src.core.multi_agent.agents.coder.llm import generate_chain_of_thought


def cot_generator_node(state: CoderAgentState) -> CoderAgentState:
    """
    Generate chain-of-thought reasoning for structured problem solving.

    PHASE 3: CHAIN-OF-THOUGHT GENERATION

    Creates a step-by-step reasoning that:
    - Breaks down the problem into atomic steps
    - References identified edge cases
    - Plans the algorithm approach
    - Guides code generation with structured thinking
    - Incorporates feedback from previous iterations

    Args:
        state: Current agent state

    Returns:
        Updated state with CoT reasoning
    """

    # Skip if validation failed
    if not state.get("should_proceed"):
        state["cot_reasoning"] = ""
        return state

    try:
        # Generate structured chain-of-thought
        cot_text = generate_chain_of_thought(
            signature=state.get("signature"),
            plan=state.get("plan"),
            edge_cases=state.get("edge_cases", []),
            model=state.get("model"),
            critic_feedback=state.get("critic_feedback"),
            exec_summary=state.get("exec_summary"),
        )

        state["cot_reasoning"] = cot_text

        if state.get("show_node_info"):
            lines = cot_text.split("\n")
            preview = "\n".join(lines[:8])
            if len(lines) > 8:
                preview += f"\n... ({len(lines)} lines total)"
            print(f"\nGenerated Chain-of-Thought ({len(lines)} lines):")
            print(preview)
            print()

    except Exception as e:
        error_msg = f"CoT generation error: {str(e)}"
        state["errors"] = state.get("errors", []) + [error_msg]
        state["cot_reasoning"] = ""
        if state.get("show_node_info"):
            print(f"  {error_msg}\n")

    return state
