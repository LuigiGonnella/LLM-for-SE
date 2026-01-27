from src.core.multi_agent.agents.critic.pipeline import build_critic_graph
from src.core.multi_agent.agents.critic.state import CriticAgentState
from typing import Dict, Any, Optional


class CriticAgent:
    def __init__(self, model: str = "deepseek"):
        """
        Initialize the critic agent.

        Args:
            model: Ollama model to use for critique
        """
        self.model = model
        self.graph = build_critic_graph()

    def critique(
        self,
        task_id: str,
        signature: str,
        docstring: str,
        plan: str,
        code: str,
        exec_summary: Optional[str] = None,
        quality_metrics: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
    ) -> str:
        """
        Generate critique for the provided code.

        Args:
            task_id: Unique identifier
            signature: Function signature
            docstring: Function docstring
            plan: Implementation plan
            code: Generated code
            exec_summary: Execution feedback
            quality_metrics: Computed quality metrics
            verbose: Show node info

        Returns:
            The critique string (markdown)
        """
        initial_state: CriticAgentState = {
            "task_id": task_id,
            "signature": signature,
            "docstring": docstring,
            "plan": plan,
            "code": code,
            "model": self.model,
            "exec_summary": exec_summary,
            "quality_metrics": quality_metrics,
            "show_node_info": verbose,
            "input_validation_errors": [],
            "should_proceed": True,
            "correctness_analysis": None,
            "quality_analysis": None,
            "feedback": None,
        }

        try:
            result = self.graph.invoke(initial_state)
            return result.get("feedback") or "Analysis failed."

        except Exception as e:
            raise RuntimeError(f"Critique generation failed: {str(e)}") from e
