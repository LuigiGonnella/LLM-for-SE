"""
agent.py

Defines the single-agent cognitive steps.
Each function corresponds to ONE node in the LangGraph pipeline.
"""

from single_agent.src.core.llm import call_llm
from single_agent.src.core.state import AgentState
import json
from single_agent.src.utils.config import config


def preprocessing_task(query: str, model: str) -> AgentState:
    state = AgentState()

    prompt = ("""
        You are an expert software engineer and task analyzer. Your job is to transform any programming task described by the user into a structured task format suitable for downstream processing. 

        Your output will populate the following AgentState fields:

        - task_id: a short, snake_case identifier for the task.
        - signature: a valid Python function signature with type hints.
        - docstring: a concise explanation of the function’s purpose and behavior.
        - examples: a JSON list of input/output pairs demonstrating expected behavior.
        - show_nodes_info: a boolean to keep as it is if already provided, to set at True if not provided.

        REQUIREMENTS:

        1. ALWAYS produce output in **strict JSON format** with the following structure:

        {
            "task_id": "**TASK_ID**",
            "signature": "**FUNCTION_SIGNATURE**",
            "docstring": "**FUNCTION_DESCRIPTION**",
            "examples": [
                {
                    "input": "**FIRST_INPUT**",
                    "output": "**FIRST_OUTPUT**"
                },
                {
                    "input": "**SECOND_INPUT**",
                    "output": "**SECOND_OUTPUT**"
                }
            ],
            "show_nodes_info": True
        }

        2. The task_id should be concise, descriptive, and snake_case.
        3. The signature must include Python type hints and be syntactically correct.
        4. Docstring should clearly describe the task, inputs, expected outputs, and any special rules.
        5. Include at least 2 examples. Inputs and outputs must be represented as JSON-serializable values (strings, numbers, lists, dicts, etc.).
        6. Difficulty, analysis, plan, code, review, exec_result, quality_metrics, refinement_count, and show_node_info **should not be included**—populate only the four fields above.
        7. Do NOT generate any explanation outside the JSON object.
        8. Handle edge cases if they can be inferred from the task description.

        EXAMPLE:

        User Query: "Write a function that counts the vowels in a string."

        Output:

        {
            "task_id": "count_vowels",
            "signature": "def count_vowels(s: str) -> int:",
            "docstring": "Count the number of vowels (a, e, i, o, u) in the input string, case-insensitive.",
            "examples": [
                {
                    "input": "'OpenAI ChatGPT'",
                    "output": "5"
                },
                {
                    "input": "'Hello World'",
                    "output": "3"
                }
            ],
            "show_nodes_info": True
        }

        INSTRUCTIONS:

        - Always return valid JSON.
        - Only fill the five fields: task_id, signature, docstring, examples, show_nodes_info.
        - Do not include additional commentary, formatting, or markdown.

    """)

    result = call_llm(user_prompt=prompt, model=model)
    task_dict = json.load(result)
    state["task_id"] = task_dict["task_id"]
    state["signature"] = task_dict["signature"]
    state["docstring"] = task_dict["docstring"]
    state["examples"] = task_dict["examples"]
    state['show_node_info'] = task_dict["show_node_info"]

    return state


