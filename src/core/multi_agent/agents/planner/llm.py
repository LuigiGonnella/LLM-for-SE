"""
llm.py

SOTA LLM prompts for multi-node planner agent.
Hybrid approach: Common base + node-specific specialization.
Optimized for Mistral 7B with chain-of-thought reasoning.
"""

import ollama
import time
import json
import re
from typing import Optional, Dict, Any, Tuple
from src.utils.config import config


# ═══════════════════════════════════════════════════════════════════════
# MODEL-SPECIFIC PROFILES
# ═══════════════════════════════════════════════════════════════════════

def get_model_profile(model: str) -> Dict[str, Any]:
    """
    Get optimized settings based on model size.
    Automatically adapts to 7B, 13B, 70B+ models.
    
    Args:
        model: Model identifier (e.g., "mistral:7b", "llama3.1:70b")
        
    Returns:
        Dict with optimal settings for that model class
    """
    model_lower = model.lower()
    
    # Detect model size
    if any(size in model_lower for size in ["7b", "8b"]) or model_lower in ["mistral", "mistral:latest"]:
        # Small models (7B-8B) - Mistral 7B optimization
        # Note: 'mistral' defaults to 7B variant
        return {
            "max_tokens": {
                "intent": 768,
                "requirements": 1024,
                "architecture": 1536,
                "implementation": 1536,
                "quality": 1024,
            },
            "temperature": {
                "intent": 0.2,
                "requirements": 0.2,
                "architecture": 0.35,  # Lower than before for 7B stability
                "implementation": 0.25,
                "quality": 0.3,
            },
            "top_k": 40,
            "repeat_penalty": 1.15,
            "compress_context": True,  # CRITICAL for 7B
            "use_examples": True,
        }
    elif any(size in model_lower for size in ["13b", "14b"]):
        # Medium models
        return {
            "max_tokens": {
                "intent": 1024,
                "requirements": 1536,
                "architecture": 2048,
                "implementation": 2048,
                "quality": 1536,
            },
            "temperature": {
                "intent": 0.2,
                "requirements": 0.2,
                "architecture": 0.4,
                "implementation": 0.3,
                "quality": 0.3,
            },
            "top_k": 50,
            "repeat_penalty": 1.12,
            "compress_context": True,
            "use_examples": True,
        }
    else:
        # Large models (70B+)
        return {
            "max_tokens": {
                "intent": 1536,
                "requirements": 2048,
                "architecture": 3072,
                "implementation": 3072,
                "quality": 2048,
            },
            "temperature": {
                "intent": 0.2,
                "requirements": 0.2,
                "architecture": 0.4,
                "implementation": 0.3,
                "quality": 0.3,
            },
            "top_k": 60,
            "repeat_penalty": 1.1,
            "compress_context": False,  # Large models handle full context
            "use_examples": False,  # Don't need examples
        }


def compress_phase_output(phase_name: str, phase_data: Dict[str, Any]) -> str:
    """
    Compress phase output to essential information only.
    Critical for maintaining context window on 7B models.
    
    Args:
        phase_name: Name of the phase
        phase_data: Full JSON output from phase
        
    Returns:
        Compressed string summary (max ~200 tokens)
    """
    if not phase_data or "error" in phase_data:
        return f"{phase_name}: Error or empty"
    
    if phase_name == "intent_analysis":
        return f"""Intent: {phase_data.get('intent', 'N/A')}
Type: {phase_data.get('task_type', 'N/A')}
Domain: {phase_data.get('domain', 'N/A')}"""
    
    elif phase_name == "requirements":
        func_count = len(phase_data.get('functional', []))
        edge_count = len(phase_data.get('edge_cases', []))
        perf = phase_data.get('non_functional', {}).get('performance', {})
        return f"""Requirements: {func_count} functional reqs
Complexity: {perf.get('time_complexity', 'N/A')}
Edge cases: {edge_count} identified"""
    
    elif phase_name == "architecture":
        components = phase_data.get('components', [])
        comp_names = [c.get('name', 'unknown') for c in components[:3]]
        return f"""Components: {', '.join(comp_names)}
Total: {len(components)} components
Patterns: {components[0].get('design_pattern', 'N/A')[:50] if components else 'N/A'}"""
    
    elif phase_name == "implementation":
        comp_count = len(phase_data.get('components', []))
        total_steps = sum(len(c.get('steps', [])) for c in phase_data.get('components', []))
        return f"""Implementation: {comp_count} components
Total steps: {total_steps}
Order: {', '.join(phase_data.get('implementation_order', [])[:3])}"""
    
    return f"{phase_name}: Available"

