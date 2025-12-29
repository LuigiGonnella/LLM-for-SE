## MULTI-AGENT ARCHITECTURE
### OPTION 1
5 Agents with distinct roles:
- Analyzer: understanding tasks
- Planner: creates detailed step-by-step solutions
- Coder: generates code
- Tester: reviews code and identifies issues
- Refiner: fixes code based on test feedback

```python
class MultiAgentState(TypedDict):
    task_id: str
    signature: str
    docstring: str
    examples: Optional[str]
    
    # Agent outputs
    analysis: Optional[str]
    plan: Optional[str]
    code: Optional[str]
    review: Optional[str]
    exec_result: Optional[dict]
    refinement_count: int
    
    # New: Agent metadata
    current_agent: str
    agent_history: list[str]  # Track which agents processed this
    feedback_loop: list[dict]  # Store agent->agent feedback
```

```python
class Agent:
    def __init__(self, name: str, model: str, role: str):
        self.name = name
        self.model = model
        self.role = role
    
    async def execute(self, state: MultiAgentState) -> MultiAgentState:
        # Agent-specific logic
        pass
```

Possible workflow:
- OPTION 1
```
Analyzer → Planner → Coder ↔ Tester (feedback loop)
                         ↓
                       Refiner
```
An example:

```
1. Analyzer analyzes task
2. Planner plans solution
3. Coder generates code
4. Tester reviews code
   ├─ If issues found → feedback to Coder
   ├─ Coder refines
   └─ Loop back to step 4 (until passing or max iterations)
5. Refiner applies final optimizations
```
- OPTION 2
```
Master Agent (decides which specialists to call)
    ├─ Analyzer (when understanding needed)
    ├─ Planner (when planning needed)
    ├─ Coder (when implementation needed)
    ├─ Tester (when validation needed)
    └─ Refiner (when fixing needed)
```
An example:
```
1. Master receives task
2. Master decides: "Need deep analysis first"
   → Calls Analyzer
3. Master reviews analysis, decides: "Needs planning"
   → Calls Planner
4. Master reviews plan, decides: "Coder can start"
   → Calls Coder
5. Master reviews code, decides: "Run Tester"
   → Calls Tester
6. Master reviews test result, decides: "Loop Coder+Tester" or "Done"
   → Either repeats steps 4-5 OR calls Refiner
7. Master decides work is complete
```

#### Implementation strategy
```
src/core/
├── agent.py (keep current functions)
├── agents/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── planner.py
│   ├── coder.py
│   ├── tester.py
│   └── refiner.py
├── orchestrator.py (agent manager)
└── multi_agent_pipeline.py (graph builder)
```


### OPTION 2
3 Agents with distinct roles:
- Strategist: Analyze + Plan
- Developer: Generate code
- Quality: Review + Refine

```
Strategist → Developer → Quality (loop back if needed)
```

