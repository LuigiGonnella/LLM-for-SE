import unittest
import importlib.util
import sys
from pathlib import Path
import tempfile


def run_task_tests(
    *,
    task_id: str,
    generated_code: str,
    test_file: Path,
) -> dict:
    """
    Runs ONLY the unittest.TestCase named test_<task_id>.
    """

    class_name = f"test_{task_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Write generated solution
        solution_path = tmpdir / "solution.py"
        solution_path.write_text(generated_code)

        # Copy test file
        test_path = tmpdir / "tests.py"
        test_path.write_text(test_file.read_text())

        sys.path.insert(0, str(tmpdir))

        try:
            spec = importlib.util.spec_from_file_location("tests", test_path)
            tests_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tests_module)

            if not hasattr(tests_module, class_name):
                raise AttributeError(
                    f"Test class '{class_name}' not found in {test_file}"
                )

            test_class = getattr(tests_module, class_name)

            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            result = unittest.TextTestRunner(
                stream=open("/dev/null", "w")
            ).run(suite)

            return {
                "passed": result.wasSuccessful(),
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
            }

        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
            }

        finally:
            sys.path.pop(0)