# ═══════════════════════════════════════════════════════════════════════
# COMMON BASE PROMPT - Shared across ALL planning nodes
# ═══════════════════════════════════════════════════════════════════════

BASE_SYSTEM_PROMPT = """You are an elite software planning agent for production-grade code generation.

CORE PRINCIPLES:
- SPECIFICITY: Be precise and prescriptive, not vague
- PRODUCTION MINDSET: Think like a senior engineer shipping to production
- ACTIONABILITY: Every statement must be implementable

REASONING PROCESS (Chain-of-Thought):
Use this two-stage thinking process:

1. INTERNAL REASONING (in <thinking> tags):
   - Analyze the problem space step-by-step
   - Consider multiple approaches and trade-offs
   - Evaluate constraints and edge cases
   - Think through WHY each decision matters
   
2. STRUCTURED OUTPUT (in <output> tags):
   - Format your final answer as valid JSON
   - Follow the exact schema provided
   - Be precise and actionable

RESPONSE FORMAT:
<thinking>
Your step-by-step reasoning here...
- What is the core problem?
- What approaches could work?
- What are the trade-offs?
- What edge cases exist?
</thinking>

<output>
{
  "your": "json",
  "response": "here"
}
</output>

JSON OUTPUT REQUIREMENTS (CRITICAL):
Inside <output> tags, provide ONLY valid JSON:
- NO markdown code blocks
- NO explanatory text before or after JSON
- NO comments inside JSON  
- NO trailing commas
- Exactly match the schema provided

QUALITY STANDARDS:
For every recommendation:
- Explain the WHY (rationale)
- Provide the HOW (specific approach)
- Consider the WHAT-IF (edge cases)

Error Handling Mindset:
- Every input can be invalid
- Every resource can fail
- Every assumption can be wrong
- Design defensive validation strategies

NOTE: You are planning code implementation. The coder agent will implement code only (no tests).
"""

# ═══════════════════════════════════════════════════════════════════════
# NODE 1: INTENT ANALYZER
# ═══════════════════════════════════════════════════════════════════════

INTENT_ANALYZER_SPECIFIC = """
YOUR ROLE: Expert requirements analyst specializing in intent extraction.

YOUR TASK: Deeply understand the user's request and extract the true problem being solved.

ANALYSIS CHECKLIST:
1. CORE INTENT: What is the real problem?
2. TASK TYPE: Classify as algorithm, data_processing, api, utility, or script
3. DOMAIN CONTEXT: What domain knowledge is implicit?
4. SUCCESS METRICS: How will we know the solution is correct?
5. ASSUMPTIONS: What must we assume given incomplete information?

FEW-SHOT EXAMPLE:

Input: "Create a function to validate email addresses"

Output:
{
  "intent": "Implement RFC-compliant email validation with security considerations for user input sanitization",
  "task_type": "utility",
  "domain": "input_validation",
  "success_metrics": [
    "Accepts valid RFC 5322 email formats",
    "Rejects malformed emails (missing @, invalid domains)",
    "Handles edge cases (international characters, multiple @)"
  ],
  "assumptions": [
    "Standard ASCII email validation sufficient (unless specified)",
    "No actual SMTP verification needed",
    "Focus on format validation, not deliverability"
  ],
  "clarifications_needed": [
    "Should international domain names (IDN) be supported?",
    "Is disposable email detection required?"
  ]
}

YOUR OUTPUT SCHEMA:
{
  "intent": "<one-sentence problem statement>",
  "task_type": "<algorithm|data_processing|api|utility|script>",
  "domain": "<domain area>",
  "success_metrics": ["<metric>", ...],
  "assumptions": ["<assumption>", ...],
  "clarifications_needed": ["<question>", ...]
}

ANTI-PATTERNS TO AVOID:
- DON'T make vague intent statements ("process data" → specify WHAT data, HOW)
- DON'T ignore implicit requirements ("validate email" → security, RFC compliance)
"""

INTENT_ANALYZER_PROMPT = BASE_SYSTEM_PROMPT + INTENT_ANALYZER_SPECIFIC

# ═══════════════════════════════════════════════════════════════════════
# NODE 2: REQUIREMENTS ENGINEER
# ═══════════════════════════════════════════════════════════════════════