```python
from typing_extensions import TypedDict
from typing import Optional, List

class MultiAgentState(TypedDict):
    """Shared state for all agents in the pipeline"""
    # Task info
    task_id: str
    signature: str
    docstring: str
    examples: Optional[str]
    model: str
    
    # Agent outputs
    analysis: Optional[str]
    plan: Optional[str]
    code: Optional[str]
    review: Optional[str]
    exec_result: Optional[dict]
    
    # Tracking
    refinement_count: int
    regeneration_count: int
    replan_count: int
    agent_history: List[str]
    feedback_loop: List[dict]
```
```python
from src.core.llm import call_llm
from src.tools.executor import execute_code
from src.utils.code_parser import extract_python_code

class StrategistAgent:
    """Analyzes tasks and creates plans"""
    
    def __init__(self, model: str):
        self.model = model
        self.name = "Strategist"
    
    def execute(self, state: MultiAgentState) -> MultiAgentState:
        print(f">> {self.name.upper()} AGENT")
        
        # Analyze task
        analysis_prompt = (
            "Analyze the following programming task.\n\n"
            "- Extract required behavior\n"
            "- Identify constraints\n"
            "- Identify edge cases\n"
            "- Do NOT write code\n\n"
            f"Function signature:\n{state['signature']}\n\n"
            f"Docstring:\n{state['docstring']}"
        )
        if state.get('examples'):
            analysis_prompt += f"\n\nExamples:\n{state['examples']}"
        
        state["analysis"] = call_llm(user_prompt=analysis_prompt, model=self.model)
        
        # Create plan
        plan_prompt = (
            "Based on the analysis below, produce a clear step-by-step plan "
            "to implement the function.\n\n"
            f"Analysis:\n{state['analysis']}"
        )
        state["plan"] = call_llm(user_prompt=plan_prompt, model=self.model)
        
        state["agent_history"].append(self.name)
        return state


class DeveloperAgent:
    """Generates code based on plans"""
    
    def __init__(self, model: str):
        self.model = model
        self.name = "Developer"
    
    def execute(self, state: MultiAgentState) -> MultiAgentState:
        print(f">> {self.name.upper()} AGENT")
        
        prompt = (
            "Using the plan below, generate the Python function.\n\n"
            "Constraints:\n"
            "- Follow the function signature EXACTLY\n"
            "- Do not include explanations\n"
            "- Do not include markdown\n"
            "- Output ONLY valid Python code\n\n"
            f"Function signature:\n{state['signature']}\n\n"
            f"Plan:\n{state['plan']}"
        )
        
        raw_code = call_llm(user_prompt=prompt, model=self.model)
        state["code"] = extract_python_code(raw_code)
        state["agent_history"].append(self.name)
        state["regeneration_count"] = state.get("regeneration_count", 0)
        
        return state


class QualityAgent:
    """Reviews code, executes it, and refines if needed"""
    
    def __init__(self, model: str, max_refinements: int = 3):
        self.model = model
        self.name = "Quality"
        self.max_refinements = max_refinements
    
    def execute(self, state: MultiAgentState) -> MultiAgentState:
        print(f">> {self.name.upper()} AGENT")
        
        # Execute code
        exec_result = execute_code(state["code"])
        state["exec_result"] = exec_result
        
        # Review code
        review_prompt = (
            "Review the Python code below.\n\n"
            f"Code:\n{state['code']}\n\n"
            f"Execution Results:\n"
            f"- Success: {exec_result['success']}\n"
            f"- Error: {exec_result['error'] or 'None'}\n"
            f"- Output: {exec_result['output'] or 'None'}\n\n"
            "Review checklist:\n"
            "- Identify logical errors\n"
            "- If code failed to execute, explain why\n"
            "- Identify violations of the function signature\n"
            "- If code appears correct, state that explicitly\n\n"
            "Provide a concise review that will guide refinement."
        )
        
        state["review"] = call_llm(user_prompt=review_prompt, model=self.model)
        state["agent_history"].append(self.name)
        
        # Log execution result
        print(f"Execution: {'✅ SUCCESS' if exec_result['success'] else '❌ FAILED'}")
        
        return state
    
    def refine(self, state: MultiAgentState) -> MultiAgentState:
        """Attempt to refine code based on review"""
        print(f">> {self.name.upper()} REFINING (attempt {state['refinement_count'] + 1})")
        
        prompt = (
            "You previously generated this code:\n\n"
            f"{state['code']}\n\n"
            "You then produced this review:\n\n"
            f"{state['review']}\n\n"
            "If issues were identified, fix the code.\n"
            "If no issues were found, return the code unchanged.\n\n"
            "Constraints:\n"
            "- Output ONLY the final Python code"
        )
        
        raw_code = call_llm(user_prompt=prompt, model=self.model)
        refined_code = extract_python_code(raw_code)
        
        # Test refined code
        refined_result = execute_code(refined_code)
        
        state["code"] = refined_code
        state["exec_result"] = refined_result
        state["refinement_count"] += 1
        
        print(f"Refinement: {'✅ SUCCESS' if refined_result['success'] else '❌ FAILED'}")
        
        return state
```

