import argparse
import os
import sys

# Ensure project root is on sys.path so `src` package is importable when
# running this script directly (e.g. `python scripts/run_single_agent.py`).
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.core.pipeline import build_single_agent_graph
from src.utils.task_loader import load_tasks
from src.utils.config import config
from src.evaluation.quality import format_metrics_report
from src.utils.test_runner import run_external_tests


def main():
    parser = argparse.ArgumentParser(
        description="Run single-agent code generation pipeline"
    )
    parser.add_argument(
        "--show-node-info",
        action="store_true",
        help="Show detailed node execution info",
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
        help="Path to the file containing external tests (e.g., data/strings/string_tests.py)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=config.model_name,
        help="LLM model to use (default: %(default)s)",
    )
    args = parser.parse_args()

    graph = build_single_agent_graph()
    tasks = load_tasks(args.task_file)

    if args.task_id:
        tasks = [t for t in tasks if str(t.get("id")) == args.task_id]
        if not tasks:
            print(f"No task found with ID: {args.task_id}")
            return

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

        state = {
            "task_id": task["id"],
            "signature": task["signature"],
            "docstring": task["docstring"],
            "examples": task.get("examples"),
            "difficulty": task.get("difficulty"),
            "model": args.model,
            "analysis": None,
            "plan": None,
            "code": None,
            "review": None,
            "exec_result": None,
            "quality_metrics": None,
            "refinement_count": 0,
            "show_node_info": args.show_node_info,
        }

        final_state = graph.invoke(state)

        print("\n=== RESULT ===")
        code_indented = final_state["code"].replace("\n", "\n  ")
        print(f"Final code:\n  {code_indented}")

        if final_state.get("quality_metrics"):
            print("\n" + format_metrics_report(final_state["quality_metrics"]) + "\n")

        if args.test_file and final_state.get("code"):
            run_external_tests(task["id"], final_state["code"], args.test_file)

        print("\n" + "-" * 100 + "\n")


if __name__ == "__main__":
    main()


# Usage examples:
# Usage default test tasks file (data/test-tasks.json)
# python -m scripts.run_single_agent

# Usage with specific task file
# python -m scripts.run_single_agent --task-file data/strings/strings-tasks.json

# Usage with specific task ID
# python -m scripts.run_single_agent --task-file data/strings/strings-tasks.json --task-id count_vowels

# Usage with output of node info
# python -m scripts.run_single_agent --task-file data/strings/strings-tasks.json --show-node-info

# Usage with external test file
# python -m scripts.run_single_agent --task-file data/strings/strings-tasks.json --task-id count_vowels --test-file data/strings/strings-tests.py

# Usage with different models
# python -m scripts.run_single_agent --model deepseek-coder-v2:16b --task-file data/strings/strings-tasks.json
# python -m scripts.run_single_agent --model codellama:7b-instruct --task-file data/strings/strings-tasks.json
