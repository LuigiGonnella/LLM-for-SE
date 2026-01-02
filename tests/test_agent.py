import pytest
from unittest.mock import patch

from single_agent.src.core.agent import (
    analyze_task,
    plan_solution,
    generate_code,
    review_code,
    refine_code,
)


@pytest.fixture
def mock_llm():
    """Fixture to mock the call_llm function"""
    with patch("single_agent.src.core.agent.call_llm") as mock:
        yield mock


def test_analyze_task(mock_llm):
    """Test analyze_task calls LLM with correct prompt structure"""
    mock_llm.return_value = "Analysis result"

    result = analyze_task(
        signature="def foo(x: int) -> int:",
        docstring="Return x + 1",
        model="test-model",
    )

    assert result == "Analysis result"
    mock_llm.assert_called_once()

    # Check that the prompt contains key elements
    call_args = mock_llm.call_args
    prompt = call_args.kwargs["user_prompt"]
    assert "deeply analyze the programming task" in prompt
    assert "def foo(x: int) -> int:" in prompt
    assert "Return x + 1" in prompt
    assert call_args.kwargs["model"] == "test-model"


def test_plan_solution(mock_llm):
    """Test plan_solution calls LLM with correct prompt structure"""
    mock_llm.return_value = "Step 1: ...\nStep 2: ..."

    result = plan_solution(analysis="Task requires incrementing x", model="test-model")

    assert result == "Step 1: ...\nStep 2: ..."
    mock_llm.assert_called_once()

    call_args = mock_llm.call_args
    prompt = call_args.kwargs["user_prompt"]
    assert "Step-by-Step Plan" in prompt
    assert "Task requires incrementing x" in prompt


def test_generate_code(mock_llm):
    """Test generate_code calls LLM with correct prompt structure"""
    mock_llm.return_value = "def foo(x: int) -> int:\n    return x + 1"

    result = generate_code(
        signature="def foo(x: int) -> int:", plan="1. Return x + 1", model="test-model"
    )

    assert "def foo(x: int) -> int:" in result
    mock_llm.assert_called_once()

    call_args = mock_llm.call_args
    prompt = call_args.kwargs["user_prompt"]
    assert "Generate a complete and correct Python function" in prompt
    assert "def foo(x: int) -> int:" in prompt
    assert "1. Return x + 1" in prompt


def test_review_code(mock_llm):
    """Test review_code calls LLM with correct prompt structure"""
    mock_llm.return_value = "The code looks correct"

    code = "def foo(x: int) -> int:\n    return x + 1"
    exec_result = {
        "success": True,
        "error": None,
        "output": "",
        "function_extracted": True,
        "function_names": ["foo"],
    }
    result = review_code(code=code, model="test-model", exec_result=exec_result)

    assert result == "The code looks correct"
    mock_llm.assert_called_once()

    call_args = mock_llm.call_args
    prompt = call_args.kwargs["user_prompt"]
    assert "evaluate the given Python code" in prompt
    assert code in prompt


def test_refine_code(mock_llm):
    """Test refine_code calls LLM with correct prompt structure"""
    mock_llm.return_value = "def foo(x: int) -> int:\n    return x + 1"

    original_code = "def foo(x):\n    return x + 1"
    review = "Missing type hint on return"

    result = refine_code(code=original_code, review=review, model="test-model")

    assert "def foo(x: int) -> int:" in result
    mock_llm.assert_called_once()

    call_args = mock_llm.call_args
    prompt = call_args.kwargs["user_prompt"]
    assert original_code in prompt
    assert review in prompt
    assert "Fix correctness issues" in prompt


def test_all_functions_use_keyword_only_args():
    """Test that all agent functions require keyword arguments"""
    # These should raise TypeError if called with positional args
    with pytest.raises(TypeError):
        analyze_task("sig", "doc", "model")

    with pytest.raises(TypeError):
        plan_solution("analysis", "model")

    with pytest.raises(TypeError):
        generate_code("sig", "plan", "model")

    with pytest.raises(TypeError):
        review_code("code", "model", {})

    with pytest.raises(TypeError):
        refine_code("code", "review", "model")
