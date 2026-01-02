import re
from typing import Optional
import ast


def _is_valid_python(code: str) -> bool:
    """
    Check if code is syntactically valid Python.

    Returns True if valid, False otherwise.
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"SyntaxError during validation: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during validation: {e}")
        return False


def _clean_and_validate_code(code_snippet: str) -> Optional[str]:
    """
    Clean code and validate it's syntactically correct Python.

    Handles indentation normalization and validation.

    Returns cleaned code if valid, None otherwise.
    """

    if not code_snippet:
        return None

    lines = code_snippet.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    if not non_empty_lines:
        return None

    min_indent = min(
        (len(line) - len(line.lstrip()) for line in non_empty_lines if line.lstrip()),
        default=0,
    )

    dedented = "\n".join(line[min_indent:] for line in lines)

    cleaned = dedented.strip()

    if _is_valid_python(cleaned):
        return cleaned
    return None


def extract_python_code(llm_output: str) -> str:
    """
    Extract clean Python code from LLM output.

    Handles common patterns:
    - Code wrapped in ```python ... ``` blocks
    - Code wrapped in ``` ... ``` blocks
    - Raw code without markdown
    - Syntax validation
    """
    if not llm_output:
        return ""

    candidates = []

    # Pattern 1: ```python ... ```
    python_block = re.findall(r"```python\s*\n(.*?)```", llm_output, re.DOTALL)
    candidates.extend(python_block)

    # Pattern 2: ``` ... ``` (generic code block)
    generic_block = re.findall(r"```\s*\n(.*?)```", llm_output, re.DOTALL)
    candidates.extend(generic_block)

    # Pattern 3: No markdown, look for def/class as code start
    # Find first function or class definition
    code_start = re.search(r"^(def |class )", llm_output, re.MULTILINE)
    if code_start:
        candidates.append(llm_output[code_start.start() :].strip())
    # Fallback: return as-is (might already be clean code)

    for candidate in candidates:
        cleaned = _clean_and_validate_code(candidate)
        if cleaned:
            return cleaned

    print("Warning: No valid Python code found in LLM output.")
    cleaned = _clean_and_validate_code(llm_output)
    if cleaned:
        return cleaned

    print("Could not validate any extracted code.")
    return llm_output.strip()
