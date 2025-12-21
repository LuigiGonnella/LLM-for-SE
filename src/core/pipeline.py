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

    print(f"Exec results: {exec_result}")
    print(f'Reviewer result: {state["review"].split('\n')[-1]}')
    return state


def refinement_node(state: AgentState) -> AgentState:
    print(">> REFINEMENT NODE")

    max_refinements = 3
    refinement_count = state.get("refinement_count", 0)

    # EARLY EXIT if code is already correct
    if "review" in state and "Code is correct" in state["review"]:
        print("Code already correct. Skipping refinement.")
        return state

    if refinement_count >= max_refinements:
        print("Maximum refinements reached. Ending refinement.")
        return state

    raw_code = refine_code(
        code=state["code"],
        review=state["review"],
        model=state["model"],
    )

    # Refiner MUST output pure Python
    refined_code = extract_python_code(raw_code)

    exec_result = execute_code(refined_code)

    # Always update state
    state["code"] = refined_code
    state["exec_result"] = exec_result
    state["refinement_count"] = refinement_count + 1

    # Re-run reviewer after refinement
    review = review_code(
        code=refined_code,
        exec_result=exec_result,
        model=state["model"],
    )
    state["review"] = review

    # Decide outcome based on reviewer verdict, not exec alone
    if "Code is correct" in review:
        print("Refinement successful: code is correct.")
    else:
        print("Refinement incomplete: issues remain.")

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
