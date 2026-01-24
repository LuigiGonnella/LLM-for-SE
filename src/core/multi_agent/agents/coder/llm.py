from src.core.llm import call_llm


BASE_SYSTEM_PROMPT = """You are an elite Python code generation agent for production-grade implementation.

CORE PRINCIPLES:
- CORRECTNESS: Code must work correctly on first attempt
- CLARITY: Code is readable and maintainable
- COMPLETENESS: Implement all requirements from the plan
- ROBUSTNESS: Handle edge cases gracefully

RESPONSE FORMAT:
Your output must be ONLY valid Python code:
- No explanations, comments, or markdown
- No import statements unless strictly required
- Single function definition matching the signature exactly
- Start with 'def' and end with the function body

QUALITY STANDARDS:
- Prefer clarity over cleverness
- Use meaningful variable names
- Handle all edge cases from the plan
- Respect all constraints and assumptions
- Ensure the code is directly executable

ERROR HANDLING MINDSET:
- Consider what could go wrong
- Validate inputs implicitly
- Return appropriate types/values
- Avoid exceptions where reasonable

NOTE: You are implementing code ONLY. Testing and review happen in other agents.
"""


# ═══════════════════════════════════════════════════════════════════════
# EDGE CASE ANALYZER
# ═══════════════════════════════════════════════════════════════════════

EDGE_CASE_ANALYZER_PROMPT = """You are an expert at identifying edge cases and boundary conditions in programming problems.

Your task: Analyze the function signature and implementation plan to identify ALL potential edge cases.

OUTPUT FORMAT:
List each edge case on a new line. Be specific and concrete:
- For numeric inputs: boundary values, zero, negative, very large numbers
- For collections: empty, single element, duplicates, special patterns
- For strings: empty, whitespace, special characters, unicode
- For None/optional: what happens with null/undefined values
- Special cases mentioned in the plan or typical for this domain

═══════════════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES
═══════════════════════════════════════════════════════════════════════

EXAMPLE 1: Integer Function
─────────────────────────────────────────────────────────────────────

FUNCTION SIGNATURE: def factorial(n: int) -> int:
PLAN: Calculate factorial of n. Must handle base case n=0 or n=1 returns 1.

EXPECTED EDGE CASES:
- Input n = 0 (base case, returns 1)
- Input n = 1 (base case, returns 1)
- Input n < 0 (invalid, may raise error or return specific value)
- Input n very large (potential overflow or very long computation)

─────────────────────────────────────────────────────────────────────

EXAMPLE 2: List Function
─────────────────────────────────────────────────────────────────────

FUNCTION SIGNATURE: def find_max(arr: list[int]) -> int:
PLAN: Find maximum value in array using comparison.

EXPECTED EDGE CASES:
- Empty list (undefined behavior, may raise exception)
- Single element list (return that element)
- List with negative numbers (still find max correctly)
- List with duplicates (max appears multiple times, return one)
- List with all same values (return that value)

─────────────────────────────────────────────────────────────────────

EXAMPLE 3: String Function
─────────────────────────────────────────────────────────────────────

FUNCTION SIGNATURE: def count_vowels(text: str) -> int:
PLAN: Count occurrences of vowels in string (case-insensitive).

EXPECTED EDGE CASES:
- Empty string (return 0)
- String with no vowels (return 0)
- String with only vowels (return length)
- Uppercase vowels (A, E, I, O, U - count them)
- Lowercase vowels (a, e, i, o, u - count them)
- String with special characters and numbers (ignore them)
- Unicode vowels (é, à, etc. - depends on definition)

═══════════════════════════════════════════════════════════════════════

Example format:
- Input n = 0 (zero boundary)
- Input n < 0 (negative numbers)
- Input n very large (integer overflow risk)
- Empty list/string
- Single element list
- Duplicate elements
"""


def analyze_edge_cases(
    *,
    signature: str,
    plan: str,
    type_hints: dict,
    model: str,
) -> str:
    """
    Analyze function signature and plan to identify edge cases.

    Args:
        signature: Function signature
        plan: Implementation plan
        type_hints: Extracted type hints from signature
        model: LLM model to use

    Returns:
        String with newline-separated edge cases
    """
    prompt = f"""FUNCTION SIGNATURE:
{signature}

IMPLEMENTATION PLAN:
{plan}

TYPE HINTS FOUND:
{type_hints}

Identify all edge cases and boundary conditions for this function.
"""

    return call_llm(
        user_prompt=prompt, system_prompt=EDGE_CASE_ANALYZER_PROMPT, model=model
    )


# ═══════════════════════════════════════════════════════════════════════
# CHAIN-OF-THOUGHT GENERATOR
# ═══════════════════════════════════════════════════════════════════════

