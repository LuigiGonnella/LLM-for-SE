# Single Agent Pipeline Architecture

## Overview

This document describes the proposed refactoring of the single-agent pipeline to separate quality assessment from the refinement loop, enabling better code quality improvements.

---

## Current Pipeline (Without Separate Quality Node)

```
analysis → planning → generation → review → refinement → END
                          ↓
                    (code produced)
```

**Issues with current approach:**
- Refinement node calls review internally
- Quality metrics are computed but not passed to the refiner
- Refiner has no explicit knowledge of quality targets
- No clear separation between LLM roles and static analysis

---

## Proposed Pipeline (WITH Separate Quality Node)

```
                    ┌─────────────────┐
                    │  generation     │
                    │  (code output)  │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                ↓                         ↓
         ┌─────────────┐         ┌──────────────┐
         │quality_node │         │  review_node │
         │(Radon static│         │(LLM review)  │
         │ analysis)   │         │              │
         └────────┬────┘         └──────┬───────┘
                  │                     │
                  └────────────┬────────┘
                               ↓
                        ┌──────────────────┐
                        │ refinement_node  │
                        │ (takes quality + │
                        │  review, loops)  │
                        └────────┬─────────┘
                                 ↓
                               END
```

**New flow:**
1. **Generation** produces code
2. **Quality node** (static analysis) runs Radon metrics in parallel with review
3. **Review node** (LLM) evaluates code with quality context
4. **Refinement node** uses both quality metrics and review verdict to improve code

---

## Node Implementations

### 1. Analysis Node
```python
def analysis_node(state: AgentState) -> AgentState:
    """Analyze the task to understand requirements."""
    print(">> ANALYSIS NODE")
    state["analysis"] = analyze_task(
        signature=state["signature"],
        docstring=state["docstring"],
        examples=state.get("examples"),
        model=state["model"],
    )
    return state
```
**Purpose:** Deep task understanding  
**Output:** Analysis of requirements, constraints, edge cases

---

### 2. Planning Node
```python
def planning_node(state: AgentState) -> AgentState:
    """Create a step-by-step implementation plan."""
    print(">> PLANNING NODE")
    state["plan"] = plan_solution(
        analysis=state["analysis"],
        model=state["model"],
    )
    return state
```
**Purpose:** Design the solution approach  
**Output:** High-level plan without code

---

### 3. Generation Node
```python
def generation_node(state: AgentState) -> AgentState:
    """Generate code from the plan."""
    print(">> GENERATION NODE")
    raw_code = generate_code(
        signature=state["signature"],
        plan=state["plan"],
        model=state["model"],
    )
    state["code"] = extract_python_code(raw_code)
    return state
```
**Purpose:** Implement the plan as working Python code  
**Output:** Python function code

---

### 4. Quality Node (NEW)
```python
def quality_node(state: AgentState) -> AgentState:
    """Compute code quality metrics using static analysis."""
    print(">> QUALITY NODE")
    
    # Static analysis - no LLM needed
    metrics = compute_quality_metrics(state["code"])
    state["quality_metrics"] = metrics
    
    # Format for human readability and LLM consumption
    state["quality_report"] = format_metrics_report(metrics)
    
    print(state["quality_report"])
    return state
```
**Purpose:** Assess code quality independently (no LLM)  
**Input:** Generated code  
**Output:** Quality metrics (MI, CC, LOC, Halstead)  
**Why separate:**
- Removes coupling between review and analysis
- Quality assessment is deterministic (Radon library)
- Can be run in parallel with review
- Reduces LLM calls

---

### 5. Review Node (Updated)
```python
def review_node(state: AgentState) -> AgentState:
    """Review code for correctness and quality."""
    print(">> REVIEW NODE")
    
    # Execute code and capture results
    exec_result = execute_code(state["code"])
    state["exec_result"] = exec_result
    
    # Review with full context: execution + quality metrics
    state["review"] = review_code(
        code=state["code"],
        model=state["model"],
        exec_result=exec_result,
        quality_metrics=state["quality_report"],  # ← from quality_node
    )
    
    print(f"Exec results: {exec_result}")
    print(f'Reviewer result: {state["review"].splitlines()[-1]}')
    return state
```
**Purpose:** LLM-based code review  
**Input:** Code, execution results, quality metrics  
**Output:** Detailed review with verdict  
**Benefit:** Reviewer has full context including quality scores

