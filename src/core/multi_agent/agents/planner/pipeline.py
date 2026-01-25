"""
Multi-Node Planner Agent Pipeline

Architecture: 5-phase specialized planning workflow
"""

from langgraph.graph import StateGraph, START, END
from src.core.multi_agent.agents.planner.state import AgentState
from src.core.multi_agent.agents.planner.nodes.intent_analyzer import intent_analysis_node
from src.core.multi_agent.agents.planner.nodes.requirements_engineer import requirements_engineering_node
from src.core.multi_agent.agents.planner.nodes.architecture_designer import architecture_design_node
from src.core.multi_agent.agents.planner.nodes.implementation_planner import implementation_planning_node
from src.core.multi_agent.agents.planner.nodes.quality_reviewer import quality_review_node
from src.core.multi_agent.agents.planner.nodes.consolidation import consolidation_node


def should_refine(state: AgentState) -> str:
    """
    Decide whether to refine the plan or proceed to consolidation.
    """
    plan_approved = state.get("plan_approved", False)
    iteration_count = state.get("iteration_count", 0)

    if plan_approved:
        print("\n  Plan approved! Proceeding to consolidation.")
        return "consolidation"

    if iteration_count <= 2:
        quality_review = state.get("quality_review", {})
        retry_phase = quality_review.get("retry_phase", "architecture_design")

        # Validate retry_phase
        valid_phases = [
            "requirements_engineering",
            "architecture_design",
            "implementation_planning",
        ]
        if retry_phase not in valid_phases:
            retry_phase = "architecture_design"  # Default fallback

        print(
            f"\n  Plan needs revision. Retrying from {retry_phase} (iteration {iteration_count}/2)"
        )
        return retry_phase

    print("\n  Max iterations reached. Proceeding with best-effort plan.")
    return "consolidation"
    

def build_planner_graph():
    """
    Build the multi-node planner agent graph.
    """
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("intent_analysis", intent_analysis_node)
    graph.add_node("requirements_engineering", requirements_engineering_node)
    graph.add_node("architecture_design", architecture_design_node)
    graph.add_node("implementation_planning", implementation_planning_node)
    graph.add_node("quality_review", quality_review_node)
    graph.add_node("consolidation", consolidation_node)

    # Define flow
    graph.add_edge(START, "intent_analysis")
    graph.add_edge("intent_analysis", "requirements_engineering")
    graph.add_edge("requirements_engineering", "architecture_design")
    graph.add_edge("architecture_design", "implementation_planning")
    graph.add_edge("implementation_planning", "quality_review")

    # Conditional routing after quality review
    graph.add_conditional_edges(
        "quality_review",
        should_refine,
        {
            "requirements_engineering": "requirements_engineering",
            "architecture_design": "architecture_design",
            "implementation_planning": "implementation_planning",
            "consolidation": "consolidation",
        },
    )

    graph.add_edge("consolidation", END)

    return graph.compile()
