from src.core.pipeline import build_single_agent_graph
from src.utils.task_loader import load_tasks
from src.utils.config import Config


def main():
    graph = build_single_agent_graph()
    tasks = load_tasks("./data/test-tasks.json")

    for task in tasks:
        state = {
            "task_id": task["id"],
            "signature": task["signature"],
            "docstring": task["docstring"],
            "analysis": None,
            "plan": None,
            "code": None,
            "review": None,
            "exec_result": None,
            "model": Config.MODEL_NAME,
        }

        final_state = graph.invoke(state)

        print("\n=== FINAL OUTPUT ===")
        print(final_state["code"])


if __name__ == "__main__":
    main()

# python -m scripts.run_single_agent
