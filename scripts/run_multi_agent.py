import argparse
import json

from src.core.multi_agent.agents.planner.agent import PlannerAgent
from src.core.multi_agent.agents.coder.agent import CoderAgent
from src.core.multi_agent.agents.critic.agent import CriticAgent
from src.utils.task_loader import load_tasks
from src.utils.config import config
from src.evaluation.quality_metrics import compute_quality_metrics
from src.utils.test_runner import run_tests_silent
from src.tools.executor import execute_code


def main():
    parser = argparse.ArgumentParser(description="Run Multi-Agent Coding Pipeline (Planner -> Coder -> Critic)")
    parser.add_argument("--task-file", default="data/test-tasks.json", help="Path to task file")
    parser.add_argument("--test-file", type=str, help="Path to external tests file")
    parser.add_argument("--model-planner", type=str, default=config.model_name, help="LLM model to use for Planner")
    parser.add_argument("--model-coder", type=str, default=config.model_name, help="LLM model to use for Coder")
    parser.add_argument("--model-critic", type=str, default=config.model_name, help="LLM model to use for Critic")
    parser.add_argument("--max-retries", type=int, default=3, help="Max iterations between Coder and Critic")
    parser.add_argument("--verbose", action="store_true", help="Show detailed agent output")
    
    args = parser.parse_args()

    # Initialize Agents
    planner = PlannerAgent(model=args.model_planner)
    coder = CoderAgent(model=args.model_coder)
    critic = CriticAgent(model=args.model_critic)

    # Load Tasks
    tasks = load_tasks(args.task_file)

    print(f"Starting Multi-Agent Pipeline for {len(tasks)} tasks...")

    for i, task in enumerate(tasks):
        task_id = task["id"]
        print(f"TASK {i+1}/{len(tasks)}: {task_id}")
        
        # 1. Planning
        print("\n[Planner] Creating implementation plan...")
        plan_result = planner.create_plan(
            task_id=task_id,
            user_request=task.get("docstring") or f"Implement {task.get('signature')}",
            verbose=args.verbose
        )
        
        if not plan_result:
            print("\n  Planning failed. Skipping task.")
            continue
        print("\n  Plan created.")

        # 2. Coder
        plan_str = json.dumps(plan_result, indent=2)
        
        current_code = None
        critic_feedback = None
        exec_summary = None
        
        for attempt in range(args.max_retries + 1):
            iter_msg = f"Initial Generation" if attempt == 0 else f"Refinement Iteration {attempt}/{args.max_retries}"
            print(f"\n[Coder] {iter_msg}...")
            
            # A. Generate Code
            coder_result = coder.generate_code(
                task_id=task_id,
                signature=task["signature"],
                plan=plan_str,
                critic_feedback=critic_feedback,
                exec_summary=exec_summary,
                verbose=args.verbose
            )
            
            if not coder_result["success"]:
                print("\n  Code generation failed.")
                break
            print("\n  Code generated.")
                
            current_code = coder_result["code"]
            
            # Execute code
            exec_summary = execute_code(current_code)
            # Compute Quality Metrics
            metrics = compute_quality_metrics(current_code)
            
            # B. Critique
            print("\n[Critic] Reviewing code...")
            
            critique = critic.critique(
                task_id=task_id,
                signature=task["signature"],
                docstring=task["docstring"],
                plan=plan_str,
                code=current_code,
                exec_summary=exec_summary,
                quality_metrics=metrics,
                verbose=args.verbose
            )
            
            critic_feedback = critique
            
            print("\n  Review completed.")

        # Final Test Execution
        print(f"\nTask {task_id} Completed")
        
        if args.test_file and current_code:
            print("\n[System] Running final verification tests...")
            passed, failed, error = run_tests_silent(task_id, current_code, args.test_file)
            if passed > 0 and failed == 0:
                print(f"    Tests PASSED ({passed} passed)")
            else:
                print(f"    Tests FAILED ({passed} passed, {failed} failed)")
                if error:
                    print(f"    Error: {error}")
        
        if current_code:
            print("\nFinal Code:")
            print("-" * 40)
            print(current_code)
            print("-" * 40)

if __name__ == "__main__":
    main()
