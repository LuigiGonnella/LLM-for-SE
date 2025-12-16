import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.core.pipeline import build_single_agent_graph
from src.utils.task_loader import load_tasks
from src.utils.config import Config

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

    # print("Task:", task["id"])
    # print("Generated code:", final_state["code"])
