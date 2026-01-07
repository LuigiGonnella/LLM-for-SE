#!/usr/bin/env python3
"""
Batch testing script for running the single-agent pipeline across multiple models.

Usage:
    python -m scripts.batch_test --models codellama:7b-instruct deepseek-coder-v2:16b
    python -m scripts.batch_test --domains strings lists
    python -m scripts.batch_test --output results.csv
"""

import argparse
import csv
from datetime import datetime

from src.core.pipeline import build_single_agent_graph
from src.utils.task_loader import load_tasks
from src.utils.test_runner import run_tests_silent
from src.utils.config import config

TASK_DOMAINS = {
    "strings": ("data/strings/strings-tasks.json", "data/strings/strings-tests.py"),
    "lists": ("data/lists/lists-tasks.json", "data/lists/lists-tests.py"),
    "logic": ("data/logic/logic-tasks.json", "data/logic/logic-tests.py"),
    "math": ("data/math/math-tasks.json", "data/math/math-tests.py"),
    "dsa": ("data/dsa/dsa-tasks.json", "data/dsa/dsa-tests.py"),
}


def run_task(graph, model, task, test_path):
    """Run a single task and return results dict."""
    state = {
        "task_id": task["id"],
        "signature": task["signature"],
        "docstring": task["docstring"],
        "examples": task.get("examples"),
        "difficulty": task.get("difficulty"),
        "model": model,
        "analysis": None,
        "plan": None,
        "code": None,
        "review": None,
        "exec_result": None,
        "quality_metrics": None,
        "refinement_count": 0,
        "show_node_info": False,
    }

    try:
        final_state = graph.invoke(state)
        code = final_state.get("code", "")
        passed, failed, error = run_tests_silent(task["id"], code, test_path)

        return {
            "task_id": task["id"],
            "difficulty": task.get("difficulty", "N/A"),
            "passed": passed,
            "failed": failed,
            "error": error,
        }
    except Exception as e:
        return {
            "task_id": task["id"],
            "difficulty": task.get("difficulty", "N/A"),
            "passed": 0,
            "failed": 0,
            "error": str(e),
        }


def print_results_table(model, results):
    """Print results in a formatted table."""
    print(f"\n{'='*80}")
    print(f"RESULTS: {model}")
    print(f"{'='*80}\n")
    print(f"{'Task ID':<45} {'Passed':>8} {'Failed':>8} {'Pass Rate':>10}")
    print("-" * 80)

    total_passed = total_failed = 0
    for r in results:
        task_label = f"{r['task_id']} ({r['difficulty'].lower()})"
        total = r["passed"] + r["failed"]
        rate = (r["passed"] / total * 100) if total > 0 else 0
        total_passed += r["passed"]
        total_failed += r["failed"]
        print(f"{task_label:<45} {r['passed']:>8} {r['failed']:>8} {rate:>9.2f}%")

    print("-" * 80)
    total = total_passed + total_failed
    rate = (total_passed / total * 100) if total > 0 else 0
    print(f"{'TOTAL':<45} {total_passed:>8} {total_failed:>8} {rate:>9.2f}%\n")


def main():
    parser = argparse.ArgumentParser(description="Batch test single-agent pipeline")
    parser.add_argument("--models", nargs="+", default=[config.model_name])
    parser.add_argument(
        "--domains",
        nargs="+",
        default=list(TASK_DOMAINS.keys()),
        choices=list(TASK_DOMAINS.keys()),
    )
    parser.add_argument("--output", type=str, help="Output CSV file")
    parser.add_argument("--task-id", type=str, help="Run only specific task")
    args = parser.parse_args()

    graph = build_single_agent_graph()
    all_results = []

    print(f"Batch test started: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Models: {args.models}")
    print(f"Domains: {args.domains}")

    for model in args.models:
        model_results = []

        for domain in args.domains:
            tasks_file, tests_file = TASK_DOMAINS[domain]
            tasks = load_tasks(tasks_file)

            if args.task_id:
                tasks = [t for t in tasks if t["id"] == args.task_id]

            print(f"\n[{model}] {domain}: {len(tasks)} tasks")

            for task in tasks:
                print(f"  Running {task['id']}...", end=" ", flush=True)
                result = run_task(graph, model, task, tests_file)
                result["model"] = model
                result["domain"] = domain
                model_results.append(result)
                all_results.append(result)

                status = (
                    "PASS" if result["failed"] == 0 and result["passed"] > 0 else "FAIL"
                )
                print(
                    f"{status} ({result['passed']}/{result['passed']+result['failed']})"
                )

        print_results_table(model, model_results)

    if args.output:
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "model",
                    "domain",
                    "task_id",
                    "difficulty",
                    "passed",
                    "failed",
                    "error",
                ],
            )
            writer.writeheader()
            writer.writerows(all_results)
        print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
