from src.core.multi_agent.agents.critic.state import CriticAgentState
from src.core.multi_agent.agents.critic.llm import analyze_correctness

def correctness_analyzer_node(state: CriticAgentState) -> CriticAgentState:
    """
    Analyze functional correctness and logic.
    """
    if not state.get("should_proceed"):
        return state

    print("\n  - PHASE 2: CORRECTNESS ANALYSIS")

    analysis = analyze_correctness(
        signature=state["signature"],
        docstring=state.get("docstring", ""),
        plan=state["plan"],
        code=state["code"],
        exec_summary=state.get("exec_summary"),
        model=state["model"],
    )

    state["correctness_analysis"] = analysis

    if state.get("show_node_info"):
        print("    Correctness analysis: ", state["correctness_analysis"])

    return state
