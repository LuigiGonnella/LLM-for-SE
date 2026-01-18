"""
Planner Agent - High-level interface for the multi-node planner.

This module provides a clean API for using the SOTA planner agent.
"""

from src.core.multi_agent.agents.planner.pipeline import build_planner_graph
from src.core.multi_agent.agents.planner.state import AgentState
from typing import Dict, Any, Optional
import json


class PlannerAgent:
    """
    High-level interface for the SOTA multi-node planner agent.
    
    Usage:
        planner = PlannerAgent(model="llama3.1:70b")
        plan = planner.create_plan(
            task_id="task_001",
            user_request="Create a function that validates email addresses",
            verbose=True
        )
        
        if plan["approved"]:
            print("Plan approved! Ready for coder agent.")
        else:
            print("Best-effort plan created.")
    """
    
    def __init__(self, model: str = "mistral"):
        """
        Initialize the planner agent.
        
        Args:
            model: Ollama model to use for planning
        """
        self.model = model
        self.graph = build_planner_graph()
    
    def create_plan(
        self,
        task_id: str,
        user_request: str,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a comprehensive implementation plan from a user request.
        
        Args:
            task_id: Unique identifier for this task
            user_request: The user's request/task description
            verbose: Whether to show detailed node outputs
        
        Returns:
            Dict containing the final plan with keys:
                - intent: Intent analysis
                - requirements: Requirements specification
                - architecture: Architecture design
                - implementation: Implementation guidance
                - quality_review: Quality assessment
                - approved: Boolean indicating plan approval
                - iterations: Number of refinement iterations
        
        Raises:
            RuntimeError: If planning fails critically
            ConnectionError: If cannot connect to Ollama
        """
        initial_state: AgentState = {
            "task_id": task_id,
            "user_request": user_request,
            "model": self.model,
            "show_node_info": verbose,
            "intent_analysis": None,
            "requirements": None,
            "architecture": None,
            "implementation_plan": None,
            "quality_review": None,
            "final_plan": None,
            "plan_approved": None,
            "iteration_count": 0,
            "errors": [],
        }
        
        try:
            result = self.graph.invoke(initial_state)
            return result.get("final_plan", {})
        
        except Exception as e:
            raise RuntimeError(f"Planning failed: {str(e)}") from e
    
    def export_plan_json(self, plan: Dict[str, Any], filepath: str) -> None:
        """
        Export plan to JSON file.
        
        Args:
            plan: The plan dict returned from create_plan()
            filepath: Path where to save the JSON file
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
    
    def get_plan_summary(self, plan: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of the plan.
        
        Args:
            plan: The plan dict returned from create_plan()
        
        Returns:
            Formatted string summary
        """
        intent = plan.get("intent", {})
        requirements = plan.get("requirements", {})
        architecture = plan.get("architecture", {})
        implementation = plan.get("implementation", {})
        quality = plan.get("quality_review", {})
        
        summary = f"""
╔══════════════════════════════════════════════════════════════════╗
║                      PLAN SUMMARY                                ║
╚══════════════════════════════════════════════════════════════════╝

📋 TASK: {plan.get('task_id', 'N/A')}

🎯 INTENT
   Problem: {intent.get('intent', 'N/A')}
   Type: {intent.get('task_type', 'N/A')}
   Domain: {intent.get('domain', 'N/A')}

📝 REQUIREMENTS
   Functional: {len(requirements.get('functional', []))} requirements
   Performance: {requirements.get('non_functional', {}).get('performance', {}).get('time_complexity', 'N/A')}
   Edge Cases: {len(requirements.get('edge_cases', []))} identified

🏗️ ARCHITECTURE
   Components: {len(architecture.get('components', []))}
   Design Patterns: {len(architecture.get('exception_hierarchy', []))} exception types

⚙️ IMPLEMENTATION
   Steps: {sum(len(c.get('steps', [])) for c in implementation.get('components', []))}
   Test Cases: {sum(len(c.get('test_cases', [])) for c in implementation.get('components', []))}

🔍 QUALITY
   Score: {quality.get('completeness_score', 0)}/10
   Issues: {len(quality.get('issues', []))}
   Status: {'✅ APPROVED' if plan.get('approved') else '⚠️ NEEDS WORK'}
   
🔄 ITERATIONS: {plan.get('iterations', 0)}

{'✅ This plan is production-ready!' if plan.get('approved') else '⚠️ This is a best-effort plan.'}
╚══════════════════════════════════════════════════════════════════╝
"""
        return summary


# ═══════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def plan_task(
    user_request: str,
    task_id: Optional[str] = None,
    model: str = "mistral",
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to quickly create a plan.
    
    Args:
        user_request: The task description
        task_id: Optional task ID (auto-generated if not provided)
        model: Ollama model to use
        verbose: Whether to show node outputs
    
    Returns:
        Complete plan dictionary
    """
    import uuid
    
    if task_id is None:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    planner = PlannerAgent(model=model)
    return planner.create_plan(
        task_id=task_id,
        user_request=user_request,
        verbose=verbose,
    )


def plan_and_summarize(
    user_request: str,
    model: str = "mistral",
) -> str:
    """
    Create a plan and return a formatted summary.
    
    Args:
        user_request: The task description
        model: Ollama model to use
    
    Returns:
        Human-readable summary string
    """
    plan = plan_task(user_request, model=model, verbose=False)
    planner = PlannerAgent(model=model)
    return planner.get_plan_summary(plan)






