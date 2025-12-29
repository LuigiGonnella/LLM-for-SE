from langgraph.graph import StateGraph, START, END
from src.core.state import AgentState
from src.tools.executor import execute_code
from src.utils.code_parser import extract_python_code
from src.evaluation.quality import compute_quality_metrics, format_metrics_report
from src.core.agent import (
    analyze_task,
    plan_solution,
    generate_code,
    review_code,
    refine_code,
)


def analysis_node(state: AgentState) -> AgentState:
    print("\n>> ANALYSIS NODE")
    state["analysis"] = analyze_task(
        signature=state["signature"],
        docstring=state["docstring"],
        examples=state.get("examples"),
        model=state["model"],
    )
    
    if state.get("show_node_info"):
        print(f"  Analysis:\n  {state['analysis'].replace('\n', '\n  ')}\n")
    
    return state


def planning_node(state: AgentState) -> AgentState:
    print("\n>> PLANNING NODE")
    state["plan"] = plan_solution(
        analysis=state["analysis"],
        model=state["model"],
    )
    if state.get("show_node_info"):
        print(f"  Plan:\n  {state['plan'].replace('\n', '\n  ')}\n")
    
    return state


def generation_node(state: AgentState) -> AgentState:
    print("\n>> GENERATION NODE")
    raw_code = generate_code(
        signature=state["signature"],
        plan=state["plan"],
        model=state["model"],
    )
    state["code"] = extract_python_code(raw_code)

    if state.get("show_node_info"):
        print(f"  Generated Code:\n  {state['code'].replace('\n', '\n  ')}\n")
    
    return state


def review_node(state: AgentState) -> AgentState:
    print("\n>> REVIEW NODE")
    exec_result = execute_code(state["code"])
    state["exec_result"] = exec_result

    # Compute quality metrics
    metrics = compute_quality_metrics(state["code"])
    state["quality_metrics"] = metrics
    
    state["review"] = review_code(
        code=state["code"],
        model=state["model"],
        exec_result=exec_result,
        quality_metrics=metrics,
    )
     
    print("  " + format_metrics_report(metrics).replace("\n", "\n  "))
    print(f"\n  Exec results: {exec_result}")
    
    if state.get("show_node_info"):
        print(f'  Reviewer result:\n    {state["review"].replace("\n", "\n    ")}\n')
    
    return state


def refinement_node(state: AgentState) -> AgentState:
    print("\n>> REFINEMENT NODE")

    # EARLY EXIT if code is already correct
    if ("review" in state and "Code is correct" in state["review"]):
        print("  Code already correct. Skipping refinement.\n")
        return state

    max_refinements = 3
    refinement_count = state.get("refinement_count", 0)

    while refinement_count < max_refinements:
        refinement_count += 1
        state["refinement_count"] = refinement_count
        print(f"  Refinement: {refinement_count}/{max_refinements}\n")

        raw_code = refine_code(
            code=state["code"],
            review=state["review"],
            model=state["model"],
        )

        # Refiner MUST output pure Python
        refined_code = extract_python_code(raw_code)
        state["code"] = refined_code

        # Re-execute refined code
        exec_result = execute_code(refined_code)
        state["exec_result"] = exec_result

        # Recompute quality metrics for refined code
        metrics = compute_quality_metrics(refined_code)
        state["quality_metrics"] = metrics

        # Re-run reviewer after refinement
        review = review_code(
            code=refined_code,
            exec_result=exec_result,
            model=state["model"],
            quality_metrics=metrics,
        )
        state["review"] = review

        # Decide outcome based on reviewer verdict, not exec alone
        if "Code is correct" in review:
            print("  Refinement successful: code is correct.\n")
            return state
        else:
            print("  Refinement incomplete: issues remain.")
    
    print("  Maximum refinements reached. Ending refinement.\n")

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
