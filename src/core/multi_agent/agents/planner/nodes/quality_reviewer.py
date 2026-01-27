from src.core.multi_agent.agents.planner.state import AgentState
from src.core.llm import call_llm
from src.core.multi_agent.agents.planner.llm import (
    PLAN_QUALITY_REVIEWER_PROMPT,
    extract_and_parse_json,
    compress_phase_output,
)
import json


def quality_review_node(state: AgentState) -> AgentState:
    """
    Review complete PLAN for quality before handoff to coder agent.
    """
    print("\n  - PHASE 5: PLAN QUALITY REVIEW")

    complete_plan = {
        "intent": compress_phase_output(
            "intent_analysis", state.get("intent_analysis", {})
        ),
        "requirements": compress_phase_output(
            "requirements", state.get("requirements", {})
        ),
        "architecture": compress_phase_output(
            "architecture", state.get("architecture", {})
        ),
        "implementation": compress_phase_output(
            "implementation", state.get("implementation_plan", {})
        ),
    }

    plan_summary = json.dumps(complete_plan, indent=2)

    user_prompt = f"""## Task
Review this complete PLAN for production readiness.

## Complete Plan
{plan_summary}

## Your Mission
Validate that this plan is comprehensive enough for a coder agent to implement production-grade code without questions.

## Review Checklist
1. **Completeness** (Score 0-10): Does it address all requirements?
2. **Clarity**: Can a coder implement without ambiguity?
3. **Robustness**: Are error handling strategies well-defined?
4. **Feasibility**: Are architectural decisions realistic?
5. **Readiness**: Is this ready for handoff to coder agent?

## Instructions
Think critically in <thinking> tags about gaps and issues.
Then provide your review in <output> tags as JSON.

## Approval Criteria (Be Pragmatic)
- Score >= 6 AND no CRITICAL blockers: APPROVED ✓
- Score < 6 OR critical blockers exist: NEEDS_REVISION

## What Counts as CRITICAL?
- Missing core functional requirements
- Fundamentally flawed algorithm choice
- Completely unclear implementation steps

## NOT Critical (minor issues are OK):
- Missing minor edge cases (coder can handle)
- Could be more detailed (good enough is fine)
- Minor optimization opportunities

## Important
Only request revision for CRITICAL issues. The coder agent is capable and will handle details.
If you find issues, specify which phase needs revision:
- "requirements_engineering": Wrong requirements or missing constraints
- "architecture_design": Flawed component design or algorithm choice
- "implementation_planning": Completely unclear steps

Remember: You are reviewing the PLAN (not code). The coder agent generates code later and can fill gaps.
"""

    response = call_llm(
        user_prompt=user_prompt,
        system_prompt=PLAN_QUALITY_REVIEWER_PROMPT,
        model=state["model"],
    )

    try:
        quality_review = extract_and_parse_json(response)
        state["quality_review"] = quality_review

        approval_status = quality_review.get("approval_status", "needs_revision")
        completeness = quality_review.get("completeness_score", 0)
        issues = quality_review.get("issues", [])

        # Count critical issues
        critical_issues = [i for i in issues if i.get("severity") == "critical"]

        # Auto-approve on final iteration to prevent infinite loops
        current_iteration = state.get("iteration_count", 0)
        if current_iteration >= 2:
            approval_status = "approved"
            is_approved = True
            if state.get("show_node_info"):
                print(f"    Auto-approving (max iterations reached)")
        # Override: auto-approve if score >= 6 and no critical issues
        elif completeness >= 6 and len(critical_issues) == 0:
            approval_status = "approved"
            is_approved = True
        else:
            is_approved = approval_status == "approved"

        if state.get("show_node_info"):
            print(f"    Completeness Score: {completeness}/10")
            print(f"    Critical Issues: {len(critical_issues)}/{len(issues)}")
            if critical_issues:
                for issue in critical_issues[:2]:  # Show top 2 critical
                    print(f"      - [CRITICAL] {issue.get('description')[:60]}...")
            print(f"    {'✓ APPROVED' if is_approved else '✗ NEEDS REVISION'}")
        state["plan_approved"] = is_approved

        # Increment iteration count if not approved
        if not is_approved:
            current_count = state.get("iteration_count", 0)
            state["iteration_count"] = current_count + 1

    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        state["quality_review"] = {"raw_response": response, "error": str(e)}
        state["plan_approved"] = False
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Quality review JSON parse failed: {str(e)}")

    return state
