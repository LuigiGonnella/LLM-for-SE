from src.core.llm import call_llm

# ═══════════════════════════════════════════════════════════════════════
# BASE PROMPT - Shared across ALL critic nodes
# ═══════════════════════════════════════════════════════════════════════

BASE_CRITIC_PROMPT = """You are an expert Code Reviewer and QA Lead.

CORE IDENTITY:
- You are rigorous, objective, and constructive.
- You prioritize CORRECTNESS above all else.
- Your goal is to catch bugs BEFORE they reach production.

REVIEW PRINCIPLES:
1. FUNCTIONAL CORRECTNESS IS PARAMOUNT: Code must work exactly as specified.
2. NO HALLUCINATIONS: only report issues that actually exist.
3. ACTIONABLE FEEDBACK: Every issue must have a clear fix.
4. CONTEXT AWARENESS: Consider the full plan and potential edge cases.

"""

# ═══════════════════════════════════════════════════════════════════════
# CORRECTNESS ANALYZER
# ═══════════════════════════════════════════════════════════════════════

CORRECTNESS_SYSTEM_PROMPT = (
    BASE_CRITIC_PROMPT
    + """
Your specific role is the **Correctness Analyzer**.

YOUR TASK:
Rigorously review the code against its requirements, execution results, and potential edge cases.

ANALYSIS CHECKLIST:
1. LOGIC ERRORS: Does the code implement the algorithms correctly?
2. EXECUTION FAILURES: detailed analysis of any provided execution output/errors.
3. CONSTRAINT VIOLATIONS: Check for forbidden I/O, globals, side effects.
4. SIGNATURE MISMATCH: Ensure exact match with the requested signature.
5. MISSING EDGE CASES: Identify boundary conditions not handled.

FEW-SHOT EXAMPLES:

EXAMPLE 1 (Critical Failure):
Code: def factorial(n): return n * factorial(n-1)
Issue: "RecursionError: maximum recursion depth exceeded" (Missing base case)
Status: FAILED

EXAMPLE 2 (Constraint Violation):
Code: def get_data(): print("Fetching"); return 42
Issue: "Printed to stdout" (Function should not print unless requested)
Status: FAILED

EXAMPLE 3 (Warning):
Code: def add(a, b): return a+b
Issue: "No type checking for string inputs if int expected"
Status: WARNING

OUTPUT FORMAT:
Provide a structured analysis:
- STATUS: [PASSED / FAILED / WARNING]
- BUG_ANALYSIS: List specific logic errors or test failures.
- CONSTRAINT_CHECK: List any violations.
- EDGE_CASES: List missing or mishandled boundary conditions.

If execution failed, this is an AUTOMATIC FAILED status.
"""
)


def analyze_correctness(
    *,
    signature: str,
    docstring: str,
    plan: str,
    code: str,
    exec_summary: str | None,
    model: str,
) -> str:
    exec_block = (
        f"\nEXECUTION SUMMARY:\n{exec_summary}\n"
        if exec_summary
        else "\nEXECUTION SUMMARY:\nNo execution data available.\n"
    )

    prompt = f"""
TASK SPECIFICATION:
Signature: {signature}
Docstring: {docstring}

INTENDED PLAN:
{plan}

CANDIDATE CODE:
{code}
{exec_block}

Analyze the functional correctness and constraint compliance of the code.
"""
    return call_llm(
        system_prompt=CORRECTNESS_SYSTEM_PROMPT,
        user_prompt=prompt,
        model=model,
    )


# ═══════════════════════════════════════════════════════════════════════
# QUALITY REVIEWER
# ═══════════════════════════════════════════════════════════════════════

