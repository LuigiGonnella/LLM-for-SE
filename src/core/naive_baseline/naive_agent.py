"""
Naive Single-Agent Baseline

A simple one-shot code generation approach where the LLM receives the task
and generates code in a single call without multi-stage reasoning.

This serves as a true minimal baseline for comparison with:
1. Sophisticated single-agent (multi-stage reasoning)
2. Multi-agent system (distinct roles)
"""

from src.core.llm import call_llm
from src.tools.executor import execute_code
from src.utils.code_parser import extract_python_code
from src.evaluation.quality_metrics import compute_quality_metrics

NAIVE_SYSTEM_PROMPT = """
You are a Python code generation assistant.

Your task is to generate correct, executable Python code based on the given specification.

Rules:
- Output ONLY valid Python code
- Do NOT include explanations, comments, or markdown
- Match the function signature exactly
- Handle edge cases appropriately
- The code must be directly executable
"""


def generate_code_naive(
    *, signature: str, docstring: str, examples: str = None, model: str
) -> str:
    """
    Naive one-shot code generation.

    Makes a single LLM call with the task specification and returns generated code.
    No analysis, planning, or review stages.

    Args:
        signature: Function signature (e.g., "def count_vowels(s: str) -> int:")
        docstring: Function specification
        examples: Optional input/output examples
        model: LLM model to use

    Returns:
        Generated Python code as string
    """

    prompt = (
        "Generate a Python function that solves the following task.\n\n"
        f"Function signature:\n{signature}\n\n"
        f"Specification:\n{docstring}\n"
    )

    if examples:
        prompt += f"\nExamples:\n{examples}\n"

    prompt += (
        "\nGenerate the complete function implementation.\n"
        "Output ONLY the Python code, with no explanations or markdown.\n"
    )

    raw_code = call_llm(
        system_prompt=NAIVE_SYSTEM_PROMPT,
        user_prompt=prompt,
        model=model,
    )

    # Extract clean Python code
    extracted = extract_python_code(raw_code)

    if extracted is None:
        # Fallback to raw output if extraction fails
        return raw_code

    return extracted


def run_naive_baseline(
    *, signature: str, docstring: str, examples: str = None, model: str
) -> dict:
    """
    Run the naive baseline end-to-end.

    Returns:
        Dictionary with:
        - code: Generated code
        - exec_result: Execution results
        - quality_metrics: Code quality metrics
    """

    # Generate code (single LLM call)
    code = generate_code_naive(
        signature=signature,
        docstring=docstring,
        examples=examples,
        model=model,
    )

    # Execute the code
    exec_result = execute_code(code)

    # Compute quality metrics
    quality_metrics = compute_quality_metrics(code)

    return {
        "code": code,
        "exec_result": exec_result,
        "quality_metrics": quality_metrics,
    }