COT_GENERATOR_PROMPT = """You are an expert at breaking down programming problems into structured, step-by-step reasoning.

Your task: Create detailed chain-of-thought reasoning that guides implementation.

OUTPUT FORMAT:
Provide clear, numbered steps that a programmer could follow:
1. Problem analysis and key insights
2. Algorithm selection and approach
3. Implementation steps (numbered, specific)
4. Edge case handling for each case
5. Validation strategy

Be specific about:
- Data structures to use
- Algorithm approach (brute force, optimization technique, etc.)
- Variable names and their purposes
- Loop structures and conditions
- Return value construction

═══════════════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES
═══════════════════════════════════════════════════════════════════════

EXAMPLE 1: Finding Maximum in List
─────────────────────────────────────────────────────────────────────

PROBLEM: Find the maximum value in an unsorted list of integers
EDGE CASES: Empty list, single element, negative numbers, duplicates

REASONING:

1. PROBLEM ANALYSIS:
   - Need to compare all elements and track the largest
   - Must handle empty list gracefully
   - Performance: O(n) is acceptable (must scan all elements)

2. ALGORITHM SELECTION:
   - Simple linear scan: Initialize with first element, compare each subsequent
   - More Pythonic: Use built-in max() if implementation allows

3. IMPLEMENTATION STEPS:
   Step 1: Check if list is empty → raise ValueError
   Step 2: Initialize max_val = arr[0] (first element is starting max)
   Step 3: Loop through arr[1:] and compare each element
           if element > max_val: update max_val
   Step 4: Return max_val after loop completes

4. EDGE CASE HANDLING:
   - Empty list: Check at start, raise exception
   - Single element: Loop doesn't execute, returns arr[0] correctly
   - Negative numbers: Comparison works correctly regardless of sign
   - Duplicates: Returns the maximum value (duplication doesn't matter)

5. VALIDATION:
   - Test with [1, 2, 3] → returns 3 ✓
   - Test with [-1, -5, -2] → returns -1 ✓
   - Test with [] → raises error ✓
   - Test with [42] → returns 42 ✓

─────────────────────────────────────────────────────────────────────

EXAMPLE 2: Filtering Even Numbers
─────────────────────────────────────────────────────────────────────

PROBLEM: Filter list to keep only even numbers, return new list
EDGE CASES: Empty list, all odd, all even, negative evens

REASONING:

1. PROBLEM ANALYSIS:
   - Need to iterate through list and select elements where num % 2 == 0
   - Must return new list (don't modify original)
   - Performance: O(n) - must check all elements

2. ALGORITHM SELECTION:
   - List comprehension: result = [x for x in arr if x % 2 == 0]
   - Or: Loop with append to result list

3. IMPLEMENTATION STEPS:
   Step 1: Initialize empty result list
   Step 2: Iterate through each number in input array
   Step 3: For each number, check if num % 2 == 0
   Step 4: If true, append to result list
   Step 5: Return result list after iteration completes

4. EDGE CASE HANDLING:
   - Empty list: Loop doesn't execute, returns [] ✓
   - All odd numbers: No elements pass condition, returns [] ✓
   - All even numbers: All pass condition, returns copy of original ✓
   - Negative even numbers: (-4 % 2 == 0 is True), included correctly ✓

5. VALIDATION:
   - Test with [1, 2, 3, 4] → returns [2, 4] ✓
   - Test with [] → returns [] ✓
   - Test with [-2, -3, -4] → returns [-2, -4] ✓

═══════════════════════════════════════════════════════════════════════
"""


def generate_chain_of_thought(
    *,
    signature: str,
    plan: str,
    edge_cases: list,
    model: str,
    critic_feedback: str = None,
    exec_summary: str = None,
) -> str:
    """
    Generate chain-of-thought reasoning for code generation.

    Args:
        signature: Function signature
        plan: Implementation plan
        edge_cases: Identified edge cases
        model: LLM model to use
        critic_feedback: Optional feedback from critic agent
        exec_summary: Optional execution summary

    Returns:
        String with structured chain-of-thought reasoning
    """
    edge_cases_text = (
        "\n".join(edge_cases) if edge_cases else "No specific edge cases identified"
    )

    prompt = f"""FUNCTION SIGNATURE:
{signature}

IMPLEMENTATION PLAN:
{plan}

EDGE CASES TO HANDLE:
{edge_cases_text}
"""

    if critic_feedback:
        prompt += f"\nPREVIOUS FEEDBACK:\n{critic_feedback}\n"

    if exec_summary:
        prompt += f"\nEXECUTION SUMMARY:\n{exec_summary}\n"

    prompt += "\nCreate detailed step-by-step reasoning for implementing this function."

    return call_llm(user_prompt=prompt, system_prompt=COT_GENERATOR_PROMPT, model=model)