---

### 6. Refinement Node (Updated)
```python
def refinement_node(state: AgentState) -> AgentState:
    """Iteratively refine code for correctness and quality."""
    print(">> REFINEMENT NODE")
    
    max_refinements = 3
    refinement_count = state.get("refinement_count", 0)
    
    while refinement_count < max_refinements:
        
        # EARLY EXIT: Code already correct
        if (
            "review" in state
            and "Code is correct" in state["review"]
            and refinement_count >= 1
        ):
            print("Code already correct. Skipping refinement.")
            return state
        
        # MAX ITERATIONS reached
        if refinement_count >= max_refinements:
            print("Maximum refinements reached. Ending refinement.")
            return state
        
        print(f"Starting refinement {refinement_count + 1}/{max_refinements}\n")
        
        # Refiner receives quality metrics alongside review
        raw_code = refine_code(
            code=state["code"],
            review=state["review"],
            quality_metrics=state["quality_report"],  # ← explicit quality data
            model=state["model"],
        )
        
        refined_code = extract_python_code(raw_code)
        
        # Execute refined code
        exec_result = execute_code(refined_code)
        
        # Update state with refined code
        state["code"] = refined_code
        state["exec_result"] = exec_result
        state["refinement_count"] = refinement_count + 1
        
        # RE-COMPUTE quality for refined code
        metrics = compute_quality_metrics(refined_code)
        state["quality_metrics"] = metrics
        state["quality_report"] = format_metrics_report(metrics)
        
        print(state["quality_report"])
        
        # RE-RUN review with updated quality metrics
        review = review_code(
            code=refined_code,
            exec_result=exec_result,
            model=state["model"],
            quality_metrics=state["quality_report"],  # ← updated metrics
        )
        state["review"] = review
        
        # Check if refinement successful
        if "Code is correct" in review:
            print("Refinement successful: code is correct.")
            return state
        else:
            print("Refinement incomplete: issues remain.")
            refinement_count += 1
    
    return state
```
**Purpose:** Iteratively improve code until correct or max iterations reached  
**Input:** Code, review, quality metrics  
**Output:** Improved code with tracked refinement count  
**Key improvements:**
- Refiner explicitly receives quality metrics
- Quality is recomputed after each refinement
- Review verdict updated with new quality data
- Clear loop with max iterations

---

## Graph Construction

```python
def build_single_agent_graph():
    """Build the single-agent pipeline as a LangGraph."""
    graph = StateGraph(AgentState)
    
    # Add all nodes
    graph.add_node("analysis", analysis_node)
    graph.add_node("planning", planning_node)
    graph.add_node("generation", generation_node)
    graph.add_node("quality", quality_node)      # NEW
    graph.add_node("review", review_node)
    graph.add_node("refinement", refinement_node)
    
    # Define edges
    graph.add_edge(START, "analysis")
    graph.add_edge("analysis", "planning")
    graph.add_edge("planning", "generation")
    graph.add_edge("generation", "quality")      # NEW: quality after generation
    graph.add_edge("quality", "review")          # NEW: quality feeds review
    graph.add_edge("review", "refinement")
    graph.add_edge("refinement", END)
    
    return graph.compile()
```

---

## Key Changes Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Quality Computation** | Hidden in refinement loop | Explicit `quality_node` |
| **Quality Visibility** | Only in review verdict | Quantified metrics passed explicitly |
| **Review Context** | Code + execution | Code + execution + quality metrics |
| **Refiner Visibility** | No quality data | Full quality metrics + review |
| **Separation of Concerns** | Mixed (LLM + static analysis) | Clean (each agent has one role) |
| **Testability** | Hard to test nodes independently | Easy to test each node |
| **Quality Tracking** | No metrics across iterations | Can track MI/CC improvements |

---

## Agent Responsibilities

### Analysis Agent
- **Input:** Task signature, docstring, examples
- **Role:** Understand the problem
- **Output:** Detailed analysis of requirements and constraints
- **Scope:** No implementation decisions

### Planning Agent
- **Input:** Analysis
- **Role:** Design the solution
- **Output:** Step-by-step implementation plan
- **Scope:** No code, only logical flow

