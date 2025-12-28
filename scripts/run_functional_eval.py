import argparse
import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.utils.task_loader import load_tasks
from src.evaluation.functional.runner import run_task_tests


def main():
    parser = argparse.ArgumentParser(
        description="Run functional evaluation on generated code (benchmark-centric)"
    )
    parser.add_argument(
        "task_file",
        help="Path to tasks.json (e.g. data/math/tasks.json)"
    )
    parser.add_argument(
        "--architecture",
        default="single_agent",
        choices=["single_agent", "multi_agent"],
    )
    parser.add_argument(
        "--run_id",
        default="run_001",
        help="Run identifier"
    )
    parser.add_argument(
        "--tests_file",
        default="data/math/tests.py",
        help="Path to tests.py"
    )
    args = parser.parse_args()

    tasks = load_tasks(args.task_file)

    generated_dir = Path("generated") / args.architecture / args.run_id
    tests_file = Path(args.tests_file)

    if not generated_dir.exists():
        raise FileNotFoundError(f"Generated directory not found: {generated_dir}")

    results = []

    for task in tasks:
        task_id = task["id"]
        code_path = generated_dir / f"{task_id}.py"

        if not code_path.exists():
            print(f"[WARN] Missing code for task {task_id}, skipping.")
            continue

        code = code_path.read_text(encoding="utf-8")

        functional = run_task_tests(
            task_id=task_id,
            generated_code=code,
            test_file=tests_file,
        )

        print(f"{task_id}: {functional}")

        results.append({
            "task_id": task_id,
            "functional": functional,
        })

    results_path = generated_dir / "functional_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved functional results to {results_path}")


if __name__ == "__main__":
    main()


#Usage
# python scripts/run_functional_eval.py \
#   data/math/tasks.json \
#   --tests_file data/math/tests.py \
#   --architecture single_agent \
#   --run_id run_001


#output structure
# generated/
# └── single_agent/
#     └── run_001/
#         ├── largest_prime_factor.py
#         ├── ...
#         └── functional_results.json