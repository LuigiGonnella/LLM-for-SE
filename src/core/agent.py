"""
agent.py

Defines the single-agent cognitive steps.
Each function corresponds to ONE node in the LangGraph pipeline.
"""

from src.core.llm import call_llm


def analyze_task(*, signature: str, docstring: str, examples: str = None, model: str) -> str:
    prompt = (
        "Analyze the following programming task.\n\n"
        "- Extract required behavior\n"
        "- Identify constraints\n"
        "- Identify edge cases\n"
        "- Do NOT write code\n\n"
        f"Function signature:\n{signature}\n\n"
        f"Docstring:\n{docstring}"
    )
    if examples:
        prompt += f"\n\nExamples:\n{examples}"
    return call_llm(user_prompt=prompt, model=model)


def plan_solution(*, analysis: str, model: str) -> str:
    prompt = (
        "Based on the analysis below, produce a clear step-by-step plan "
        "to implement the function.\n\n"
        f"Analysis:\n{analysis}"
    )
    return call_llm(user_prompt=prompt, model=model)


def generate_code(*, signature: str, plan: str, model: str) -> str:
    prompt = (
        "Using the plan below, generate the Python function.\n\n"
        "Constraints:\n"
        "- Follow the function signature EXACTLY\n"
        "- Do not include explanations\n"
        "- Do not include markdown\n"
        "- Output ONLY valid Python code\n\n"
        f"Function signature:\n{signature}\n\n"
        f"Plan:\n{plan}"
    )
    return call_llm(user_prompt=prompt, model=model)


def review_code(*, code: str, model: str, exec_result: dict) -> str:
    prompt = (
        "Review the Python code below.\n\n"
        f"Code:\n{code}\n\n"
        f"Execution Results:\n"
        f"- Success: {exec_result['success']}\n"
        f"- Error: {exec_result['error'] or 'None'}\n"
        f"- Output: {exec_result['output'] or 'None'}\n\n"
        "Review checklist:\n"
        "- Identify logical errors\n"
        "- If code failed to execute, explain why\n"
        "- Identify violations of the function signature\n"
        "- If code appears correct, state that explicitly\n\n"
        "Provide a concise review that will guide refinement."
    )
    return call_llm(user_prompt=prompt, model=model)


def refine_code(*, code: str, review: str, model: str) -> str:
    prompt = (
        "You previously generated this code:\n\n"
        f"{code}\n\n"
        "You then produced this review:\n\n"
        f"{review}\n\n"
        "If issues were identified, fix the code.\n"
        "If no issues were found, return the code unchanged.\n\n"
        "Constraints:\n"
        "- Output ONLY the final Python code"
    )
    return call_llm(user_prompt=prompt, model=model)
