"""
Planner agent.

Responsibility:
- Read task signature + docstring
- Produce a structured plan (requirements, edge cases, approach steps)

Prompts live in this file.
"""

from src.core.llm import call_llm

PLANNER_SYSTEM_PROMPT = """
You are a planning agent for Python programming tasks.
Your job is to produce a concise, structured plan that a coder can follow.
Do not write code.
"""


def make_planner_prompt(signature: str, docstring: str) -> str:
    # Keep this structured for easy downstream use.
    return f"""
You are given a Python function specification.

Return a plan with the following sections:
REQUIREMENTS:
- bullet list

EDGE_CASES:
- bullet list

PLAN:
1) step-by-step algorithmic plan

COMPLEXITY:
- time and space complexity (big-O), if relevant

FUNCTION SIGNATURE:
{signature}

DOCSTRING / SPEC:
{docstring}
""".strip()


def plan_task(*, signature: str, docstring: str, model: str) -> str:
    user_prompt = make_planner_prompt(signature, docstring)
    return call_llm(
        system_prompt=PLANNER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=model,
    )
