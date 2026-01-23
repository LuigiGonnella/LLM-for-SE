"""
State definition for the multi-node planner agent.

This state tracks the complete planning workflow across all specialized nodes.
"""

from typing_extensions import TypedDict
from typing import Optional, Dict, List, Any


class AgentState(TypedDict):
    """
    Comprehensive state for multi-node planner agent.

    """

    # ═══ INPUT ═══
    task_id: str
    user_request: str
    model: str
    show_node_info: Optional[bool]

    # ═══ PHASE 1: INTENT ANALYSIS ═══
    intent_analysis: Optional[Dict[str, Any]]

    # ═══ PHASE 2: REQUIREMENTS ENGINEERING ═══
    requirements: Optional[Dict[str, Any]]

    # ═══ PHASE 3: ARCHITECTURE DESIGN ═══
    architecture: Optional[Dict[str, Any]]

    # ═══ PHASE 4: IMPLEMENTATION PLANNING ═══
    implementation_plan: Optional[Dict[str, Any]]

    # ═══ PHASE 5: QUALITY REVIEW ═══
    quality_review: Optional[Dict[str, Any]]

    # ═══ FINAL OUTPUT ═══
    final_plan: Optional[Dict[str, Any]]
    plan_approved: Optional[bool]

    # ═══ METADATA ═══
    iteration_count: Optional[int]
    errors: Optional[List[str]]
