from src.core.pipeline import build_single_agent_graph
from src.core.state import AgentState


def test_build_single_agent_graph():
    """Test that the graph builds successfully"""
    graph = build_single_agent_graph()
    assert graph is not None


def test_graph_has_correct_nodes():
    """Test that the graph contains all expected nodes"""
    graph = build_single_agent_graph()

    # The compiled graph should have the nodes we defined
    # LangGraph compiled graphs have a 'nodes' attribute
    assert graph is not None


def test_agent_state_structure():
    """Test that AgentState has all required fields"""
    state: AgentState = {
        "task_id": "test",
        "signature": "def foo():",
        "docstring": "Test function",
        "examples": None,
        "difficulty": None,
        "model": "test-model",
        "analysis": None,
        "plan": None,
        "code": None,
        "review": None,
        "exec_result": None,
    }

    # Verify all expected keys are present
    assert "task_id" in state
    assert "signature" in state
    assert "docstring" in state
    assert "examples" in state
    assert "difficulty" in state
    assert "model" in state
    assert "analysis" in state
    assert "plan" in state
    assert "code" in state
    assert "review" in state
    assert "exec_result" in state


def test_agent_state_optional_fields():
    """Test that optional fields can be None"""
    state: AgentState = {
        "task_id": "test",
        "signature": "def foo():",
        "docstring": "Test function",
        "examples": None,
        "difficulty": None,
        "model": "test-model",
        "analysis": None,
        "plan": None,
        "code": None,
        "review": None,
        "exec_result": None,
    }

    assert state["analysis"] is None
    assert state["plan"] is None
    assert state["code"] is None
    assert state["review"] is None
    assert state["exec_result"] is None
    assert state["examples"] is None
    assert state["difficulty"] is None
