"""
Multi-Node Planner Agent Pipeline

Architecture: 5-phase specialized planning workflow
- Each node has a single, focused responsibility
- Phases build on each other progressively
- Quality gate ensures plan approval before output
- Optional refinement loop for failing plans

Flow:
  START → Intent Analysis → Requirements Engineering → Architecture Design
    → Implementation Planning → Quality Review → [approved?]
      ├─ YES → Consolidation → END
      └─ NO → [retry < max?]
          ├─ YES → Architecture Design (with feedback)
          └─ NO → END (with best effort plan)

Benefits over single-node approach:
- Higher specialization = better prompt focus
- Incremental validation at each phase
- Clear separation of concerns
- Easier debugging and monitoring
- Modular refinement (can retry specific phases)
"""

from langgraph.graph import StateGraph, START, END
from src.core.multi_agent.agents.planner.state import AgentState
from src.core.multi_agent.agents.planner.llm import (
    call_llm,
    extract_and_parse_json,
    get_model_profile,
    compress_phase_output,
    INTENT_ANALYZER_PROMPT,
    REQUIREMENTS_ENGINEER_PROMPT,
    ARCHITECTURE_DESIGNER_PROMPT,
    IMPLEMENTATION_PLANNER_PROMPT,
    PLAN_QUALITY_REVIEWER_PROMPT,
)
import json
from typing import Dict, Any


# ═══════════════════════════════════════════════════════════════════════
# NODE 1: INTENT ANALYZER
# ═══════════════════════════════════════════════════════════════════════

def intent_analysis_node(state: AgentState) -> AgentState:
    """
    Extract core intent, classify task, identify success metrics.
    
    This is the foundation - understanding what the user truly needs.
    """
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  PHASE 1: INTENT ANALYSIS                                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
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
        node_name="intent",
    )
    
    try:
        intent_analysis = extract_and_parse_json(response)
        state["intent_analysis"] = intent_analysis
        
        if state.get("show_node_info"):
            print(f"\n📋 Intent: {intent_analysis.get('intent', 'N/A')}")
            print(f"🏷️  Task Type: {intent_analysis.get('task_type', 'N/A')}")
            print(f"🎯 Domain: {intent_analysis.get('domain', 'N/A')}")
            print(f"✓  Assumptions: {len(intent_analysis.get('assumptions', []))}")
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error: {e}")
        state["intent_analysis"] = {"raw_response": response, "error": str(e)}
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Intent analysis JSON parse failed: {str(e)}")
    
    return state


# ═══════════════════════════════════════════════════════════════════════
# NODE 2: REQUIREMENTS ENGINEER
# ═══════════════════════════════════════════════════════════════════════

def requirements_engineering_node(state: AgentState) -> AgentState:
    """
    Define comprehensive functional and non-functional requirements.
    
    Transforms intent into concrete, testable specifications.
    """
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  PHASE 2: REQUIREMENTS ENGINEERING                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Use compression for 7B models
    profile = get_model_profile(state["model"])
    if profile["compress_context"]:
        intent_summary = compress_phase_output("intent_analysis", state.get("intent_analysis", {}))
    else:
        intent_summary = json.dumps(state.get("intent_analysis", {}), indent=2)
    
    user_prompt = f"""## Task
Transform the following intent into comprehensive requirements.

## Intent Analysis
{intent_summary}

## Your Mission
1. Define functional requirements (what the code must do)
2. Specify non-functional requirements (performance, security, reliability)
3. List constraints (technical and business)
4. Identify edge cases and boundary conditions

## Instructions
Think step-by-step in <thinking> tags about what requirements are needed.
Then provide complete requirements in <output> tags as JSON.

## Remember
- Be specific with O(n) complexity bounds
- List exact input validation checks
- Consider security implications
- Think about failure scenarios
"""
    
    response = call_llm(
        user_prompt=user_prompt,
        system_prompt=REQUIREMENTS_ENGINEER_PROMPT,
        model=state["model"],
        node_name="requirements",
    )
    
    try:
        requirements = extract_and_parse_json(response)
        state["requirements"] = requirements
        
        if state.get("show_node_info"):
            func_count = len(requirements.get("functional", []))
            edge_count = len(requirements.get("edge_cases", []))
            print(f"\n📝 Functional Requirements: {func_count}")
            print(f"⚡ Performance Constraints: {requirements.get('non_functional', {}).get('performance', {})}")
            print(f"🔒 Security Requirements: {len(requirements.get('non_functional', {}).get('security', []))}")
            print(f"🧪 Edge Cases Identified: {edge_count}")
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error: {e}")
        state["requirements"] = {"raw_response": response, "error": str(e)}
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Requirements JSON parse failed: {str(e)}")
    
    return state


