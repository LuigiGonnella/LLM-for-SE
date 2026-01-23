from typing_extensions import TypedDict
from typing import Optional, List


class CoderAgentState(TypedDict):
    """
    State for the coder agent.
    Tracks code generation workflow from input validation through optimization.

    Phases:
    1. INPUT VALIDATION: Verify inputs are well-formed
    2. EDGE CASE ANALYSIS: Identify boundary conditions
    3. COT GENERATION: Create structured reasoning
    4. CODE GENERATION: Generate initial code
    5. CODE VALIDATION: Check syntax and logic
    6. CODE OPTIMIZATION: Improve readability and performance
    7. CONSOLIDATION: Package final output
    """

    # ═══ INPUT ═══
    task_id: str
    signature: str
    plan: str
    model: str
    show_node_info: Optional[bool]

    # ═══ ITERATION FEEDBACK ═══
    critic_feedback: Optional[str]
    exec_summary: Optional[str]

    # ═══ PHASE 1: INPUT VALIDATION ═══
    input_validation_errors: Optional[List[str]]
    should_proceed: bool

    # ═══ PHASE 2: EDGE CASE ANALYSIS ═══
    edge_cases: Optional[List[str]]

    # ═══ PHASE 3: CHAIN-OF-THOUGHT ═══
    cot_reasoning: Optional[str]

    # ═══ PHASE 4: CODE GENERATION ═══
    raw_code: Optional[str]

    # ═══ PHASE 5: CODE VALIDATION ═══
    validated_code: Optional[str]
    validation_errors: Optional[List[str]]

    # ═══ PHASE 6: CODE OPTIMIZATION ═══
    optimized_code: Optional[str]
    optimization_suggestions: Optional[List[str]]

    # ═══ FINAL OUTPUT ═══
    code: Optional[str]

    # ═══ METADATA ═══
    errors: Optional[List[str]]
