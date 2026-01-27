import os
import sys
import tempfile
import subprocess
import ast


def extract_imports(content):
    """Extracts all import statements from the python code."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return ""

    imports = []
    lines = content.splitlines(keepends=True)
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            start = node.lineno - 1
            end = node.end_lineno
            imports.append("".join(lines[start:end]))
    return "".join(imports)


def extract_test_class(file_path, class_name):
    """Extracts the source code of a specific class from a python file using AST."""
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    lines = content.splitlines(keepends=True)

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            start = node.lineno - 1
            end = node.end_lineno
            return "".join(lines[start:end])

    return None


def run_external_tests(task_id, generated_code, test_path):
    if not os.path.exists(test_path):
        print(f"  Test file not found: {test_path}")
        return

    # Convert task_id (e.g., "count_vowels") to CamelCase (e.g., "CountVowels")
    camel_case_name = "".join(word.capitalize() for word in task_id.split("_"))
    test_class_name = f"Test{camel_case_name}"

    print(f"Running external tests ({test_class_name}) from {test_path}...")

    # Estrai il codice della classe di test
    test_class_code = extract_test_class(test_path, test_class_name)
    if not test_class_code:
        print(f"  Can't extract class {test_class_name} from {test_path}")
        return 0, 0

    # Extract imports from the test file to ensure dependencies are met
    with open(test_path, "r") as f:
        test_file_content = f.read()
    extra_imports = extract_imports(test_file_content)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as temp_test_file:
        temp_file_name = temp_test_file.name

        # 1. Imports
        temp_test_file.write("import pytest\n")
        temp_test_file.write("import typing\n")
        temp_test_file.write("from typing import List, Dict, Set, Optional, Any\n")
        temp_test_file.write(extra_imports + "\n\n")

        # 2. Codice Generato
        temp_test_file.write("# --- GENERATED CODE ---\n")
        temp_test_file.write(generated_code + "\n\n")

        # 3. Classe di Test
        temp_test_file.write("# --- TEST CLASS ---\n")
        temp_test_file.write(test_class_code)

    # Esegui pytest
    cmd = [sys.executable, "-m", "pytest", temp_file_name, "-v"]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print("\nTest Results:")

    if result.returncode == 0:
        print("  All tests passed!")
    else:
        print("  Some tests failed.")

    # Filter output to show only the summary
    output_lines = result.stdout.splitlines()
    summary_start_index = -1
    for i, line in enumerate(output_lines):
        if "short test summary info" in line:
            summary_start_index = i
            break

    if summary_start_index != -1:
        print("\n".join(output_lines[summary_start_index:]))
    else:
        # If no short summary, look for the final status line (e.g. "=== 88 passed in 0.03s ===")
        summary_line = None
        for line in reversed(output_lines):
            if line.strip().startswith("=") and ("passed" in line or "failed" in line):
                summary_line = line
                break

        if summary_line:
            print(summary_line)
        elif result.returncode != 0:
            # Fallback if summary not found and tests failed
            print("\n".join(output_lines[-15:]))

    os.remove(temp_file_name)


def run_tests_silent(task_id, generated_code, test_path, debug=False):
    """
    Run tests silently and return (passed, failed, error_msg).
    Returns (0, 0, error_msg) if tests cannot be run.

    Args:
        task_id: Task identifier
        generated_code: The code to test
        test_path: Path to the test file
        debug: If True, saves temp test file and prints full output on failure
    """
    import re

    if not os.path.exists(test_path):
        return 0, 0, "Test file not found"

    camel_case_name = "".join(word.capitalize() for word in task_id.split("_"))
    test_class_name = f"Test{camel_case_name}"

    test_class_code = extract_test_class(test_path, test_class_name)
    if not test_class_code:
        return 0, 0, f"Test class {test_class_name} not found"

    with open(test_path, "r") as f:
        test_file_content = f.read()
    extra_imports = extract_imports(test_file_content)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as temp_test_file:
        temp_file_name = temp_test_file.name
        temp_test_file.write("import pytest\n")
        temp_test_file.write("import typing\n")
        temp_test_file.write("from typing import List, Dict, Set, Optional, Any\n")
        temp_test_file.write(extra_imports + "\n\n")
        temp_test_file.write(generated_code + "\n\n")
        temp_test_file.write(test_class_code)

    try:
        cmd = [sys.executable, "-m", "pytest", temp_file_name, "-v", "--tb=short"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr

        passed = 0
        failed = 0
        error_msg = ""

        # Try multiple regex patterns for different pytest output formats
        if match := re.search(r"(\d+) passed", output):
            passed = int(match.group(1))
        if match := re.search(r"(\d+) failed", output):
            failed = int(match.group(1))

        # If no tests were collected/run
        if "no tests ran" in output.lower() or "collected 0 items" in output.lower():
            error_msg = "No tests collected"
        # Check for pytest module import error
        elif "No module named" in output and "pytest" in output:
            error_msg = "pytest not installed"
        # Check for syntax errors in generated code
        elif "SyntaxError" in output:
            error_msg = "Syntax error in generated code"
        # Check for import errors
        elif "ImportError" in output or "ModuleNotFoundError" in output:
            # Extract specific import error
            if match := re.search(r"(ImportError|ModuleNotFoundError): (.+)", output):
                error_msg = match.group(0)
            else:
                error_msg = "Import error in test execution"
        # Generic failure message
        elif result.returncode != 0 and passed == 0 and failed == 0:
            # Extract first error line if available
            error_lines = [
                line
                for line in output.split("\n")
                if "ERROR" in line or "FAILED" in line
            ]
            error_msg = error_lines[0] if error_lines else "Tests failed to run"
        elif failed > 0:
            error_msg = f"{failed} test(s) failed"

        # Debug mode: save temp file and print output
        if debug and (passed == 0 or failed > 0):
            debug_file = f"debug_test_{task_id}.py"
            import shutil

            shutil.copy(temp_file_name, debug_file)
            print(f"\n[DEBUG] Test file saved to: {debug_file}")
            print(f"[DEBUG] Full pytest output:\n{output}\n")

        return passed, failed, error_msg

    except subprocess.TimeoutExpired:
        return 0, 0, "Test timeout (>60s)"
    except Exception as e:
        return 0, 0, f"Exception: {str(e)}"
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
