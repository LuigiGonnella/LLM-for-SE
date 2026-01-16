from pathlib import Path

from src.core.multi_agent.pipeline import build_multi_agent_graph
from src.utils.task_loader import load_tasks


def main():
    graph = build_multi_agent_graph()
    tasks = load_tasks("data/tasks.json")

    # Adjust this path convention to your repo
    tests_dir = Path("data/humaneval/tests")

    for task in tasks:
        task_id = task["id"]
        test_file = task.get("test_file") or (tests_dir / f"{task_id}.py")

        state = {
            "task_id": task_id,
            "signature": task["signature"],
            "docstring": task["docstring"],
            "plan": None,
            "code": None,
            "feedback": None,
            "exec_result": None,
            "quality_metrics": None,
            "iteration": 0,
            "max_iterations": 2,
            "model": "qwen2.5-coder:7b-instruct",
            "test_file": str(test_file),  # executor only; agents never see file contents
        }

        final_state = graph.invoke(state)

        print("\n==============================")
        print(f"TASK: {task_id}")
        print("PASSED:", (final_state.get("exec_result") or {}).get("passed"))
        print("QUALITY:", final_state.get("quality_metrics"))
        print("FINAL CODE:\n", final_state.get("code"))


if __name__ == "__main__":
    main()
