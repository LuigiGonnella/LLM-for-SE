"""
Critic agent.

Responsibility:
- Read the code + planner plan + execution feedback summary + quality metrics
- Produce actionable feedback for the coder (do not rewrite full code)

Prompts live in this file.
"""

from src.core.llm import call_llm

CRITIC_SYSTEM_PROMPT = """
You are a strict code critic for Python programming tasks.
You must diagnose issues and propose concrete fixes.
Do not write full code unless absolutely necessary.
Focus on correctness first, then code quality.
"""


def make_critic_prompt(
    signature: str,
    docstring: str,
    plan: str,
    code: str,
    exec_summary: str | None,
    quality_metrics: dict | None,
) -> str:
    exec_block = f"\nEXECUTION FEEDBACK (SUMMARY):\n{exec_summary}\n" if exec_summary else "\nEXECUTION FEEDBACK (SUMMARY):\nNone\n"
    qm_block = f"\nQUALITY METRICS:\n{quality_metrics}\n" if quality_metrics else "\nQUALITY METRICS:\nNone\n"

    return f"""
You are reviewing a generated solution.

TASK:
Signature:
{signature}

Spec:
{docstring}

PLANNER PLAN:
{plan}

CANDIDATE CODE:
{code}
{exec_block}{qm_block}
Provide feedback in the following format:

ISSUES (prioritized):
- [Correctness] ...
- [Correctness] ...
- [Quality] ...
- [Quality] ...

FIX INSTRUCTIONS:
1) ...
2) ...
3) ...

NOTES:
- Keep fixes minimal.
- If tests failed, focus on the likely cause based on the error summary.
- If tests passed but quality metrics are poor, suggest simplifications (remove unnecessary checks/imports, reduce complexity).
""".strip()


def critique(
    *,
    signature: str,
    docstring: str,
    plan: str,
    code: str,
    model: str,
    exec_summary: str | None = None,
    quality_metrics: dict | None = None,
) -> str:
    user_prompt = make_critic_prompt(signature, docstring, plan, code, exec_summary, quality_metrics)
    return call_llm(
        system_prompt=CRITIC_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=model,
    )