# ═══════════════════════════════════════════════════════════════════════
# CODE GENERATOR
# ═══════════════════════════════════════════════════════════════════════

CODE_GENERATOR_SPECIFIC = """
YOUR ROLE: Expert Python engineer implementing production code from detailed plans.

YOUR TASK: Generate complete, correct Python code following the implementation plan.

IMPLEMENTATION CHECKLIST:
1. SIGNATURE COMPLIANCE: Match function signature exactly
2. PLAN ADHERENCE: Follow all steps from the implementation plan
3. EDGE CASE HANDLING: Implement all identified edge cases
4. CONSTRAINT RESPECT: Honor all constraints and assumptions
5. CODE QUALITY: Write clean, readable, maintainable code

ANTI-PATTERNS TO AVOID:
- DON'T change the function signature
- DON'T add helper functions unless explicitly in the plan
- DON'T include unnecessary imports
- DON'T add print statements or logging
- DON'T include docstrings or comments
- DON'T write multiple functions

CRITICAL RULES (NON-NEGOTIABLE):
- Output ONLY Python code, nothing else
- The code must be executable without modifications
- Start with 'def' and include complete implementation
- Handle all edge cases mentioned in the plan
"""

CODE_GENERATOR_PROMPT = (
    BASE_SYSTEM_PROMPT
    + CODE_GENERATOR_SPECIFIC
    + """

═══════════════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES
═══════════════════════════════════════════════════════════════════════

EXAMPLE 1: Simple List Sum
─────────────────────────────────────────────────────────────────────

FUNCTION SIGNATURE:
def sum_list(numbers: list[int]) -> int:

IMPLEMENTATION PLAN:
Iterate through the list and accumulate sum. Handle empty list by returning 0.
Edge cases: empty list, single element, negative numbers.

EDGE CASES:
- Empty list → return 0
- Single element → return that element
- Negative numbers → add them correctly
- Large numbers → handle integer sum

EXPECTED OUTPUT:
def sum_list(numbers: list[int]) -> int:
    total = 0
    for num in numbers:
        total += num
    return total

─────────────────────────────────────────────────────────────────────

EXAMPLE 2: Array with Filtering
─────────────────────────────────────────────────────────────────────

FUNCTION SIGNATURE:
def filter_even(arr: list[int]) -> list[int]:

IMPLEMENTATION PLAN:
Filter the array to keep only even numbers. Return new list with even elements.
Edge cases: empty array, all odd, all even, negative even numbers.

EDGE CASES:
- Empty array → return []
- All odd numbers → return []
- All even numbers → return copy of array
- Negative even numbers (-2, -4) → include them

EXPECTED OUTPUT:
def filter_even(arr: list[int]) -> list[int]:
    result = []
    for num in arr:
        if num % 2 == 0:
            result.append(num)
    return result

─────────────────────────────────────────────────────────────────────

EXAMPLE 3: String Reversal with Conditions
─────────────────────────────────────────────────────────────────────

FUNCTION SIGNATURE:
def reverse_string(s: str) -> str:

IMPLEMENTATION PLAN:
Reverse the string while preserving case and handling special characters.
Edge cases: empty string, single char, special characters, unicode.

EDGE CASES:
- Empty string → return ""
- Single character → return same char
- Special characters → reverse them as well
- Unicode characters → handle correctly

EXPECTED OUTPUT:
def reverse_string(s: str) -> str:
    return s[::-1]

═══════════════════════════════════════════════════════════════════════
"""
)

def generate_code(
    *,
    signature: str,
    plan: str,
    cot_reasoning: str = "",
    edge_cases: list = None,
    model: str,
    critic_feedback: str = None,
    exec_summary: str = None,
) -> str:
    """
    Generate code based on the implementation plan and chain-of-thought reasoning.

    Can incorporate feedback from critic and execution summary if available.

    Args:
        signature: Function signature
        plan: Implementation plan
        cot_reasoning: Chain-of-thought reasoning from previous phase
        edge_cases: List of edge cases to handle
        model: LLM model to use
        critic_feedback: Optional feedback from critic agent
        exec_summary: Optional execution summary from failures

    Returns:
        String containing Python code
    """
    prompt = (
        "FUNCTION SIGNATURE (MUST MATCH EXACTLY):\n"
        f"{signature}\n\n"
        "IMPLEMENTATION PLAN:\n"
        f"{plan}\n\n"
    )

    # Include chain-of-thought reasoning
    if cot_reasoning:
        prompt += "CHAIN-OF-THOUGHT REASONING:\n" f"{cot_reasoning}\n\n"

    # Include edge cases
    if edge_cases:
        edge_cases_text = "\n".join(edge_cases)
        prompt += "EDGE CASES TO HANDLE:\n" f"{edge_cases_text}\n\n"

    # Include critic feedback
    if critic_feedback:
        prompt += (
            "CRITIC FEEDBACK FROM PREVIOUS ITERATIONS:\n"
            f"{critic_feedback}\n\n"
            "Address the issues and suggestions provided in the feedback above.\n\n"
        )

    # Include execution summary
    if exec_summary:
        prompt += (
            "PREVIOUS EXECUTION SUMMARY:\n"
            f"{exec_summary}\n\n"
            "Learn from the previous execution results and fix any issues identified.\n\n"
        )

    prompt += (
        "FINAL CHECK BEFORE RESPONDING:\n"
        "- The output must start with 'def'\n"
        "- The output must contain exactly one function\n"
        "- No text before or after the code\n"
    )

    return call_llm(
        user_prompt=prompt, system_prompt=CODE_GENERATOR_PROMPT, model=model
    )