def analyze_task(
    *, signature: str, docstring: str, examples: str = None, model: str
) -> str:
    prompt = (
        "You are an expert software engineer and task analyzer.\n"
        "Your job is to deeply analyze the programming task described below.\n\n"
        "IMPORTANT RULES:\n"
        "- Do NOT write any code\n"
        "- Do NOT suggest implementation details or algorithms\n"
        "- Do NOT restate the problem verbatim\n"
        "- Focus only on understanding, constraints, and correctness\n\n"
        "ANALYSIS OBJECTIVES:\n"
        "1. Clearly infer the required behavior of the function\n"
        "2. Identify all explicit and implicit constraints\n"
        "3. Enumerate edge cases and corner cases\n"
        "4. Identify ambiguous or underspecified aspects (if any)\n"
        "5. Infer input/output expectations and invariants\n"
        "6. Highlight common pitfalls or misunderstandings\n\n"
        "OUTPUT FORMAT (MANDATORY):\n"
        "Return your analysis using the following sections:\n\n"
        "### Required Behavior\n"
        "- Bullet list describing what the function must do\n\n"
        "### Inputs and Outputs\n"
        "- Describe expected input types, structure, and valid ranges\n"
        "- Provide the refactored input task in JSON format"
        "- Describe output type, format, and guarantees\n\n"
        "### Constraints\n"
        "- Bullet list of constraints (time, space, value ranges, rules)\n\n"
        "- Include implicit constraints derived from the problem type\n\n"
        "### Edge Cases\n"
        "- Bullet list of edge cases that must be handled correctly\n\n"
        "### Ambiguities / Assumptions\n"
        "- List any unclear aspects and reasonable assumptions\n\n"
        "### Common Pitfalls\n"
        "- Mistakes that an implementation might easily make\n\n"
        "TASK DESCRIPTION:\n\n"
        f"Function signature:\n{signature}\n\n"
        f"Docstring:\n{docstring}"
    )
    if examples:
        prompt += f"\n\nExamples:\n{examples}"

    prompt += (
        "\n\nREMEMBER:\n"
        "- Do NOT write code\n"
        "- Do NOT provide pseudocode\n"
        "- This is an analysis-only task\n"
    )

    return call_llm(user_prompt=prompt, model=model)


def plan_solution(*, analysis: str, model: str) -> str:
    prompt = (
        "You are an expert software engineer responsible for planning a correct and robust solution.\n"
        "You are given a completed task analysis.\n\n"
        "IMPORTANT RULES:\n"
        "- Do NOT write code\n"
        "- Do NOT include syntax, function definitions, or language-specific constructs\n"
        "- Focus on logical steps and design decisions only\n\n"
        "PLANNING OBJECTIVES:\n"
        "1. Translate the analysis into a clear implementation plan\n"
        "2. Define the high-level approach and strategy\n"
        "3. Identify sub-tasks and their responsibilities\n"
        "4. Specify how edge cases are handled\n"
        "5. Ensure all constraints are respected\n"
        "6. Avoid unnecessary complexity\n"
        "7. Resolve any ambiguities identified in the analysis\n\n"
        "OUTPUT FORMAT (MANDATORY):\n"
        "Return the plan using the following sections:\n\n"
        "### High-Level Approach\n"
        "- Brief description of the overall strategy\n\n"
        "### Step-by-Step Plan\n"
        "- Ordered list of logical steps required to implement the solution\n"
        "- Include specific checks for constraints and edge cases within the steps\n\n"
        "### Edge Case Handling\n"
        "- Explicitly state how each major edge case is addressed\n\n"
        "### Data Handling and State\n"
        "- Describe what data is tracked and how it evolves\n\n"
        "### Validation and Correctness Checks\n"
        "- Describe checks or conditions needed to ensure correctness\n\n"
        "### Complexity Considerations\n"
        "- Expected time and space complexity at a high level\n\n"
        "INPUT ANALYSIS:\n\n"
        f"{analysis}"
    )

    prompt += (
        "\n\nREMEMBER:\n"
        "- Do NOT write code or pseudocode\n"
        "- Do NOT include implementation syntax\n"
        "- This is a planning-only task\n"
    )

    return call_llm(user_prompt=prompt, model=model)