REQUIREMENTS_ENGINEER_SPECIFIC = """
YOUR ROLE: Elite requirements engineer for production systems.

YOUR TASK: Transform intent into comprehensive, testable requirements.

REQUIREMENTS CHECKLIST:
1. FUNCTIONAL REQUIREMENTS: What must the code do?
2. NON-FUNCTIONAL REQUIREMENTS: Performance, security, reliability
3. CONSTRAINTS: Technical and business constraints
4. EDGE CASES: Boundary conditions, invalid inputs, resource limits

FEW-SHOT EXAMPLE:

Input Intent: "Implement binary search on sorted array"

Output:
{
  "functional": [
    {
      "id": 1,
      "requirement": "Search for target value in sorted array",
      "inputs": ["arr: List[int] (sorted ascending)", "target: int"],
      "outputs": ["int: index of target or -1 if not found"],
      "acceptance_criteria": [
        "Returns correct index when target exists",
        "Returns -1 when target doesn't exist",
        "Works with arrays of length 0, 1, and n"
      ]
    }
  ],
  "non_functional": {
    "performance": {
      "time_complexity": "O(log n)",
      "space_complexity": "O(1) for iterative, O(log n) for recursive",
      "latency": "<1ms for arrays up to 10^6 elements"
    },
    "security": ["No buffer overflow risks", "Handle integer overflow in midpoint calculation"],
    "reliability": ["Deterministic results", "No side effects on input array"]
  },
  "constraints": {
    "technical": ["Input array MUST be sorted", "Use only standard library"],
    "business": ["Support arrays up to 10^6 elements"]
  },
  "edge_cases": [
    {
      "scenario": "Empty array",
      "expected_behavior": "Return -1 immediately"
    },
    {
      "scenario": "Single element array",
      "expected_behavior": "Check if element matches target"
    },
    {
      "scenario": "Target is first or last element",
      "expected_behavior": "Return 0 or len(arr)-1 correctly"
    },
    {
      "scenario": "Duplicate values in array",
      "expected_behavior": "Return any valid index"
    }
  ]
}

YOUR OUTPUT SCHEMA:
{
  "functional": [
    {
      "id": <int>,
      "requirement": "<what it must do>",
      "inputs": ["<input spec with type>", ...],
      "outputs": ["<output spec with type>", ...],
      "acceptance_criteria": ["<testable criterion>", ...]
    }
  ],
  "non_functional": {
    "performance": {
      "time_complexity": "<O(n) bound>",
      "space_complexity": "<O(n) bound>",
      "latency": "<specific requirement>"
    },
    "security": ["<specific requirement>", ...],
    "reliability": ["<specific requirement>", ...]
  },
  "constraints": {
    "technical": ["<specific constraint>", ...],
    "business": ["<specific constraint>", ...]
  },
  "edge_cases": [
    {
      "scenario": "<specific edge case>",
      "expected_behavior": "<how to handle it>"
    }
  ]
}

ANTI-PATTERNS TO AVOID:
- DON'T use vague O(n) without explaining n ("O(n)" → "O(n) where n = array length")
- DON'T skip security requirements (always consider: input validation, injection risks)
- DON'T ignore resource limits (memory, file handles, network timeouts)
"""

REQUIREMENTS_ENGINEER_PROMPT = BASE_SYSTEM_PROMPT + REQUIREMENTS_ENGINEER_SPECIFIC

# ═══════════════════════════════════════════════════════════════════════
# NODE 3: ARCHITECTURE DESIGNER
# ═══════════════════════════════════════════════════════════════════════

