"""
Multi-Node Coder Agent Pipeline

Architecture: 6-phase specialized code generation workflow
- Input Validator: Validates function signature and plan structure
- Edge Case Analyzer: Identifies potential edge cases and boundary conditions
- CoT Generator: Creates chain-of-thought reasoning for structured problem solving
- Code Generator: Generates Python code using CoT and plan
- Code Validator: Validates syntax and basic logic
- Code Optimizer: Optimizes code for readability and performance

Flow:
  START → Input Validator → Edge Case Analyzer → CoT Generator
    → Code Generator → Code Validator → Code Optimizer → END

"""

from langgraph.graph import StateGraph, START, END
from src.core.multi_agent.agents.coder.state import CoderAgentState
from src.core.multi_agent.agents.coder.nodes.input_validator import input_validator_node
from src.core.multi_agent.agents.coder.nodes.edge_case_analyzer import (
    edge_case_analyzer_node,
)
from src.core.multi_agent.agents.coder.nodes.cot_generator import cot_generator_node
from src.core.multi_agent.agents.coder.nodes.code_generator import code_generator_node
from src.core.multi_agent.agents.coder.nodes.code_validator import code_validator_node
from src.core.multi_agent.agents.coder.nodes.code_optimizer import code_optimizer_node


def consolidation_node(state: CoderAgentState) -> CoderAgentState:
    """
    Consolidate optimized code into final output.

    Final step that packages code for delivery to critic agent.
    """
    # Use optimized code as final output
    state["code"] = state.get("optimized_code")

    if state.get("show_node_info"):
        if state["code"]:
            lines = state["code"].split("\n")
            print(f"\nCode generation complete")
            print(f"Lines: {len(lines)}")
            print(f"Status: Ready for critic review")
        else:
            print(f"\nNo code generated")
            if state.get("errors"):
                print(f"Errors: {len(state['errors'])}")
                for err in state["errors"][:3]:
                    print(f"   - {err}")

    return state


# ═══════════════════════════════════════════════════════════════════════
# GRAPH BUILDER
# ═══════════════════════════════════════════════════════════════════════


def build_coder_graph():
    """
    Build the multi-node coder agent graph.

    Architecture:
    - 6 specialized code generation nodes
    - Input validation gate
    - Chain-of-thought reasoning for improved quality
    - Validation to ensure correctness
    - Optimization for final polish
    - Consolidation for final output

    Returns:
        Compiled LangGraph
    """
    graph = StateGraph(CoderAgentState)

    # Add all nodes
    graph.add_node("input_validator", input_validator_node)
    graph.add_node("edge_case_analyzer", edge_case_analyzer_node)
    graph.add_node("cot_generator", cot_generator_node)
    graph.add_node("code_generator", code_generator_node)
    graph.add_node("code_validator", code_validator_node)
    graph.add_node("code_optimizer", code_optimizer_node)
    graph.add_node("consolidation", consolidation_node)

    # Define flow - linear pipeline
    graph.add_edge(START, "input_validator")
    graph.add_edge("input_validator", "edge_case_analyzer")
    graph.add_edge("edge_case_analyzer", "cot_generator")
    graph.add_edge("cot_generator", "code_generator")
    graph.add_edge("code_generator", "code_validator")
    graph.add_edge("code_validator", "code_optimizer")
    graph.add_edge("code_optimizer", "consolidation")
    graph.add_edge("consolidation", END)

    return graph.compile()
