from src.core.multi_agent.agents.planner.state import AgentState
from src.core.llm import call_llm
from src.core.multi_agent.agents.planner.llm import (
    ARCHITECTURE_DESIGNER_PROMPT,
    extract_and_parse_json,
    compress_phase_output,
)
import json


def architecture_design_node(state: AgentState) -> AgentState:
    """
    Design optimal architecture: components, patterns, data structures.
    """
    print("\n  - PHASE 3: ARCHITECTURE DESIGN")

    # Get task context
    intent_summary = compress_phase_output(
        "intent_analysis", state.get("intent_analysis", {})
    )
    requirements_summary = compress_phase_output(
        "requirements", state.get("requirements", {})
    )

    # Include feedback from quality review if this is a refinement iteration
    feedback_section = ""
    if state.get("quality_review") and state.get("iteration_count", 0) > 0:
        quality_review = state.get("quality_review", {})
        issues = quality_review.get("issues", [])
        if issues:
            issues_text = "\n".join(
                [
                    f"- [{i['severity']}] {i['description']}: {i['recommendation']}"
                    for i in issues[:5]
                ]
            )
            feedback_section = f"""

## Quality Review Feedback (Iteration {state.get('iteration_count', 0)})
The previous architecture had these issues:
{issues_text}

Please address these in your revised design.
"""

    user_prompt = f"""## Task: {state.get('task_id', 'N/A')}
User Request: {state.get('user_request', 'N/A')}

## Context
{intent_summary}

## Requirements to Satisfy
{requirements_summary}
{feedback_section}

## Your Mission
Design the SIMPLEST architecture that satisfies requirements.

IMPORTANT - Architecture Complexity Guidelines:
- For simple algorithms (FizzBuzz, sum, filter): Usually ONE component (the main function)
- For moderate tasks (sorting, search): 2-3 components maximum
- For complex systems (parsers, games): Multiple components with clear separation

DO NOT over-engineer! Avoid factory patterns, abstract classes, or multiple components unless genuinely needed.

Your Design Tasks:
1. Identify components (prefer 1-2 for simple problems)
2. Choose appropriate design pattern ONLY if it simplifies the solution
3. Select optimal data structures with O(n) analysis
4. Recommend specific algorithm approach
5. Define exception handling strategy
6. Specify component interfaces (function signatures)

## Instructions
Think through design alternatives in <thinking> tags.
Ask yourself: "Is this the SIMPLEST solution that works?"
Then provide your architecture in <output> tags as JSON.

## Design Principles
- Single Responsibility Principle
- Fail-fast with clear error messages
- Optimize for the common case
- Use standard library where possible
"""

    response = call_llm(
        user_prompt=user_prompt,
        system_prompt=ARCHITECTURE_DESIGNER_PROMPT,
        model=state["model"],
    )

    try:
        architecture = extract_and_parse_json(response)
        state["architecture"] = architecture

        if state.get("show_node_info"):
            components = architecture.get("components", [])
            print(f"    Components Designed: {len(components)}")
            for comp in components[:3]:  # Show first 3
                print(f"      - {comp.get('name')}: {comp.get('responsibility')}")
            print(
                f"    Design Patterns: {len(architecture.get('exception_hierarchy', []))}"
            )

    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        state["architecture"] = {"raw_response": response, "error": str(e)}
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Architecture JSON parse failed: {str(e)}")

    return state
