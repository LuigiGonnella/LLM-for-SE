"""
Naive Baseline Runner

Runs only the naive baseline (single LLM call) pipeline.

Usage:
    python -m scripts.run_naive_agent --task-file data/strings/strings-tasks.json --task-id count_vowels
    python -m scripts.run_naive_agent --test-file data/strings/strings-tests.py --task-id count_vowels
"""

import argparse

from src.core.naive_baseline.naive_agent import generate_code_naive
from src.utils.task_loader import load_tasks
from src.utils.config import config
from src.tools.executor import execute_code
from src.evaluation.quality_metrics import (
    compute_quality_metrics,
    format_metrics_report,
)
from src.utils.test_runner import run_external_tests


def run_naive_mode(task: dict, model: str) -> dict:
    """Run naive baseline mode and return results."""
    code = generate_code_naive(
        signature=task["signature"],
        docstring=task["docstring"],
        examples=task.get("examples"),
        model=model,
    )

    exec_result = execute_code(code)
    quality_metrics = compute_quality_metrics(code)

    return {
        "code": code,
        "exec_result": exec_result,
        "quality_metrics": quality_metrics,
        "llm_calls": 1,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run naive baseline code generation pipeline"
    )

    parser.add_argument(
        "--task-file",
        default="data/test-tasks.json",
        help="Path to task file (e.g., data/logic/logic-tasks.json)",
    )
    parser.add_argument(
        "--task-id",
        type=str,
        help="ID of the specific task to execute",
    )
    parser.add_argument(
        "--test-file",
        type=str,
        help="Path to external test file (e.g., data/strings/strings-tests.py)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=config.base_model,
        help="LLM model to use (default: %(default)s)",
    )

    args = parser.parse_args()

    tasks = load_tasks(args.task_file)

    if args.task_id:
        tasks = [t for t in tasks if str(t.get("id")) == args.task_id]
        if not tasks:
            print(f"❌ No task found with ID: {args.task_id}")
            return

    print("\n" + "=" * 100)
    print("MODE: NAIVE BASELINE (One-Shot Generation)")
    print("=" * 100)
    print("Architecture: Single LLM call, no multi-stage reasoning")
    print("LLM Calls: 1 (fixed)")
    print("=" * 100 + "\n")

    for task in tasks:
        print("QUERY:")
        print(f"  ID        : {task.get('id')}")
        print(f"  Signature : {task.get('signature')}")
        print(f"  Docstring : {task.get('docstring')}")
        if task.get("examples"):
            print("  Examples  :")
            for ex in task["examples"]:
                print(f"    - Input : {ex.get('input')}")
                print(f"      Output: {ex.get('output')}")
        if task.get("difficulty"):
            print(f"  Difficulty: {task.get('difficulty')}\n")

        print("🤖 Generating code with naive baseline...\n")
        try:
            result = run_naive_mode(task, args.model)
        except Exception as e:
            print(f"\n❌ Pipeline failed with error: {e}")
            import traceback

            traceback.print_exc()
            continue

        print("\n=== RESULT ===")
        if result.get("code"):
            code_indented = result["code"].replace("\n", "\n  ")
            print(f"Final code:\n  {code_indented}")
        else:
            print("Final code:\n  [none]")

        if result.get("exec_result"):
            exec_result = result["exec_result"]
            print("\nExecution Summary:")
            print(f"  Success           : {exec_result.get('success')}")
            print(f"  Function Extracted: {exec_result.get('function_extracted')}")
            print(f"  Function Names    : {exec_result.get('function_names')}")
            if exec_result.get("error"):
                print(f"  Error             : {exec_result.get('error')}")
            if exec_result.get("output"):
                print(f"  Output            : {repr(exec_result.get('output'))}")

        if result.get("quality_metrics"):
            print("\n" + format_metrics_report(result["quality_metrics"]) + "\n")

        if args.test_file and result.get("code"):
            run_external_tests(task["id"], result["code"], args.test_file)

        print("\n" + "-" * 100 + "\n")


if __name__ == "__main__":
    main()
