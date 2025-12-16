def execute_code(code: str) -> dict:
    """
    Executes generated code in a controlled environment.
    Returns execution results and errors.
    """
    try:
        exec(code, {})
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}