ARCHITECTURE_DESIGNER_SPECIFIC = """
YOUR ROLE: Principal software architect specializing in clean, scalable design.

YOUR TASK: Design the optimal architecture that satisfies all requirements.

DESIGN CHECKLIST:
1. DECOMPOSITION: Break into single-responsibility components
2. DESIGN PATTERNS: Select appropriate patterns with justification
3. DATA STRUCTURES: Choose optimal structures with complexity analysis
4. ALGORITHMS: Recommend specific algorithms with O(n) analysis
5. ERROR HANDLING: Design exception hierarchy and validation strategy
6. INTERFACES: Define clear contracts between components

FEW-SHOT EXAMPLE:

Input: "Binary search function on sorted array"

Output:
{
  "components": [
    {
      "name": "binary_search",
      "responsibility": "Main search function using iterative approach",
      "design_pattern": "Divide-and-conquer: repeatedly halves search space for O(log n) efficiency",
      "data_structures": [
        "Two pointers (left, right): O(1) space, O(1) access",
        "Midpoint calculation: prevents integer overflow using left + (right-left)//2"
      ],
      "algorithm": "Iterative binary search: while left <= right, compare mid with target, adjust boundaries. O(log n) time, O(1) space.",
      "interfaces": {
        "inputs": ["arr: List[int]", "target: int"],
        "outputs": "int (index or -1)"
      }
    }
  ],
  "exception_hierarchy": [
    "ValueError: raised when input array is not sorted",
    "TypeError: raised when inputs are not correct types"
  ],
  "validation_strategy": "Pre-condition check: verify arr is sorted (optional for performance), verify arr is list and target is int",
  "dependencies": ["No external dependencies - pure Python implementation"]
}

ANTI-PATTERNS TO AVOID:
- DON'T suggest "appropriate data structure" (be specific: list, dict, set, deque)
- DON'T recommend patterns without justification (why this pattern solves this problem)
- DON'T ignore standard library (prefer built-ins over custom implementations)

YOUR OUTPUT SCHEMA:
{
  "components": [
    {
      "name": "<component_name>",
      "responsibility": "<single responsibility>",
      "design_pattern": "<pattern: why it fits>",
      "data_structures": ["<structure: O(n) for operations>", ...],
      "algorithm": "<algorithm: approach and O(n) analysis>",
      "interfaces": {
        "inputs": ["<param: type>", ...],
        "outputs": "<return: type>"
      }
    }
  ],
  "exception_hierarchy": ["<ExceptionType: when to raise>", ...],
  "validation_strategy": "<how to validate inputs>",
  "dependencies": ["<A depends on B: reason>", ...]
}

ANTI-PATTERNS TO AVOID:
- DON'T suggest "appropriate data structure" (be specific: list, dict, set, deque)
- DON'T recommend patterns without justification (why this pattern solves this problem)
- DON'T ignore standard library (prefer built-ins over custom implementations)
"""

ARCHITECTURE_DESIGNER_PROMPT = BASE_SYSTEM_PROMPT + ARCHITECTURE_DESIGNER_SPECIFIC

# ═══════════════════════════════════════════════════════════════════════
# NODE 4: IMPLEMENTATION PLANNER
# ═══════════════════════════════════════════════════════════════════════

IMPLEMENTATION_PLANNER_SPECIFIC = """
YOUR ROLE: Senior developer creating implementation blueprints.

YOUR TASK: Transform architecture into step-by-step implementation instructions.

PLANNING CHECKLIST:
1. IMPLEMENTATION ORDER: Sequence components based on dependencies
2. DETAILED STEPS: Break into atomic, sequential actions with specific guidance
3. INPUT VALIDATION: Exact validation checks and exceptions
4. ERROR HANDLING: When to raise exceptions, error messages, logging
5. CODING STANDARDS: Naming, documentation, type hints

FEW-SHOT EXAMPLE:

Input: "Binary search architecture"

Output:
{
  "implementation_order": ["binary_search"],
  "components": [
    {
      "name": "binary_search",
      "steps": [
        {
          "step": 1,
          "action": "Define function signature with type hints",
          "code_guidance": "def binary_search(arr: List[int], target: int) -> int:",
          "validation": [
            {
              "check": "isinstance(arr, list)",
              "exception": "TypeError",
              "message": "arr must be a list, got {type(arr)}"
            },
            {
              "check": "isinstance(target, int)",
              "exception": "TypeError",
              "message": "target must be an int, got {type(target)}"
            }
          ],
          "edge_cases": ["Handle empty list: return -1 immediately"]
        },
        {
          "step": 2,
          "action": "Initialize left and right pointers",
          "code_guidance": "left, right = 0, len(arr) - 1",
          "validation": [],
          "edge_cases": ["If arr is empty, right will be -1"]
        },
        {
          "step": 3,
          "action": "Implement main search loop",
          "code_guidance": "while left <= right: calculate mid using left + (right - left) // 2 to avoid overflow",
          "validation": [],
          "edge_cases": ["Loop terminates when left > right (target not found)"]
        },
        {
          "step": 4,
          "action": "Compare mid element with target and adjust pointers",
          "code_guidance": "if arr[mid] == target: return mid; elif arr[mid] < target: left = mid + 1; else: right = mid - 1",
          "validation": [],
          "edge_cases": ["Target at boundaries (first/last element)"]
        },
        {
          "step": 5,
          "action": "Return -1 if target not found",
          "code_guidance": "return -1 after loop exits",
          "validation": [],
          "edge_cases": []
        }
      ],
      "documentation_template": {
        "docstring": "Args: arr (sorted list), target (value to find)\nReturns: index or -1\nRaises: TypeError if inputs invalid",
        "inline_comments": ["Comment complex logic like overflow-safe midpoint calculation"]
      }
    }
  ]
}

YOUR OUTPUT SCHEMA:
{
  "implementation_order": ["<component_name>", ...],
  "components": [
    {
      "name": "<component_name>",
      "steps": [
        {
          "step": <int>,
          "action": "<specific implementation task>",
          "code_guidance": "<how to approach it>",
          "validation": [
            {
              "check": "<exact validation expression>",
              "exception": "<ExceptionType>",
              "message": "<error message with context>"
            }
          ],
          "edge_cases": ["<case: specific handling>", ...]
        }
      ],
      "documentation_template": {
        "docstring": "<required sections: Args, Returns, Raises, Examples>",
        "inline_comments": ["<when to add comments>", ...]
      }
    }
  ]
}

CODE SNIPPET TEMPLATES:
Provide minimal starter code for complex patterns:
```python
# Input validation template
if not isinstance(param, expected_type):
    raise TypeError(f\"Expected {expected_type}, got {type(param)}\")
```

ANTI-PATTERNS TO AVOID:
- DON'T say \"validate input\" (specify: check type, range, format with exact code)
- DON'T skip error messages (always include: context, expected vs actual)
- DON'T write \"handle edge case\" (specify: what edge case, how to handle)
"""

