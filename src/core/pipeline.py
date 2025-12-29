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

    # Compute quality metrics
    metrics = compute_quality_metrics(state["code"])
    state["quality_metrics"] = metrics
    print(format_metrics_report(metrics))

    state["review"] = review_code(
        code=state["code"],
        model=state["model"],
        exec_result=exec_result,
        quality_metrics=metrics,
    )

    print(f"Exec results: {exec_result}")
    print(f'Reviewer result: {state["review"].splitlines()[-1]}')
    return state


def refine_step(code: str, review: str, model: str) -> str:
    """
    Single refinement step: call LLM to refine code based on review.
    Returns extracted Python code.
    """
    raw_code = refine_code(
        code=code,
        review=review,
        model=model,
    )
    return extract_python_code(raw_code)


def evaluate_refined_code(code: str, model: str) -> tuple[dict, str]:
    """
    Evaluate refined code: execute and get review (without metrics).
    Returns (exec_result, review).
    """
    exec_result = execute_code(code)
    review = review_code(
        code=code,
        exec_result=exec_result,
        model=model,
        quality_metrics=None,
    )
    return exec_result, review


def should_continue_refining(review: str, refinement_count: int, max_refinements: int) -> bool:
    """
    Determine if we should continue refining.
    Returns False if code is correct or max refinements reached.
    """
    if "Code is correct" in review and refinement_count >= 1:
        return False
    if refinement_count >= max_refinements:
        return False
    return True


def refinement_node(state: AgentState) -> AgentState:
    print(">> REFINEMENT NODE")

    max_refinements = 3
    refinement_count = state.get("refinement_count", 0)

    while refinement_count < max_refinements:
        if refinement_count < max_refinements:
            print(f"starting refinement {refinement_count+1}/{max_refinements}\n")

        # Step 1: Refine the code
        refined_code = refine_step(
            code=state["code"],
            review=state["review"],
            model=state["model"],
        )

        # Step 2: Evaluate the refined code (no metrics yet)
        exec_result, review = evaluate_refined_code(
            code=refined_code,
            model=state["model"],
        )

        # Step 3: Update state (no metrics yet)
        state["code"] = refined_code
        state["exec_result"] = exec_result
        state["review"] = review
        refinement_count += 1
        state["refinement_count"] = refinement_count

        # Step 4: Decide whether to continue
        if not should_continue_refining(review, refinement_count, max_refinements):
            # Only compute metrics on final iteration
            metrics = compute_quality_metrics(refined_code)
            state["quality_metrics"] = metrics
            
            if "Code is correct" in review:
                print("Refinement successful: code is correct.")
            else:
                print("Maximum refinements reached. Ending refinement.")
            return state
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
