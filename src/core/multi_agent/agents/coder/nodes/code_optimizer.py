"""
Code Optimizer Node - Optimizes code for readability and performance.
"""

from src.core.multi_agent.agents.coder.state import CoderAgentState
from src.core.multi_agent.agents.coder.llm import optimize_code


def code_optimizer_node(state: CoderAgentState) -> CoderAgentState:
    """
    Optimize generated code for readability and performance.
    
    PHASE 6: CODE OPTIMIZATION
    
    Improvements:
    - Variable naming clarity
    - Algorithm efficiency (when obvious improvements exist)
    - Code structure and readability
    - Comment quality if applicable
    - Follows Python best practices (PEP 8)
    
    Falls back to validated code if optimization fails.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with optimized code
    """

    # Skip if no validated code
    if not state.get("validated_code"):
        state["optimized_code"] = None
        return state
    
    print("\n  - PHASE 6: CODE OPTIMIZATION")
    
    try:
        # Use LLM to optimize code
        optimized_code = optimize_code(
            code=state["validated_code"],
            signature=state.get("signature"),
            plan=state.get("plan"),
            edge_cases=state.get("edge_cases", []),
            model=state.get("model"),
        )
        
        state["optimized_code"] = optimized_code
        
        if state.get("show_node_info"):
            lines_before = len(state["validated_code"].split("\n"))
            lines_after = len(optimized_code.split("\n"))
            
            print("    Code optimized:")
            print(f"      Lines: {lines_before} → {lines_after}")
            
            preview = "\n".join(optimized_code.split("\n")[:5])
            if len(optimized_code.split("\n")) > 5:
                preview += f"\n... ({len(optimized_code.split('\n'))} lines total)"
            print(f"\n{preview}\n")
    
    except Exception as e:
        error_msg = f"Optimization error: {str(e)}"
        state["errors"] = state.get("errors", []) + [error_msg]
        # Fallback to validated code without optimization
        state["optimized_code"] = state["validated_code"]
        if state.get("show_node_info"):
            print(f"    {error_msg} (using unoptimized code)\n")
    
    return state