IMPLEMENTATION_PLANNER_PROMPT = BASE_SYSTEM_PROMPT + IMPLEMENTATION_PLANNER_SPECIFIC

# ═══════════════════════════════════════════════════════════════════════
# NODE 5: PLAN QUALITY REVIEWER
# ═══════════════════════════════════════════════════════════════════════

PLAN_QUALITY_REVIEWER_SPECIFIC = """
YOUR ROLE: Senior planning architect reviewing plan quality before handoff to coder agent.

YOUR TASK: Validate that this plan is comprehensive enough for a developer agent to implement production-grade code without questions.

PLAN REVIEW CHECKLIST:
1. COMPLETENESS (Score 0-10): Does the plan address all functional and non-functional requirements?
2. CLARITY: Can a coder agent implement from this plan without ambiguity?
3. ROBUSTNESS: Are error handling strategies well-defined?
4. FEASIBILITY: Are architectural decisions and complexity targets realistic?
5. READINESS: Is this plan ready for handoff to the coder agent?

APPROVAL CRITERIA:
- Score >= 8 AND all critical issues resolved: APPROVED (ready for coder agent)
- Score < 8 OR critical issues remain: NEEDS_REVISION (send back to architecture phase)

YOUR OUTPUT SCHEMA:
{
  "completeness_score": <0-10>,
  "issues": [
    {
      "severity": "<critical|major|minor>",
      "category": "<requirements|architecture|implementation>",
      "description": "<specific problem>",
      "recommendation": "<actionable fix>",
      "location": "<which component/phase>"
    }
  ],
  "improvements": [
    {
      "area": "<what to improve>",
      "suggestion": "<specific improvement>",
      "impact": "<expected benefit>"
    }
  ],
  "approval_status": "<approved|needs_revision>",
  "retry_phase": "<requirements_engineering|architecture_design|implementation_planning|none>",
  "summary": "<2-3 sentence overall assessment>"
}

IMPORTANT: If approval_status is "needs_revision", specify retry_phase:
- "requirements_engineering": Issues with functional/non-functional requirements or constraints
- "architecture_design": Issues with component design, patterns, or data structures
- "implementation_planning": Issues with implementation steps or guidance clarity
- "none": Max iterations reached or approval granted

Remember: You are reviewing the PLAN, not code. The coder agent will generate code later based on YOUR approved plan.
"""

PLAN_QUALITY_REVIEWER_PROMPT = BASE_SYSTEM_PROMPT + PLAN_QUALITY_REVIEWER_SPECIFIC


# ═══════════════════════════════════════════════════════════════════════
# JSON REPAIR UTILITY
# ═══════════════════════════════════════════════════════════════════════

