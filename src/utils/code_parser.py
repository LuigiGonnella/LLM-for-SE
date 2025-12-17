import re


def extract_python_code(llm_output: str) -> str:
    """
    Extract clean Python code from LLM output.

    Handles common patterns:
    - Code wrapped in ```python ... ``` blocks
    - Code wrapped in ``` ... ``` blocks
    - Raw code without markdown
    """
    if not llm_output:
        return ""

    # Pattern 1: ```python ... ```
    python_block = re.search(r"```python\s*\n(.*?)```", llm_output, re.DOTALL)
    if python_block:
        return python_block.group(1).strip()

    # Pattern 2: ``` ... ``` (generic code block)
    generic_block = re.search(r"```\s*\n(.*?)```", llm_output, re.DOTALL)
    if generic_block:
        return generic_block.group(1).strip()

    # Pattern 3: No markdown, look for def/class as code start
    # Find first function or class definition
    code_start = re.search(r"^(def |class )", llm_output, re.MULTILINE)
    if code_start:
        # Return everything from the first def/class onwards
        return llm_output[code_start.start():].strip()

    # Fallback: return as-is (might already be clean code)
    return llm_output.strip()
