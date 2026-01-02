from typing_extensions import TypedDict
from typing import Optional


class AgentState(TypedDict):
    task_id: str
    signature: str
    docstring: str
    examples: Optional[str]
    model: str
    analysis: Optional[str]
    plan: Optional[str]
    code: Optional[str]
    review: Optional[str]
    exec_result: Optional[dict]
    quality_metrics: Optional[dict]
    refinement_count: Optional[int]
    show_node_info: Optional[bool]