# ═══════════════════════════════════════════════════════════════════════
# NODE 3: ARCHITECTURE DESIGNER
# ═══════════════════════════════════════════════════════════════════════

def architecture_design_node(state: AgentState) -> AgentState:
    """
    Design optimal architecture: components, patterns, data structures.
    
    This is the technical blueprint for implementation.
    """
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  PHASE 3: ARCHITECTURE DESIGN                            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Use compression for 7B models
    profile = get_model_profile(state["model"])
    if profile["compress_context"]:
        requirements_summary = compress_phase_output("requirements", state.get("requirements", {}))
    else:
        requirements_summary = json.dumps(state.get("requirements", {}), indent=2)
    
    # Include feedback from quality review if this is a refinement iteration
    feedback_section = ""
    if state.get("quality_review") and state.get("iteration_count", 0) > 0:
        quality_review = state.get("quality_review", {})
        issues = quality_review.get("issues", [])
        if issues:
            issues_text = "\n".join([f"- [{i['severity']}] {i['description']}: {i['recommendation']}" 
                                     for i in issues[:5]])
            feedback_section = f"""

## Quality Review Feedback (Iteration {state.get('iteration_count', 0)})
The previous architecture had these issues:
{issues_text}

Please address these in your revised design.
"""
    
    user_prompt = f"""## Task
Design the optimal architecture to satisfy these requirements.

## Requirements
{requirements_summary}
{feedback_section}

## Your Mission
1. Decompose into single-responsibility components
2. Select appropriate design patterns with justification
3. Choose optimal data structures with O(n) analysis
4. Recommend specific algorithms
5. Design exception hierarchy
6. Define clear component interfaces

## Instructions
Think through design alternatives in <thinking> tags.
Consider trade-offs (performance vs complexity, memory vs speed).
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
        temperature=0.15,  # Slightly higher for creative design
        max_tokens=4096,
    )
    
    try:
        architecture = json.loads(response)
        state["architecture"] = architecture
        
        if state.get("show_node_info"):
            components = architecture.get("components", [])
            print(f"\n🏗️  Components Designed: {len(components)}")
            for comp in components[:3]:  # Show first 3
                print(f"   • {comp.get('name')}: {comp.get('responsibility')}")
            print(f"📐 Design Patterns: {len(architecture.get('exception_hierarchy', []))}")
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error: {e}")
        state["architecture"] = {"raw_response": response, "error": str(e)}
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Architecture JSON parse failed: {str(e)}")
    
    return state


# ═══════════════════════════════════════════════════════════════════════
# NODE 4: IMPLEMENTATION PLANNER
# ═══════════════════════════════════════════════════════════════════════

def implementation_planning_node(state: AgentState) -> AgentState:
    """
    Create detailed step-by-step implementation guidance.
    
    This gives the coder agent exact instructions for building the solution.
    """
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  PHASE 4: IMPLEMENTATION PLANNING                        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Use compression for 7B models
    profile = get_model_profile(state["model"])
    if profile["compress_context"]:
        architecture_summary = compress_phase_output("architecture", state.get("architecture", {}))
    else:
        architecture_summary = json.dumps(state.get("architecture", {}), indent=2)
    
    user_prompt = f"""## Task
Create detailed step-by-step implementation guidance for this architecture.

## Architecture
{architecture_summary}

