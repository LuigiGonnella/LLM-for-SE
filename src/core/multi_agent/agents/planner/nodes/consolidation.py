from src.core.multi_agent.agents.planner.state import AgentState


def consolidation_node(state: AgentState) -> AgentState:
    """
    Consolidate all planning phases into final unified plan.
    """
    print("\n  - PHASE 6: PLAN CONSOLIDATION")

    final_plan = {
        "task_id": state.get("task_id"),
        "user_request": state.get("user_request"),
        "intent": state.get("intent_analysis"),
        "requirements": state.get("requirements"),
        "architecture": state.get("architecture"),
        "implementation": state.get("implementation_plan"),
        "quality_review": state.get("quality_review"),
        "approved": state.get("plan_approved", False),
        "iterations": state.get("iteration_count", 0),
    }

    state["final_plan"] = final_plan

    if state.get("show_node_info"):
        print("    Final plan assembled")
        print(
            f"    Components: {len(final_plan.get('architecture', {}).get('components', []))}"
        )
        print(f"    Iterations: {final_plan.get('iterations', 0)}")
        print(
            f"    {'Status: APPROVED' if final_plan.get('approved') else 'Status: BEST EFFORT'}"
        )

    return state