Possible workflow:
- OPTION 1
```
Strategist → Developer → Quality (passes on first try)
                            ↓
                          END
```
An example:

```
Task: Write a function that adds two numbers
def add(a: int, b: int) -> int:
    """Add two numbers and return the result"""

STRATEGIST OUTPUT:
- Analysis: "Need to add two parameters, return sum"
- Plan: "1. Take two integer inputs
         2. Add them using + operator
         3. Return the result"

DEVELOPER OUTPUT:
- Code: "def add(a: int, b: int) -> int:
             return a + b"

QUALITY OUTPUT (Test):
- Execute: ✅ add(2, 3) = 5 (PASS)
- Execute: ✅ add(-1, 1) = 0 (PASS)
- Review: "Code is correct. No issues found."
- Result: SUCCESS ✅

Total cost: 3 agent calls (Strategist + Developer + Quality once)
```
- OPTION 2
```
Strategist → Developer → Quality (fails)
                            ↓
                        (refine code)
                            ↓
                        Quality (passes)
                            ↓
                          END
```
An example:
```
Task: Find the maximum number in a list
def find_max(numbers: list[int]) -> int:
    """Return the maximum number in the list"""

STRATEGIST OUTPUT:
- Plan: "1. Initialize max to first element
         2. Loop through remaining elements
         3. Update max if current > max
         4. Return max"

DEVELOPER OUTPUT (attempt 1):
- Code: "def find_max(numbers: list[int]) -> int:
             max_val = numbers[0]
             for num in numbers:
                 if num > max_val:
                     max_val = num
             return max_val"

QUALITY OUTPUT (Test attempt 1):
- Execute: ✅ find_max([3, 1, 4, 1, 5]) = 5 (PASS)
- Execute: ❌ find_max([]) = IndexError! (FAIL)
- Review: "Code fails on empty list. Need to handle edge case."
- Refinement count: 1

QUALITY OUTPUT (refine attempt 1):
- Refined Code: "def find_max(numbers: list[int]) -> int:
                     if not numbers:
                         return float('-inf')
                     max_val = numbers[0]
                     for num in numbers:
                         if num > max_val:
                             max_val = num
                     return max_val"

QUALITY OUTPUT (Test attempt 2):
- Execute: ✅ find_max([3, 1, 4, 1, 5]) = 5 (PASS)
- Execute: ✅ find_max([]) = -inf (PASS)
- Execute: ✅ find_max([-10, -5, -1]) = -1 (PASS)
- Review: "All tests pass. Edge case handled."
- Result: SUCCESS ✅

Total cost: 3 agent calls + 1 refinement loop
```
- OPTION 3
```
Strategist → Developer → Quality (fails)
                            ↓
                        (refine #1)
                        Quality (fails)
                            ↓
                        (refine #2)
                        Quality (passes)
                            ↓
                          END
```

