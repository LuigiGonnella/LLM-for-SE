from typing_extensions import TypedDict
from typing import Optional


class AgentState(TypedDict):
    task_id: str
    signature: str
    docstring: str
    examples: Optional[str]
    difficulty: Optional[str]
    model: str
    analysis: Optional[str]
    plan: Optional[str]
    code: Optional[str]
    review: Optional[str]
    exec_result: Optional[dict]