def extract_and_parse_json(response: str, max_attempts: int = 3) -> Dict[Any, Any]:
    """
    Extract and parse JSON from LLM response with automatic repair.
    
    Handles common issues:
    - JSON wrapped in <output> tags (chain-of-thought)
    - Markdown code blocks
    - Trailing commas
    - Missing quotes
    - Extra text before/after JSON
    
    Args:
        response: Raw LLM response
        max_attempts: Number of repair strategies to try
        
    Returns:
        Parsed JSON dict
        
    Raises:
        json.JSONDecodeError: If all repair attempts fail
    """
    attempts = [
        # Attempt 1: Extract from <output> tags
        lambda r: re.search(r'<output>\s*(.+?)\s*</output>', r, re.DOTALL),
        # Attempt 2: Extract from ```json blocks
        lambda r: re.search(r'```(?:json)?\s*(.+?)\s*```', r, re.DOTALL),
        # Attempt 3: Find first { to last }
        lambda r: re.search(r'\{.+\}', r, re.DOTALL),
    ]
    
    for i, extract_func in enumerate(attempts[:max_attempts]):
        try:
            # Try to extract JSON
            match = extract_func(response)
            if match:
                json_str = match.group(1) if i < 2 else match.group(0)
            else:
                json_str = response  # Use raw response
            
            # Clean common issues
            json_str = json_str.strip()
            # Remove trailing commas before } or ]
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            
            # Try to parse
            return json.loads(json_str)
            
        except (json.JSONDecodeError, AttributeError):
            continue
    
    # All attempts failed
    raise json.JSONDecodeError(
        f"Failed to parse JSON after {max_attempts} attempts. Response: {response[:200]}...",
        response,
        0
    )


# ═══════════════════════════════════════════════════════════════════════
# LLM CALL FUNCTION
# ═══════════════════════════════════════════════════════════════════════

def call_llm(
    *,
    user_prompt: str,
    system_prompt: str,
    model: str,
    temperature: float = None,
    max_tokens: int = None,
    node_name: str = "default",
) -> str:
    """
    Core LLM call for all planner nodes.
    Automatically adapts to model size using profiles.
    
    Args:
        user_prompt: The specific task/question for this node (DATA ONLY)
        system_prompt: The node-specific system prompt (INSTRUCTIONS)
        model: Ollama model identifier
        temperature: Sampling temperature (None = use profile default)
        max_tokens: Maximum response tokens (None = use profile default)
        node_name: Node identifier for profile optimization
    
    Returns:
        str: LLM response (typically JSON in <output> tags)
    
    Raises:
        RuntimeError: After all retry attempts exhausted
        ConnectionError: Cannot connect to Ollama
    """
    # Get model-specific profile
    profile = get_model_profile(model)
    
    # Use profile defaults if not specified
    if temperature is None:
        temperature = profile["temperature"].get(node_name, 0.2)
    if max_tokens is None:
        max_tokens = profile["max_tokens"].get(node_name, 1536)
    
    base_delay = 0.5
    max_delay = 8.0
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": temperature,
                    "top_p": 0.9,
                    "top_k": profile["top_k"],  # Use profile value
                    "num_predict": max_tokens,
                    "repeat_penalty": profile["repeat_penalty"],  # Use profile value
                    "repeat_last_n": 256,
                    "stop": ["</output>", "\n\n\n\n", "```"],
                    "num_ctx": 8192,
                },
            )
            
            content = response.get("message", {}).get("content", "")
            if not content or len(content.strip()) < 10:
                raise ValueError(f"Empty response (attempt {attempt + 1})")
            
            return content
        
        except ollama.ResponseError as e:
            last_exception = e
            if attempt == config.max_retries:
                raise RuntimeError(
                    f"LLM API error after {config.max_retries + 1} attempts: {str(e)}"
                ) from e
        
        except ollama.RequestError as e:
            last_exception = e
            if attempt == config.max_retries:
                raise ConnectionError(
                    f"Cannot connect to Ollama. Ensure 'ollama serve' is running: {str(e)}"
                ) from e
        
        except Exception as e:
            last_exception = e
            if attempt == config.max_retries:
                raise RuntimeError(
                    f"Unexpected error after {config.max_retries + 1} attempts: {str(e)}"
                ) from e
        
        if attempt < config.max_retries:
            delay = min(base_delay * (2 ** attempt), max_delay)
            print(f"⏳ Retry {attempt + 1} in {delay:.1f}s...")
            time.sleep(delay)
    
    raise RuntimeError(f"Failed after {config.max_retries + 1} attempts: {str(last_exception)}")

