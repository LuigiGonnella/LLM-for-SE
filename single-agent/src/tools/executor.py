import io
from contextlib import redirect_stdout, redirect_stderr


def execute_code(code: str) -> dict:
    """
    Executes generated code in a controlled environment.
    Returns execution results and errors.
    """

    result = {
        "success": False,
        "error": None,
        "output": None,
        "function_extracted": False,
        "function_names": [],
    }

    namespace = {}
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, namespace)
        result["success"] = True
        result["output"] = stdout_capture.getvalue()

        functions = [
            name
            for name, obj in namespace.items()
            if callable(obj) and not name.startswith("_")
        ]

        if functions:
            result["function_extracted"] = True
            result["function_names"] = functions
        else:
            result["function_extracted"] = False
            result["function_names"] = []
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"

    return result
