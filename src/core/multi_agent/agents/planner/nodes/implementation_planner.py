from src.core.multi_agent.agents.planner.state import AgentState
from src.core.llm import call_llm
from src.core.multi_agent.agents.planner.llm import (
    IMPLEMENTATION_PLANNER_PROMPT,
    extract_and_parse_json,
    compress_phase_output,
)
import json

def implementation_planning_node(state: AgentState) -> AgentState:
    """
    Create detailed step-by-step implementation guidance.
    """
    print("\n  - PHASE 4: IMPLEMENTATION PLANNING")

    # Get compressed summaries
    intent_summary = compress_phase_output("intent_analysis", state.get("intent_analysis", {}))
    requirements_summary = compress_phase_output("requirements", state.get("requirements", {}))
    architecture_summary = compress_phase_output("architecture", state.get("architecture", {}))

    user_prompt = f"""## Task: {state.get('task_id', 'N/A')}
User Request: {state.get('user_request', 'N/A')}

## Context
{intent_summary}

{requirements_summary}

## Architecture to Implement
{architecture_summary}

## Your Mission
Create detailed step-by-step implementation guidance for the coder agent.

1. Determine implementation order (respect dependencies)
2. Break each component into atomic implementation steps
3. Specify exact input validation checks
4. Define error handling (when to raise, what messages)
5. Provide code guidance (specific approach for each step)

## Instructions
Think through the implementation sequence in <thinking> tags.
Consider what a coder needs to know at each step.

CRITICAL: You MUST wrap your final JSON output in <output></output> tags like this:
<output>
{{
  "your": "json",
  "goes": "here"
}}
</output>

Do NOT output raw JSON without the <output> tags. This will cause parsing failures.

## Guidelines
- Each step should be implementable in ~5-10 lines of code
- Provide specific validation expressions (not just "validate input")
- Include exact exception types and error messages
- Mention edge cases that need special handling
- Use type hints and descriptive names
"""

    response = call_llm(
        user_prompt=user_prompt,
        system_prompt=IMPLEMENTATION_PLANNER_PROMPT,
        model=state["model"],
    )

    try:
        implementation_plan = extract_and_parse_json(response)
        state["implementation_plan"] = implementation_plan

        if state.get("show_node_info"):
            components = implementation_plan.get("components", [])
            print(f"    Implementation Components: {len(components)}")
            total_steps = sum(len(c.get("steps", [])) for c in components)
            print(f"    Total Implementation Steps: {total_steps}")

    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        state["implementation_plan"] = {"raw_response": response, "error": str(e)}
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Implementation plan JSON parse failed: {str(e)}")

    return state
