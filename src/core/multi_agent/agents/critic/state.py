from typing_extensions import TypedDict
from typing import Optional, Dict, List, Any


class CriticAgentState(TypedDict):
    """
    State for the critic agent.
    Tracks the critique workflow from input validation through feedback generation.
    """

    # ═══ INPUT ═══
    task_id: str
    signature: str
    docstring: str
    plan: str
    code: str
    model: str
    exec_summary: Optional[str]
    quality_metrics: Optional[Dict[str, Any]]
    show_node_info: Optional[bool]

    # ═══ INTERNAL STATE ═══
    input_validation_errors: Optional[List[str]]
    should_proceed: bool

    # Analysis results
    correctness_analysis: Optional[str]  # Findings on bugs/logic
    quality_analysis: Optional[str]  # Findings on style/complexity

    # ═══ FINAL OUTPUT ═══
    feedback: Optional[str]  # The final critique string
