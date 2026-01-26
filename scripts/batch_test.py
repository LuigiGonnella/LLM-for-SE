#!/usr/bin/env python3
"""
Batch testing script for running single-agent or multi-agent pipeline across multiple models.

Usage:
    # Single-agent mode
    python -m scripts.batch_test --mode single --models codellama:7b-instruct
    
    # Multi-agent mode
    python -m scripts.batch_test --mode multi --models deepseek-coder-v2:16b
    
    # Test specific domains
    python -m scripts.batch_test --mode single --domains strings lists
    
    # Save results to CSV
    python -m scripts.batch_test --mode multi --output results.csv
"""

import argparse
import csv
import json
from datetime import datetime
import sys
from pathlib import Path
from tqdm import tqdm
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.single_agent.pipeline import build_single_agent_graph
from src.core.multi_agent.agents.planner.agent import PlannerAgent
from src.core.multi_agent.agents.coder.agent import CoderAgent
from src.core.multi_agent.agents.critic.agent import CriticAgent
from src.utils.task_loader import load_tasks
from src.utils.test_runner import run_tests_silent
from src.utils.config import config
from src.tools.executor import execute_code
from src.evaluation.quality_metrics import compute_quality_metrics

TASK_DOMAINS = {
    "strings": ("data/strings/strings-tasks.json", "data/strings/strings-tests.py"),
    "lists": ("data/lists/lists-tasks.json", "data/lists/lists-tests.py"),
    "logic": ("data/logic/logic-tasks.json", "data/logic/logic-tests.py"),
    "math": ("data/math/math-tasks.json", "data/math/math-tests.py"),
    "dsa": ("data/dsa/dsa-tasks.json", "data/dsa/dsa-tests.py"),
}


def run_task_single_agent(graph, model, task, test_path):
    """Run a single task using single-agent pipeline and return results dict."""
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


def run_task_multi_agent(agents, task, test_path, max_retries=2):
    """Run a single task using multi-agent pipeline and return results dict."""
    planner, coder, critic = agents
    task_id = task["id"]
    
    try:
        # 1. Planning Phase
        plan_result = planner.create_plan(
            task_id=task_id,
            user_request=task.get("docstring") or f"Implement {task.get('signature')}",
            verbose=False
        )
        
        if not plan_result:
            return {
                "task_id": task_id,
                "difficulty": task.get("difficulty", "N/A"),
                "passed": 0,
                "failed": 0,
                "error": "Planning failed",
            }
        
        plan_str = json.dumps(plan_result, indent=2)
        current_code = None
        critic_feedback = None
        exec_summary = None
        
        # 2. Coder-Critic Loop
        for attempt in range(max_retries + 1):
            # Generate Code
            coder_result = coder.generate_code(
                task_id=task_id,
                signature=task["signature"],
                plan=plan_str,
                critic_feedback=critic_feedback,
                exec_summary=exec_summary,
                verbose=False
            )
            
            if not coder_result["success"]:
                break
                
            current_code = coder_result["code"]
            
            # Execute and get metrics
            exec_summary = execute_code(current_code)
            metrics = compute_quality_metrics(current_code)
            
            # Critique
            critic_feedback = critic.critique(
                task_id=task_id,
                signature=task["signature"],
                docstring=task["docstring"],
                plan=plan_str,
                code=current_code,
                exec_summary=exec_summary,
                quality_metrics=metrics,
                verbose=False
            )
        
        # 3. Final Testing
        if current_code:
            passed, failed, error = run_tests_silent(task_id, current_code, test_path)
        else:
            passed, failed, error = 0, 0, "No code generated"
        
        return {
            "task_id": task_id,
            "difficulty": task.get("difficulty", "N/A"),
            "passed": passed,
            "failed": failed,
            "error": error,
        }
        
    except Exception as e:
        return {
            "task_id": task_id,
            "difficulty": task.get("difficulty", "N/A"),
            "passed": 0,
            "failed": 0,
            "error": str(e),
        }


