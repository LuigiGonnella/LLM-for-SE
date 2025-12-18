import argparse

from src.core.pipeline import build_single_agent_graph
from src.utils.task_loader import load_tasks
from src.utils.config import config


def main():
    parser = argparse.ArgumentParser(
        description="Run single-agent code generation pipeline"
    )
    parser.add_argument(
        "task_file",
        nargs="?",
        default="data/test-tasks.json",
        help="Path to task file (e.g., data/logic/logic-tasks.json)",
    )
    args = parser.parse_args()

    graph = build_single_agent_graph()
    tasks = load_tasks(args.task_file)

    for task in tasks:
        state = {
            "task_id": task["id"],
            "signature": task["signature"],
            "docstring": task["docstring"],
            "examples": task.get("examples"),
            "difficulty": task.get("difficulty"),
            "model": config.model_name,
            "analysis": None,
            "plan": None,
            "code": None,
            "review": None,
            "exec_result": None,
        }

        final_state = graph.invoke(state)

        print("\n=== FINAL OUTPUT ===")
        print(final_state["code"])


if __name__ == "__main__":
    main()


# Usage examples:
# python -m scripts.run_single_agent                              # uses default (data/test-tasks.json)
# python -m scripts.run_single_agent data/logic/logic-tasks.json  # run logic tasks
# python -m scripts.run_single_agent data/strings/strings-tasks.json
# python -m scripts.run_single_agent data/dsa/dsa-tasks.json