def generate_code(*, signature: str, plan: str, model: str) -> str:
    prompt = (
        "You are an expert Python engineer.\n"
        "Generate a complete and correct Python function strictly following the provided plan.\n\n"
        "ABSOLUTE RULES (NON-NEGOTIABLE):\n"
        "- Output ONLY valid Python code\n"
        "- Do NOT include explanations, comments, markdown, or extra text\n"
        "- Do NOT include imports unless strictly required by the plan\n"
        "- Do NOT change the function name, parameters, or order\n"
        "- Do NOT add helper functions unless explicitly implied by the plan\n"
        "- Do NOT print, log, or read input\n"
        "- The code must be directly executable\n\n"
        "CORRECTNESS REQUIREMENTS:\n"
        "- Handle all edge cases mentioned in the plan\n"
        "- Respect all constraints and assumptions\n"
        "- Prefer clarity and correctness over cleverness\n\n"
        "FUNCTION SIGNATURE (MUST MATCH EXACTLY):\n"
        f"{signature}\n\n"
        "IMPLEMENTATION PLAN:\n"
        f"{plan}\n\n"
        "FINAL CHECK BEFORE RESPONDING:\n"
        "- The output must start with 'def'\n"
        "- The output must contain exactly one function\n"
        "- No text before or after the code\n"
    )
    return call_llm(user_prompt=prompt, model=model)


def review_code(
    *, code: str, model: str, exec_result: dict, quality_metrics: dict = None
) -> str:
    prompt = (
        "You are a strict and detail-oriented code reviewer and judge.\n"
        "You must evaluate the given Python code using execution results and quality metrics.\n\n"
        "ABSOLUTE RULES:\n"
        "- Do NOT rewrite or fix the code\n"
        "- Do NOT suggest alternative implementations unless necessary to explain an issue\n"
        "- Base your review ONLY on the provided code, execution results, and quality metrics\n"
        "- Treat execution failures as definitive evidence of incorrectness\n\n"
        "EXECUTION RESULT SCHEMA (AUTHORITATIVE):\n"
        "- success: whether the code executed without raising exceptions\n"
        "- error: exception information if execution failed\n"
        "- output: captured stdout/stderr (must normally be empty)\n"
        "- function_extracted: whether at least one callable function was defined\n"
        "- function_names: list of extracted function names\n\n"
        "QUALITY METRICS SCHEMA:\n"
        "- maintainability_index: 0-100 scale (>=80 Excellent, >=60 Good, >=40 Moderate, <40 Poor)\n"
        "- cyclomatic_complexity: number of decision points (<=5 Simple, <=10 Moderate, >10 Complex)\n"
        "- lines_of_code: total lines\n"
        "- halstead_effort: cognitive effort required to understand the code\n\n"
        "EXECUTION INTERPRETATION RULES:\n"
        "- If success is False, the code HAS issues\n"
        "- If error is not None, the code HAS issues\n"
        "- If function_extracted is False, the code HAS issues\n"
        "- If more than one function is defined, the code HAS issues\n"
        "- If output is non-empty, treat it as a potential violation (unexpected I/O)\n\n"
        "QUALITY INTERPRETATION RULES:\n"
        "- If maintainability_index < 80, flag as needing improvement\n"
        "- If maintainability_index < 60, flag as poorly maintainable\n"
        "- If cyclomatic_complexity > 5, flag as could be simplified\n"
        "- If cyclomatic_complexity > 10, flag as overly complex\n"
        "- Quality issues alone do NOT make the verdict 'Code has issues'\n"
        "- Always suggest specific quality improvements in the Code Quality Assessment\n\n"
        "REVIEW OBJECTIVES:\n"
        "1. Verify execution success and function extraction\n"
        "2. Verify logical correctness via static inspection\n"
        "3. Identify missing or incorrect edge case handling\n"
        "4. Detect violations of the function contract or signature expectations\n"
        "5. Detect forbidden behavior (I/O, globals, side effects)\n"
        "6. Assess code quality and maintainability\n\n"
        "OUTPUT FORMAT (MANDATORY):\n"
        "Return your review using the following sections:\n\n"
        "### Execution Results Analysis\n"
        "- State whether execution succeeded\n"
        "- State whether exactly one function was extracted\n"
        "- Report any execution error or unexpected output\n\n"
        "### Signature and Contract Compliance\n"
        "- State whether the function definition appears valid and compliant\n"
        "- Identify any mismatch in name, parameters, or behavior\n\n"
        "### Logical Correctness\n"
        "- Describe any logical errors based on code inspection\n"
        '- If none are found, explicitly state: "No logical errors found"\n\n'
        "### Edge Case Coverage\n"
        "- Identify missing or incorrectly handled edge cases\n"
        '- If none are missing, explicitly state: "All relevant edge cases appear to be handled"\n\n'
        "### Code Quality Assessment\n"
        "- Comment on maintainability based on the metrics\n"
        "- Comment on complexity and readability\n"
        "- Suggest improvements if quality is poor (but do NOT rewrite code)\n\n"
        "### Constraint Violations\n"
        "- Identify violations such as unexpected I/O, multiple functions, globals, or side effects\n"
        '- If none are found, explicitly state: "No constraint violations detected"\n\n'
        "### Final Verdict\n"
        "- IMPORTANT: Base verdict ONLY on functional correctness, NOT on quality metrics\n"
        "- If code executes successfully and logic is correct, verdict MUST be 'Code is correct'\n"
        "- Quality issues should be noted above but do NOT affect the verdict\n"
        "- One of the following EXACT statements:\n"
        '  * "Code is correct" (functionally correct, even if quality could improve)\n'
        '  * "Code has issues" (has bugs, logic errors, or execution failures)\n\n'
        "CODE UNDER REVIEW:\n\n"
        f"{code}\n\n"
        "EXECUTION RESULTS:\n\n"
        f"{exec_result}\n\n"
    )

    if quality_metrics:
        prompt += f"QUALITY METRICS:\n\n{quality_metrics}\n\n"

    prompt += (
        "IMPORTANT:\n"
        '- If execution failed or function_extracted is False, verdict MUST be "Code has issues"\n'
        '- If more than one function name is present, verdict MUST be "Code has issues"\n'
        '- If execution succeeded AND logic is correct, verdict MUST be "Code is correct"\n'
        "- NEVER let quality metrics alone determine the verdict\n"
        "- Quality issues go in Code Quality Assessment section, not in verdict\n"
        "- Do NOT be vague or speculative\n"
        "- Do NOT include code blocks or markdown\n"
    )
    return call_llm(user_prompt=prompt, model=model)


