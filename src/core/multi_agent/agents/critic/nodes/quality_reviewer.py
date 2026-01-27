from src.core.multi_agent.agents.critic.state import CriticAgentState
from src.core.multi_agent.agents.critic.llm import analyze_quality


def quality_reviewer_node(state: CriticAgentState) -> CriticAgentState:
    """
    Review code quality and metrics.
    """
    if not state.get("should_proceed"):
        return state

    print("\n  - PHASE 3: QUALITY REVIEW")

    analysis = analyze_quality(
        code=state["code"],
        quality_metrics=state.get("quality_metrics"),
        model=state["model"],
    )

    state["quality_analysis"] = analysis

    if state.get("show_node_info"):
        print("    Quality review: ", state["quality_analysis"])

    return state
