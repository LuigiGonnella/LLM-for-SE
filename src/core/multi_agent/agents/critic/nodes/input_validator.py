from src.core.multi_agent.agents.critic.state import CriticAgentState

def input_validator_node(state: CriticAgentState) -> CriticAgentState:
    """
    Validate input state before processing.
    
    Checks:
    - Code presence
    - Plan presence
    - Signature presence
    """
    print("\n  - PHASE 1: INPUT VALIDATION")
    validation_errors = []

    if not state.get("code"):
        validation_errors.append("Code is required for critique")
    
    if not state.get("plan"):
        validation_errors.append("Plan is required for critique")
        
    if not state.get("signature"):
        validation_errors.append("Signature is required for critique")

    state["input_validation_errors"] = validation_errors
    state["should_proceed"] = len(validation_errors) == 0

    if state.get("show_node_info"):
        if state["should_proceed"]:
            print("    Input validation passed")
        else:
            print("    Input validation failed:")
            for error in validation_errors:
                print(f"      - {error}")
            print()

    return state
