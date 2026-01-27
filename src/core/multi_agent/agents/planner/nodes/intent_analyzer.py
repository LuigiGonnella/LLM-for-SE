from src.core.multi_agent.agents.planner.state import AgentState
from src.core.llm import call_llm
from src.core.multi_agent.agents.planner.llm import (
    INTENT_ANALYZER_PROMPT,
    extract_and_parse_json,
)
import json


def intent_analysis_node(state: AgentState) -> AgentState:
    """
    Extract core intent, classify task, identify success metrics.
    """
    print("\n  - PHASE 1: INTENT ANALYSIS")

    user_prompt = f"""## Task
Analyze the following user request and extract the true intent.

## User Request
{state['user_request']}

## Your Mission
1. Extract the core intent (what problem is being solved)
2. Classify the task type (algorithm, data_processing, api, utility, script)
3. Identify success metrics (how we know it works)
4. Note any assumptions you must make

## Instructions
Think step-by-step in <thinking> tags, then provide your analysis in <output> tags as JSON matching the schema.
"""

    response = call_llm(
        user_prompt=user_prompt,
        system_prompt=INTENT_ANALYZER_PROMPT,
        model=state["model"],
    )

    try:
        intent_analysis = extract_and_parse_json(response)
        state["intent_analysis"] = intent_analysis

        if state.get("show_node_info"):
            print(f"    Intent: {intent_analysis.get('intent', 'N/A')}")
            print(f"    Task Type: {intent_analysis.get('task_type', 'N/A')}")
            print(f"    Domain: {intent_analysis.get('domain', 'N/A')}")
            print(f"    Assumptions: {len(intent_analysis.get('assumptions', []))}")

    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        state["intent_analysis"] = {"raw_response": response, "error": str(e)}
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Intent analysis JSON parse failed: {str(e)}")

    return state
