from src.core.multi_agent.agents.coder.pipeline import build_coder_graph
from src.core.multi_agent.agents.coder.state import CoderAgentState
from typing import Dict, Any, Optional
import json


class CoderAgent:
    def __init__(self, model: str = "deepseek"):
        """
        Initialize the coder agent.

        Args:
            model: Ollama model to use for code generation (default: deepseek)
        """
        self.model = model
        self.graph = build_coder_graph()

    def generate_code(
        self,
        task_id: str,
        signature: str,
        plan: str,
        critic_feedback: Optional[str] = None,
        exec_summary: Optional[str] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate code based on the implementation plan.

        Args:
            task_id: Unique identifier for this task
            signature: Function signature (e.g., "def solve(n: int) -> int:")
            plan: Implementation plan from planner agent
            critic_feedback: Optional feedback from critic agent (for iteration)
            exec_summary: Optional execution summary (for iteration)
            verbose: Whether to show detailed node outputs

        Returns:
            Dict containing:
                - success: Boolean indicating code generation success
                - code: Generated Python code
                - error: Error message if generation failed

        Raises:
            RuntimeError: If code generation fails critically
            ConnectionError: If cannot connect to Ollama
        """
        initial_state: CoderAgentState = {
            "task_id": task_id,
            "signature": signature,
            "plan": plan,
            "code": None,
            "model": self.model,
            "show_node_info": verbose,
            "critic_feedback": critic_feedback,
            "exec_summary": exec_summary,
            "errors": [],
            "input_validation_errors": [],
            "should_proceed": True,
            "edge_cases": [],
            "cot_reasoning": "",
            "raw_code": None,
            "validated_code": None,
            "validation_errors": [],
            "optimized_code": None,
            "optimization_suggestions": [],
        }

        try:
            result = self.graph.invoke(initial_state)

            return {
                "success": result.get("code") is not None,
                "code": result.get("code"),
                "error": result.get("errors")[0] if result.get("errors") else None,
            }

        except Exception as e:
            raise RuntimeError(f"Code generation failed: {str(e)}") from e

    def export_code_json(self, result: Dict[str, Any], filepath: str) -> None:
        """
        Export generated code to JSON file.

        Args:
            result: The result dict returned from generate_code()
            filepath: Path where to save the JSON file
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