## Your Mission
1. Determine implementation order (respect dependencies)
2. Break each component into atomic implementation steps
3. Specify exact input validation checks
4. Define error handling (when to raise, what messages)
5. Provide code guidance (specific approach for each step)

## Instructions
Think through the implementation sequence in <thinking> tags.
Consider what a coder needs to know at each step.
Then provide the complete plan in <output> tags as JSON.

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
        node_name="implementation",
    )
    
    try:
        implementation_plan = extract_and_parse_json(response)
        state["implementation_plan"] = implementation_plan
        
        if state.get("show_node_info"):
            components = implementation_plan.get("components", [])
            print(f"\n📋 Implementation Components: {len(components)}")
            total_steps = sum(len(c.get("steps", [])) for c in components)
            print(f"⚙️  Total Implementation Steps: {total_steps}")
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error: {e}")
        state["implementation_plan"] = {"raw_response": response, "error": str(e)}
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Implementation plan JSON parse failed: {str(e)}")
    
    return state


# ═══════════════════════════════════════════════════════════════════════
# NODE 5: PLAN QUALITY REVIEWER
# ═══════════════════════════════════════════════════════════════════════

def quality_review_node(state: AgentState) -> AgentState:
    """
    Review complete PLAN for quality before handoff to coder agent.
    
    This validates the plan is comprehensive enough for the coder agent
    to implement production-grade code without ambiguity.
    
    Acts as quality gate - plan must be approved to proceed to coder.
    """
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  PHASE 5: PLAN QUALITY REVIEW                            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Use compression for 7B models - critical here as context is largest
    profile = get_model_profile(state["model"])
    if profile["compress_context"]:
        complete_plan = {
            "intent": compress_phase_output("intent_analysis", state.get("intent_analysis", {})),
            "requirements": compress_phase_output("requirements", state.get("requirements", {})),
            "architecture": compress_phase_output("architecture", state.get("architecture", {})),
            "implementation": compress_phase_output("implementation", state.get("implementation_plan", {})),
        }
    else:
        complete_plan = {
            "intent": state.get("intent_analysis"),
            "requirements": state.get("requirements"),
            "architecture": state.get("architecture"),
            "implementation": state.get("implementation_plan"),
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

## Approval Criteria
- Score >= 8 AND all critical issues resolved: APPROVED
- Score < 8 OR critical issues remain: NEEDS_REVISION

## Important
If you find issues, specify which phase needs revision:
- "requirements_engineering": Wrong requirements or missing constraints
- "architecture_design": Flawed component design or algorithm choice
- "implementation_planning": Unclear steps or missing validations

You are reviewing the PLAN (not code). The coder agent generates code later.
"""
    
    response = call_llm(
        user_prompt=user_prompt,
        system_prompt=PLAN_QUALITY_REVIEWER_PROMPT,
        model=state["model"],
        node_name="quality",
    )
    
    try:
        quality_review = extract_and_parse_json(response)
        state["quality_review"] = quality_review
        
        approval_status = quality_review.get("approval_status", "needs_revision")
        completeness = quality_review.get("completeness_score", 0)
        issues = quality_review.get("issues", [])
        
        if state.get("show_node_info"):
            print(f"\n📊 Completeness Score: {completeness}/10")
            print(f"🔍 Issues Found: {len(issues)}")
            for issue in issues[:3]:  # Show top 3
                print(f"   [{issue.get('severity')}] {issue.get('description')[:60]}...")
            print(f"\n{'✅ APPROVED' if approval_status == 'approved' else '⚠️  NEEDS REVISION'}")
        
        state["plan_approved"] = (approval_status == "approved")
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error: {e}")
        state["quality_review"] = {"raw_response": response, "error": str(e)}
        state["plan_approved"] = False
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Quality review JSON parse failed: {str(e)}")
    
    return state


# ═══════════════════════════════════════════════════════════════════════
# NODE 6: CONSOLIDATION
# ═══════════════════════════════════════════════════════════════════════

def consolidation_node(state: AgentState) -> AgentState:
    """
    Consolidate all planning phases into final unified plan.
    
    This creates the complete output for the coder agent.
    """
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  CONSOLIDATION: Final Plan Assembly                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    final_plan = {
        "task_id": state.get("task_id"),
        "user_request": state.get("user_request"),
        "intent": state.get("intent_analysis"),
        "requirements": state.get("requirements"),
        "architecture": state.get("architecture"),
        "implementation": state.get("implementation_plan"),
        "quality_review": state.get("quality_review"),
        "approved": state.get("plan_approved", False),
        "iterations": state.get("iteration_count", 0),
    }
    
    state["final_plan"] = final_plan
    
    if state.get("show_node_info"):
        print("\n✨ Final plan assembled")
        print(f"📦 Components: {len(final_plan.get('architecture', {}).get('components', []))}")
        print(f"🔄 Iterations: {final_plan.get('iterations', 0)}")
        print(f"{'✅ Status: APPROVED' if final_plan.get('approved') else '⚠️  Status: BEST EFFORT'}")
    
    return state


# ═══════════════════════════════════════════════════════════════════════
# ROUTING LOGIC
# ═══════════════════════════════════════════════════════════════════════

def should_refine(state: AgentState) -> str:
    """
    Decide whether to refine the plan or proceed to consolidation.
    Now supports targeted refinement to specific phases.
    
    Logic:
    - If plan approved: → consolidation
    - If iterations < 2 and not approved: → retry_phase (from quality review)
    - If iterations >= 2: → consolidation (best effort)
    """
    plan_approved = state.get("plan_approved", False)
    iteration_count = state.get("iteration_count", 0)
    
    if plan_approved:
        print("\n✅ Plan approved! Proceeding to consolidation.")
        return "consolidation"
    
    if iteration_count < 2:
        quality_review = state.get("quality_review", {})
        retry_phase = quality_review.get("retry_phase", "architecture_design")
        
        # Validate retry_phase
        valid_phases = ["requirements_engineering", "architecture_design", "implementation_planning"]
        if retry_phase not in valid_phases:
            retry_phase = "architecture_design"  # Default fallback
        
        print(f"\n⚠️  Plan needs revision. Retrying from {retry_phase} (iteration {iteration_count + 1}/2)")
        state["iteration_count"] = iteration_count + 1
        return retry_phase
    
    print("\n⚠️  Max iterations reached. Proceeding with best-effort plan.")
    return "consolidation"


# ═══════════════════════════════════════════════════════════════════════
# GRAPH BUILDER
# ═══════════════════════════════════════════════════════════════════════

def build_planner_graph():
    """
    Build the multi-node planner agent graph.
    
    Architecture:
    - 5 specialized planning nodes
    - Quality gate with refinement loop
    - Consolidation for final output
    
    Returns:
        Compiled LangGraph
    """
    graph = StateGraph(AgentState)
    
    # Add all nodes
    graph.add_node("intent_analysis", intent_analysis_node)
    graph.add_node("requirements_engineering", requirements_engineering_node)
    graph.add_node("architecture_design", architecture_design_node)
    graph.add_node("implementation_planning", implementation_planning_node)
    graph.add_node("quality_review", quality_review_node)
    graph.add_node("consolidation", consolidation_node)
    
    # Define flow
    graph.add_edge(START, "intent_analysis")
    graph.add_edge("intent_analysis", "requirements_engineering")
    graph.add_edge("requirements_engineering", "architecture_design")
    graph.add_edge("architecture_design", "implementation_planning")
    graph.add_edge("implementation_planning", "quality_review")
    
    # Conditional routing after quality review
    graph.add_conditional_edges(
        "quality_review",
        should_refine,
        {
            "requirements_engineering": "requirements_engineering",  # Retry from requirements
            "architecture_design": "architecture_design",  # Retry from architecture
            "implementation_planning": "implementation_planning",  # Retry from implementation
            "consolidation": "consolidation",  # Proceed to final
        }
    )
    
    graph.add_edge("consolidation", END)
    
    return graph.compile()