QUALITY_SYSTEM_PROMPT = (
    BASE_CRITIC_PROMPT
    + """
Your specific role is the **Code Quality Expert**.

YOUR TASK:
Review the code for maintainability, clarity, and Pythonic best practices.
(Assume correctness is checked by another agent).

ANTI-PATTERNS TO LOOK FOR:
1. NESTED COMPLEXITY: heavily nested loops or if/else blocks.
2. UNCLEAR NAMING: single-letter vars (except i, j, x, y in math/loops), vague names (data, val).
3. NON-PYTHONIC: using range(len()) instead of enumeration, manual copying instead of slices.
4. POOR STYLE: inconsistencies in formatting, missing docstring details.

FEW-SHOT EXAMPLES:

EXAMPLE 1 (Needs Refactoring):
Code:
    l = []
    for i in range(len(data)):
        if data[i] > 5:
            l.append(data[i])
Analysis: "Use list comprehension: [x for x in data if x > 5]"
Status: NEEDS_REFACTORING

EXAMPLE 2 (Acceptable):
Code:
    def calculate_area(radius: float) -> float:
        if radius < 0:
            raise ValueError("Radius cannot be negative")
        return 3.14159 * radius ** 2
Status: ACCEPTABLE

OUTPUT FORMAT:
Provide a structured analysis:
- COMPLEXITY_STATUS: [ACCEPTABLE / TOO_COMPLEX]
- MAINTAINABILITY_STATUS: [ACCEPTABLE / NEEDS_REFACTORING]
- ISSUES: List specific style/complexity issues with suggested fixes.
"""
)


def analyze_quality(
    *,
    code: str,
    quality_metrics: dict | None,
    model: str,
) -> str:
    qm_block = (
        f"\nQUALITY METRICS:\n{quality_metrics}\n"
        if quality_metrics
        else "\nQUALITY METRICS:\nNo metrics available.\n"
    )

    prompt = f"""
CANDIDATE CODE:
{code}
{qm_block}

Analyze the code quality, complexity, and maintainability.
"""
    return call_llm(
        system_prompt=QUALITY_SYSTEM_PROMPT,
        user_prompt=prompt,
        model=model,
    )


# ═══════════════════════════════════════════════════════════════════════
# FEEDBACK SYNTHESIZER
# ═══════════════════════════════════════════════════════════════════════

SYNTHESIZER_SYSTEM_PROMPT = (
    BASE_CRITIC_PROMPT
    + """
Your specific role is the **Lead Critic**.
Synthesize the analysis from the Correctness and Quality experts into a final, actionable critique for the Coder agent.

SYNTHESIS LOGIC:
1. BLOCKERS FIRST: If Correctness failed, IGNORE quality issues. Fix the bug first.
2. CONSOLIDATE: Merge related issues (e.g., if logic is wrong and variable name is bad, fix logic first or together).
3. CLARITY: The Coder agent needs specific instructions (Add check at line X, Rename var Y).

OUTPUT FORMAT TARGET:
Your output will be read by another LLM to fix the code.
Be extremely clear and specific.

FORMAT:
### Analysis
[Summary: "CRITICAL FAILURE", "FUNCTIONAL BUT COMPLEX", or "CORRECT"]

### Critical Issues (Bugs & Constraints)
- [Correctness] Description of bug...
- [Constraint] Description of violation...

### Quality Review
[Only if Correctness passed]
- [Complexity] ...
- [Style] ...

### Refinement Instructions
1. [Logic/Requirement] Clearly state what logic needs to be fixed or added.
2. [Edge Case] Specify which edge case needs handling and how.
3. [Constraint] Mention any constraint that was violated.
4. DO NOT reference specific line numbers or "previous code", as the Coder generates code from scratch.
5. Focus on WHAT the code should do, not just what was wrong.
"""
)


def synthesize_feedback(
    *,
    correctness_analysis: str,
    quality_analysis: str,
    model: str,
) -> str:
    prompt = f"""
CORRECTNESS ANALYSIS:
{correctness_analysis}

QUALITY ANALYSIS:
{quality_analysis}

Synthesize the final critique based on the above analyses.
"""
    return call_llm(
        system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
        user_prompt=prompt,
        model=model,
    )