def refine_code(*, code: str, review: str, model: str) -> str:
    prompt = (
        "You are an expert Python engineer tasked with refining existing code.\n"
        "You are given the original code and a formal review of that code.\n\n"
        "ABSOLUTE RULES:\n"
        "- Output ONLY valid Python code\n"
        "- Do NOT include explanations, comments, or markdown\n"
        "- Do NOT change the function signature\n"
        "- Do NOT add new functionality beyond what is required\n"
        "- Do NOT introduce new edge cases or assumptions\n"
        "- Preserve all correct behavior\n\n"
        "REFINEMENT OBJECTIVES (in priority order):\n"
        "1. Fix correctness issues identified in the review (highest priority)\n"
        "2. Ensure all edge cases are handled correctly\n"
        "3. Address quality issues flagged in the Code Quality Assessment:\n"
        "   - Reduce cyclomatic complexity if flagged as too high\n"
        "   - Improve maintainability if flagged as poor\n"
        "   - Simplify overly complex logic\n"
        "4. Improve readability without changing behavior\n\n"
        "QUALITY IMPROVEMENT GUIDELINES:\n"
        "- Reduce nesting depth where possible\n"
        "- Extract repeated logic patterns\n"
        "- Use early returns to reduce complexity\n"
        "- Prefer clear variable names\n"
        "- Keep changes minimal but meaningful\n\n"
        "ORIGINAL CODE:\n\n"
        f"{code}\n\n"
        "CODE REVIEW:\n\n"
        f"{review}\n\n"
        "FINAL CHECK BEFORE RESPONDING:\n"
        "- The output must start with 'def'\n"
        "- The output must contain exactly one function\n"
        "- No text before or after the code\n"
    )
    return call_llm(user_prompt=prompt, model=model)
