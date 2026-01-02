"""
task_loader.py

Utility for loading programming tasks from JSON files.
This abstracts away dataset format from the core pipeline.
"""

import json
from typing import List, Dict


def load_tasks(path: str) -> List[Dict]:
    """
    Load tasks from a JSON file.

    Expected format (per task):
    {
        "id": str,
        "signature": str,
        "docstring": str
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    if not isinstance(tasks, list):
        raise ValueError("Task file must contain a list of tasks")

    required_fields = {"id", "signature", "docstring"}
    optional_fields = {"examples", "difficulty"}

    for task in tasks:
        if not required_fields.issubset(task.keys()):
            raise ValueError(
                f"Task {task.get('id', '<unknown>')} is missing required fields. "
                f"Expected fields: {required_fields}"
            )

        for field in optional_fields:
            task.setdefault(field, None)

    return tasks
