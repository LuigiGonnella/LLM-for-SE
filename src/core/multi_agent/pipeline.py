"""
Multi-agent LangGraph pipeline.

Flow:
Planner -> Coder -> Eval -> (if pass/acceptable -> END) else Critic -> Coder -> Eval -> ...

Agents do NOT see test files.
Only exec_result summary is provided.
"""

from langgraph.graph import StateGraph, START, END

from src.core.state import AgentState
from src.core.agents.planner import plan_task
from src.core.agents.coder import generate_code
from src.core.agents.critic import critique

from src.tools.executor import run_tests  # adjust if your executor function name differs
from src.evaluation.quality import compute_quality_metrics  # adjust if differs


def _exec_summary(exec_result: dict | None) -> str | None:
    if not exec_result:
        return None
    # Keep it short: do not leak test contents, only errors/trace.
    parts = [
        f"passed={exec_result.get('passed')}",
        f"error_type={exec_result.get('error_type')}",
        f"error_message={exec_result.get('error_message')}",
    ]
    return ", ".join([p for p in parts if p and "None" not in p])


def planner_node(state: AgentState) -> AgentState:
    state["plan"] = plan_task(
        signature=state["signature"],
        docstring=state["docstring"],
        model=state["model"],
    )
    return state


def coder_node(state: AgentState) -> AgentState:
    state["code"] = generate_code(
        signature=state["signature"],
        plan=state["plan"],
        model=state["model"],
        critic_feedback=state.get("feedback"),
        exec_summary=_exec_summary(state.get("exec_result")),
    )
    return state


def eval_node(state: AgentState) -> AgentState:
    # NOTE: test_file should be provided by the runner, but never shown to agents
    test_file = state.get("test_file")
    if not test_file:
        raise ValueError("State missing 'test_file' for evaluation (executor needs it).")

    # Functional correctness
    exec_result = run_tests(code=state["code"], test_file=str(test_file))
    state["exec_result"] = exec_result

    # Code quality metrics
    state["quality_metrics"] = compute_quality_metrics(state["code"])

    return state


def critic_node(state: AgentState) -> AgentState:
    state["feedback"] = critique(
        signature=state["signature"],
        docstring=state["docstring"],
        plan=state["plan"],
        code=state["code"],
        model=state["model"],
        exec_summary=_exec_summary(state.get("exec_result")),
        quality_metrics=state.get("quality_metrics"),
    )
    return state


def should_stop(state: AgentState) -> str:
    """
    Decide whether to stop after eval, or loop through critic->coder again.
    Minimal-cost policy:
    - Stop if tests passed
    - Else, loop until max iterations
    Optionally add quality thresholds later.
    """
    exec_result = state.get("exec_result") or {}
    passed = bool(exec_result.get("passed"))

    if passed:
        return "end"

    it = int(state.get("iteration", 0))
    max_it = int(state.get("max_iterations", 2))
    if it >= max_it:
        return "end"

    return "critic"


def increment_iteration(state: AgentState) -> AgentState:
    state["iteration"] = int(state.get("iteration", 0)) + 1
    return state


def build_multi_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("eval", eval_node)
    graph.add_node("critic", critic_node)
    graph.add_node("inc_iter", increment_iteration)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "eval")

    # After eval, decide to stop or critique
    graph.add_conditional_edges(
        "eval",
        should_stop,
        {
            "critic": "critic",
            "end": END,
        },
    )

    # If critique, increment iteration and go back to coder
    graph.add_edge("critic", "inc_iter")
    graph.add_edge("inc_iter", "coder")

    return graph.compile()
