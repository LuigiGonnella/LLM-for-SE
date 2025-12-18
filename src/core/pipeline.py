from langgraph.graph import StateGraph, START, END
from src.core.state import AgentState
from src.core.agent import (
    analyze_task,
    plan_solution,
    generate_code,
    review_code,
    refine_code,
)


def analysis_node(state: AgentState) -> AgentState:
    print(">> ANALYSIS NODE")
    state["analysis"] = analyze_task(
        signature=state["signature"],
        docstring=state["docstring"],
        examples=state.get("examples"),
        model=state["model"],
    )
    return state


def planning_node(state: AgentState) -> AgentState:
    print(">> PLANNING NODE")
    state["plan"] = plan_solution(
        analysis=state["analysis"],
        model=state["model"],
    )
    return state


def generation_node(state: AgentState) -> AgentState:
    print(">> GENERATION NODE")
    state["code"] = generate_code(
        signature=state["signature"],
        plan=state["plan"],
        model=state["model"],
    )
    return state


def review_node(state: AgentState) -> AgentState:
    print(">> REVIEW NODE")
    state["review"] = review_code(
        code=state["code"],
        model=state["model"],
    )
    return state


def refinement_node(state: AgentState) -> AgentState:
    print(">> REFINEMENT NODE")
    state["code"] = refine_code(
        code=state["code"],
        review=state["review"],
        model=state["model"],
    )
    return state


def build_single_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analysis", analysis_node)
    graph.add_node("planning", planning_node)
    graph.add_node("generation", generation_node)
    graph.add_node("review", review_node)
    graph.add_node("refinement", refinement_node)

    graph.add_edge(START, "analysis")
    graph.add_edge("analysis", "planning")
    graph.add_edge("planning", "generation")
    graph.add_edge("generation", "review")
    graph.add_edge("review", "refinement")
    graph.add_edge("refinement", END)

    return graph.compile()