### Coding Agent (Generation)
- **Input:** Signature, plan
- **Role:** Implement the plan
- **Output:** Working Python code
- **Scope:** Pure code generation

### Quality Analyzer
- **Input:** Generated code
- **Role:** Measure code quality objectively
- **Output:** Metrics (MI, CC, LOC, Halstead)
- **Scope:** Static analysis only (no LLM)

### Review Agent
- **Input:** Code, execution results, quality metrics
- **Role:** Evaluate correctness and identify issues
- **Output:** Detailed review with verdict
- **Scope:** Critical assessment based on full context

### Refinement Agent
- **Input:** Code, review verdict, quality metrics
- **Role:** Improve code iteratively
- **Output:** Enhanced code with better correctness and quality
- **Scope:** Fix issues, improve quality, maintain correctness

---

## State Flow

```python
AgentState = TypedDict(
    "AgentState",
    {
        # Task definition
        "task_id": str,
        "signature": str,
        "docstring": str,
        "examples": Optional[str],
        "model": str,
        
        # Agent outputs
        "analysis": Optional[str],          # from analysis_node
        "plan": Optional[str],              # from planning_node
        "code": Optional[str],              # from generation_node (updated in refinement)
        
        # Quality assessment (NEW)
        "quality_metrics": Optional[dict],  # from quality_node
        "quality_report": Optional[str],    # formatted quality_metrics
        
        # Review and execution
        "review": Optional[str],            # from review_node (updated in refinement)
        "exec_result": Optional[dict],      # from execution
        
        # Refinement tracking
        "refinement_count": int,            # number of refinement iterations
    },
)
```

---

## Benefits of This Architecture

1. **Clear Separation of Concerns**
   - Each agent has a single, well-defined responsibility
   - Easy to understand the pipeline flow

2. **Better Quality Feedback Loop**
   - Refiner explicitly sees quality metrics
   - Can target specific improvements (reduce CC, improve MI)

3. **Improved Testability**
   - Each node can be tested independently
   - Easy to mock quality metrics or review verdicts

4. **Cost Efficiency**
   - Quality metrics use free static analysis (Radon)
   - No extra LLM calls for quality assessment

5. **Transparency**
   - Quality improvements are tracked and visible
   - Easy to debug refinement iterations

6. **Scalability**
   - Can add new agents (e.g., StyleChecker) without breaking existing flow
   - Can adjust refinement strategy based on quality or correctness

---

## Example Execution Flow

```
Input: Task to solve

1. analysis_node
   → Output: "The function must sort a list in O(n) time..."
   → State updated: analysis = "..."

2. planning_node
   → Input: analysis
   → Output: "Step 1: Use counting sort... Step 2: Handle edge cases..."
   → State updated: plan = "..."

3. generation_node
   → Input: signature, plan
   → Output: "def sort_fast(arr): ..."
   → State updated: code = "def sort_fast(arr): ..."

4. quality_node (NEW)
   → Input: code
   → Output: MI=75, CC=3, LOC=12
   → State updated: quality_metrics = {...}, quality_report = "=== Code Quality ==="

5. review_node
   → Input: code, quality_report
   → Executes code, generates review with quality context
   → Output: "Code is correct. MI=75 is good, CC=3 is simple."
   → State updated: review = "...", exec_result = {...}

6. refinement_node (if needed)
   → Input: code, review, quality_report
   → If "Code is correct" in review: return state
   → Else: refine_code(...) with quality context
   → Re-execute and re-review
   → Repeat until correct or max iterations

Output: Final code with quality metrics and refinement history
```

---

## Migration Notes

To implement this:

1. **Update `src/core/agent.py`:**
   - Modify `refine_code()` to accept `quality_metrics` parameter

2. **Update `src/core/pipeline.py`:**
   - Add `quality_node()` function
   - Update `review_node()` to use quality metrics
   - Update `refinement_node()` to pass quality to refiner
   - Update graph construction with new node and edges

3. **No changes needed to:**
   - `src/evaluation/quality.py` (already works)
   - `src/core/state.py` (AgentState already has quality fields)
   - `src/tools/executor.py`
   - `src/utils/code_parser.py`

---

## Conclusion

This architecture cleanly separates concerns while improving the refinement process through explicit quality feedback. The refiner can now make informed decisions about code quality improvements alongside correctness fixes.