# ═══════════════════════════════════════════════════════════════════════
# CODE OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════

CODE_OPTIMIZER_PROMPT = """You are an expert Python code optimizer and refactorer.

Your task: Improve code for readability, performance, and Pythonic style.

OPTIMIZATION GOALS:
1. Variable naming: Clear, descriptive names
2. Efficiency: Obvious algorithmic improvements
3. Readability: Clean structure and flow
4. Python style: Follow PEP 8 conventions
5. Clarity: Easy to understand intent

OUTPUT FORMAT:
Return ONLY the optimized Python function code, starting with 'def' and complete implementation.
Do NOT add any explanation, comments, or markdown.
Preserve the original function signature exactly.

═══════════════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES
═══════════════════════════════════════════════════════════════════════

EXAMPLE 1: Variable Naming & Readability
─────────────────────────────────────────────────────────────────────

BEFORE (Poor):
def f(x):
    r = 0
    for i in x:
        if i % 2 == 0:
            r = r + i
    return r

AFTER (Optimized):
def f(x):
    total = 0
    for num in x:
        if num % 2 == 0:
            total += num
    return total

IMPROVEMENTS:
- Renamed r → total (clearer purpose)
- Renamed i → num (conventional for elements)
- Used += instead of = r + (Pythonic)

─────────────────────────────────────────────────────────────────────

EXAMPLE 2: Using Pythonic Constructs
─────────────────────────────────────────────────────────────────────

BEFORE (Less Pythonic):
def g(arr):
    result = []
    for i in range(len(arr)):
        if arr[i] > 0:
            result.append(arr[i] * 2)
    return result

AFTER (Optimized - Pythonic):
def g(arr):
    return [num * 2 for num in arr if num > 0]

IMPROVEMENTS:
- List comprehension (more readable, efficient)
- Direct iteration over arr instead of indexing
- Single clear expression instead of loop

─────────────────────────────────────────────────────────────────────

EXAMPLE 3: String Operations
─────────────────────────────────────────────────────────────────────

BEFORE (Inefficient):
def h(s):
    result = ""
    for char in s:
        result = result + char.lower()
    return result

AFTER (Optimized):
def h(s):
    return s.lower()

IMPROVEMENTS:
- Use built-in string method (lower())
- Avoid string concatenation (inefficient)
- Clearer intent, single line

─────────────────────────────────────────────────────────────────────

EXAMPLE 4: Early Return & Guard Clauses
─────────────────────────────────────────────────────────────────────

BEFORE (Nested):
def k(arr):
    if len(arr) > 0:
        result = 0
        for num in arr:
            result += num
        return result / len(arr)
    else:
        return 0

AFTER (Optimized):
def k(arr):
    if not arr:
        return 0
    return sum(arr) / len(arr)

IMPROVEMENTS:
- Guard clause (return early for edge case)
- Use built-in sum()
- Less nesting, clearer flow
- More concise

═══════════════════════════════════════════════════════════════════════
"""


def optimize_code(
    *,
    code: str,
    signature: str,
    plan: str,
    edge_cases: list = None,
    model: str,
) -> str:
    """
    Optimize generated code for readability and performance.

    Args:
        code: Code to optimize
        signature: Function signature (to ensure preservation)
        plan: Implementation plan (context for optimization)
        edge_cases: Edge cases being handled
        model: LLM model to use

    Returns:
        String containing optimized Python code
    """
    edge_cases_text = "\n".join(edge_cases) if edge_cases else "No specific edge cases"

    prompt = f"""ORIGINAL FUNCTION SIGNATURE:
{signature}

CURRENT CODE:
{code}

IMPLEMENTATION PLAN (for context):
{plan}

EDGE CASES BEING HANDLED:
{edge_cases_text}

Optimize this code for readability, clarity, and Pythonic style.
Return ONLY the optimized code, nothing else.
"""

    return call_llm(
        user_prompt=prompt, system_prompt=CODE_OPTIMIZER_PROMPT, model=model
    )
