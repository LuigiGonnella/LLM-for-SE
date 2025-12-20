from langgraph.graph import StateGraph, START, END
from src.core.state import AgentState
from src.tools.executor import execute_code
from src.utils.code_parser import extract_python_code
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
    raw_code = generate_code(
        signature=state["signature"],
        plan=state["plan"],
        model=state["model"],
    )
    state["code"] = extract_python_code(raw_code)
    return state


def review_node(state: AgentState) -> AgentState:
    print(">> REVIEW NODE")
    exec_result = execute_code(state["code"])
    state["exec_result"] = exec_result

    state["review"] = review_code(
        code=state["code"],
        model=state["model"],
        exec_result=exec_result,
    )

    print(f"Review results: {exec_result}")
    return state


def refinement_node(state: AgentState) -> AgentState:
    print(">> REFINEMENT NODE")

    max_refinements = 3
    refinement_count = state.get("refinement_count", 0)

    if refinement_count >= max_refinements:
        print("Maximum refinements reached. Ending refinement.")
        return state
    
    raw_code = refine_code(
        code=state["code"],
        review=state["review"],
        model=state["model"],
    )
    refined_code = extract_python_code(raw_code)
    refined_result = execute_code(refined_code)

    state["code"] = refined_code
    state["exec_result"] = refined_result
    state["refinement_count"] = refinement_count + 1

    if refined_result["success"]:
        print("Refinement successful.")
    else:
        print("Refinement did not lead to successful execution.")
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
