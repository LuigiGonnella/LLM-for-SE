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
    except SyntaxError:
        return False
    except Exception:
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


def extract_python_code(llm_output: str) -> Optional[str]:
    """
    Extract clean Python code from LLM output.

    Handles common patterns:
    - Code wrapped in ```python ... ``` blocks
    - Code wrapped in ``` ... ``` blocks
    - Raw code without markdown
    - Code with explanatory text before/after
    - Syntax validation

    Returns extracted code if valid, None otherwise.
    """
    if not llm_output:
        return None

    candidates = []

    # Pattern 1: ```python ... ```
    python_block = re.findall(r"```python\s*\n(.*?)```", llm_output, re.DOTALL)
    candidates.extend(python_block)

    # Pattern 2: ``` ... ``` (generic code block, newline required after ```)
    generic_block = re.findall(r"```\s*\n(.*?)```", llm_output, re.DOTALL)
    candidates.extend(generic_block)

    # Pattern 2b: ``` ... ``` (generic code block, no newline - code starts on same line)
    generic_block_inline = re.findall(r"```([^\n`].*?)```", llm_output, re.DOTALL)
    candidates.extend(generic_block_inline)
    
    # Pattern 3: Find code between "def" and end of response (greedy)
    # This handles cases where code is followed by explanations
    def_matches = re.findall(r"(def\s+\w+\s*\([^)]*\)[^:]*:.*?)(?=\n\n[A-Z]|\n\nNote:|\n\n#|\Z)", llm_output, re.DOTALL)
    candidates.extend(def_matches)

    # Pattern 4: No markdown, look for def/class as code start (allowing leading whitespace)
    # Find first function or class definition
    code_start = re.search(r"^\s*(def |class )", llm_output, re.MULTILINE)
    if code_start:
        # Extract until double newline or end of string
        remaining_text = llm_output[code_start.start():].strip()
        # Try to find natural ending (double newline before text that looks like prose)
        end_match = re.search(r"\n\n(?=[A-Z][a-z]+:|\*\*|Note|Explanation)", remaining_text)
        if end_match:
            candidates.append(remaining_text[:end_match.start()].strip())
        else:
            candidates.append(remaining_text)

    for candidate in candidates:
        cleaned = _clean_and_validate_code(candidate)
        if cleaned:
            return cleaned

    # Fallback: try validating raw output
    cleaned = _clean_and_validate_code(llm_output)
    if cleaned:
        return cleaned

    return None
