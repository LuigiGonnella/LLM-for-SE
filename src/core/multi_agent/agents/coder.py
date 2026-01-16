"""
Coder agent.

Responsibility:
- Generate Python code from signature + planner plan
- Optionally incorporate critic feedback and execution feedback summaries

Prompts live in this file.
"""

from src.core.llm import call_llm
from src.utils.code_parser import extract_code

CODER_SYSTEM_PROMPT = """
You are a coding agent for Python programming tasks.
You must output ONLY valid Python code.
Follow the given plan and constraints exactly.
"""


def make_coder_prompt(signature: str, plan: str, feedback: str | None, exec_summary: str | None) -> str:
    feedback_block = f"\nCRITIC FEEDBACK:\n{feedback}\n" if feedback else ""
    exec_block = f"\nEXECUTION FEEDBACK (SUMMARY):\n{exec_summary}\n" if exec_summary else ""

    return f"""
You are an expert Python engineer.
Generate a complete and correct Python function strictly following the provided plan.

ABSOLUTE RULES (NON-NEGOTIABLE):
- Output ONLY valid Python code
- Do NOT include explanations, comments, markdown, or extra text
- Do NOT include docstrings
- Do NOT include imports unless strictly required by the plan
- Do NOT change the function name, parameters, or order
- Do NOT add helper functions unless strictly required by the plan
- Do NOT print, log, or read input
- The code must be directly executable

CORRECTNESS REQUIREMENTS:
- Handle all edge cases mentioned in the plan
- Respect all constraints and assumptions
- Prefer clarity and correctness over cleverness

FUNCTION SIGNATURE (MUST MATCH EXACTLY):
{signature}

IMPLEMENTATION PLAN:
{plan}
{feedback_block}{exec_block}
FINAL CHECK BEFORE RESPONDING:
- The output must start with 'def'
- The output must contain exactly one top-level function matching the signature
- No text before or after the code
""".strip()


def generate_code(
    *,
    signature: str,
    plan: str,
    model: str,
    critic_feedback: str | None = None,
    exec_summary: str | None = None,
) -> str:
    user_prompt = make_coder_prompt(signature, plan, critic_feedback, exec_summary)
    raw = call_llm(
        system_prompt=CODER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=model,
    )
    return extract_code(raw)