def print_results_table(model, results):
    """Print results in a formatted table, grouped by domain."""
    print(f"\n{'='*80}")
    print(f"RESULTS: {model}")
    print(f"{'='*80}\n")

    # Group results by domain
    domains = {}
    for r in results:
        domain = r.get("domain", "unknown")
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(r)

    total_passed = total_failed = 0

    for domain, domain_results in domains.items():
        print(f"[{domain.upper()}]")
        print(f"{'Task ID':<45} {'Passed':>8} {'Failed':>8} {'Pass Rate':>10}")
        print("-" * 80)

        domain_passed = domain_failed = 0
        for r in domain_results:
            task_label = f"{r['task_id']} ({r['difficulty'].lower()})"
            task_total = r["passed"] + r["failed"]
            rate = (r["passed"] / task_total * 100) if task_total > 0 else 0
            domain_passed += r["passed"]
            domain_failed += r["failed"]
            print(f"{task_label:<45} {r['passed']:>8} {r['failed']:>8} {rate:>9.2f}%")

        domain_total = domain_passed + domain_failed
        domain_rate = (domain_passed / domain_total * 100) if domain_total > 0 else 0
        print("-" * 80)
        print(
            f"{'Subtotal':<45} {domain_passed:>8} {domain_failed:>8} {domain_rate:>9.2f}%"
        )
        print()

        total_passed += domain_passed
        total_failed += domain_failed

    print("=" * 80)
    total = total_passed + total_failed
    rate = (total_passed / total * 100) if total > 0 else 0
    print(f"{'TOTAL':<45} {total_passed:>8} {total_failed:>8} {rate:>9.2f}%\n")


def main():
    parser = argparse.ArgumentParser(description="Batch test single-agent or multi-agent pipeline")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["single", "multi"],
        default="single",
        help="Pipeline mode: single-agent or multi-agent"
    )
    parser.add_argument("--models", nargs="+", default=[config.base_model])
    parser.add_argument(
        "--domains",
        nargs="+",
        default=list(TASK_DOMAINS.keys()),
        choices=list(TASK_DOMAINS.keys()),
    )
    parser.add_argument("--output", type=str, help="Output CSV file")
    parser.add_argument("--task-id", type=str, help="Run only specific task")
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Max iterations between Coder and Critic (multi-agent only)"
    )
    args = parser.parse_args()

    # Initialize pipeline based on mode
    if args.mode == "single":
        graph = build_single_agent_graph()
        agents = None
    else:  # multi-agent
        graph = None
        # Initialize agents (all use the same model from --models)
        agents = None  # Will be created per model
    
    all_results = []

    print(f"Batch test started: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Mode: {args.mode.upper()}-AGENT")
    print(f"Models: {args.models}")
    print(f"Domains: {args.domains}")

    for model in args.models:
        model_results = []
        
        # Create agents for multi-agent mode
        if args.mode == "multi":
            agents = (
                PlannerAgent(model=model),
                CoderAgent(model=model),
                CriticAgent(model=model)
            )

        for domain in args.domains:
            tasks_file, tests_file = TASK_DOMAINS[domain]
            tasks = load_tasks(tasks_file)

            if args.task_id:
                tasks = [t for t in tasks if t["id"] == args.task_id]

            print(f"\n[{model}] {domain}: {len(tasks)} tasks")

            pbar = tqdm(tasks, desc="Tasks", unit="task", leave=True)
            for task in pbar:
                pbar.set_description(f"{task['id']}")
                
                # Run task based on mode
                if args.mode == "single":
                    result = run_task_single_agent(graph, model, task, tests_file)
                else:  # multi-agent
                    result = run_task_multi_agent(agents, task, tests_file, args.max_retries)
                
                result["model"] = model
                result["domain"] = domain
                model_results.append(result)
                all_results.append(result)

                status = (
                    "PASS" if result["failed"] == 0 and result["passed"] > 0 else "FAIL"
                )
                pbar.set_postfix_str(
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