An example:
```
Task: Check if a string is a palindrome (ignoring spaces and case)
def is_palindrome(s: str) -> bool:
    """Return True if string is a palindrome, False otherwise"""

STRATEGIST OUTPUT:
- Plan: "1. Convert to lowercase
         2. Remove spaces and special characters
         3. Compare string with its reverse
         4. Return True if equal, False otherwise"

DEVELOPER OUTPUT (attempt 1):
- Code: "def is_palindrome(s: str) -> bool:
             s = s.lower().replace(' ', '')
             return s == s[::-1]"

QUALITY OUTPUT (Test attempt 1):
- Execute: ✅ is_palindrome("A man a plan a canal Panama") - FAIL!
  └─ Expected: True, Got: False
- Execute: ❌ is_palindrome("racecar") - FAIL!
  └─ Special chars not handled!
- Review: "Code doesn't remove punctuation. Only removes spaces."
- Refinement count: 1

QUALITY OUTPUT (refine attempt 1):
- Refined Code: "def is_palindrome(s: str) -> bool:
                     import string
                     s = s.lower()
                     s = ''.join(c for c in s if c.isalnum())
                     return s == s[::-1]"

QUALITY OUTPUT (Test attempt 2):
- Execute: ✅ is_palindrome("A man, a plan, a canal: Panama") = True (PASS)
- Execute: ✅ is_palindrome("race a car") = False (PASS)
- Execute: ❌ is_palindrome("") = True (UNEXPECTED!)
- Review: "Empty string case returns True (debatable). Check if expected."
- Refinement count: 2

QUALITY OUTPUT (refine attempt 2):
- Refined Code: "def is_palindrome(s: str) -> bool:
                     s = s.lower()
                     s = ''.join(c for c in s if c.isalnum())
                     if not s:  # Empty string after filtering
                         return True  # Treat empty as palindrome
                     return s == s[::-1]"

QUALITY OUTPUT (Test attempt 3):
- Execute: ✅ is_palindrome("A man, a plan, a canal: Panama") = True (PASS)
- Execute: ✅ is_palindrome("race a car") = False (PASS)
- Execute: ✅ is_palindrome("") = True (PASS)
- Execute: ✅ is_palindrome("0P") = False (PASS)
- Review: "All tests pass. Edge cases handled correctly."
- Result: SUCCESS ✅

Total cost: 3 agent calls + 2 refinement loops
```

- OPTION 4:
```
Strategist → Developer (code 1) → Quality (fails)
                                      ↓
                        (refine fails after max)
                                      ↓
                        Call Developer again
                                  ↓
                        Developer (code 2)
                                  ↓
                              Quality
                                  ↓
                                END
```

An example:
```
Task: Generate nth Fibonacci number efficiently
def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number (0-indexed)"""

STRATEGIST OUTPUT:
- Plan: "1. Handle base cases (n=0, n=1)
         2. Build up Fibonacci sequence iteratively
         3. Return the nth number"

DEVELOPER OUTPUT (attempt 1 - Recursive approach):
- Code: "def fibonacci(n: int) -> int:
             if n <= 1:
                 return n
             return fibonacci(n-1) + fibonacci(n-2)"

QUALITY OUTPUT (Test attempt 1):
- Execute: ✅ fibonacci(5) = 5 (PASS, but SLOW)
- Execute: ✅ fibonacci(10) = 55 (PASS, but very SLOW)
- Execute: ❌ fibonacci(30) = TIMEOUT! (FAIL)
- Review: "Recursive approach causes exponential time complexity!
           Previous approach fundamentally flawed for this task.
           Need iterative solution with memoization or dynamic programming."
- Refinement count: 3 (exhausted)

DEVELOPER OUTPUT (attempt 2 - Iterative approach):
- Code: "def fibonacci(n: int) -> int:
             if n <= 1:
                 return n
             a, b = 0, 1
             for _ in range(2, n + 1):
                 a, b = b, a + b
             return b"

QUALITY OUTPUT (Test attempt 2):
- Execute: ✅ fibonacci(5) = 5 (PASS, instant)
- Execute: ✅ fibonacci(10) = 55 (PASS, instant)
- Execute: ✅ fibonacci(30) = 832040 (PASS, instant)
- Execute: ✅ fibonacci(100) = 354224848179261915075 (PASS, instant)
- Review: "Excellent! O(n) time complexity. All tests pass."
- Result: SUCCESS ✅

Total cost: 3 agent calls + 1 complete regeneration
Key insight: Plan was correct, but implementation strategy needed change
```

#### Implementation strategy
```
src/core/
├── agents/
│   ├── __init__.py
│   ├── strategist.py    # analyze + plan
│   ├── developer.py     # generate_code
│   └── quality.py       # review + refine
├── multi_agent_pipeline.py
└── multi_agent_state.py
```