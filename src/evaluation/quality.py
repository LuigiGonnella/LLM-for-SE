"""
Code quality metrics using Radon for static analysis.

Metrics computed:
- Maintainability Index (MI): 0-100 scale, higher is better
- Cyclomatic Complexity (CC): lower is better, measures decision points
- Lines of Code (LOC): raw and logical lines
- Halstead Metrics: volume, difficulty, effort (cognitive complexity)
"""

import ast
from radon.metrics import mi_visit, h_visit
from radon.complexity import cc_visit
from radon.raw import analyze


def compute_quality_metrics(code: str) -> dict:
    """
    Compute comprehensive code quality metrics.

    Args:
        code: Python source code string

    Returns:
        Dictionary with all computed metrics and interpretations
    """
    metrics = {
        "maintainability_index": None,
        "cyclomatic_complexity": None,
        "lines_of_code": None,
        "logical_lines": None,
        "halstead_volume": None,
        "halstead_difficulty": None,
        "halstead_effort": None,
        "num_functions": None,
        "avg_complexity_per_function": None,
        "parse_error": None,
    }

    try:
        # Validate syntax first
        ast.parse(code)
    except SyntaxError as e:
        metrics["parse_error"] = str(e)
        return metrics

    # Maintainability Index (0-100, higher = more maintainable)
    try:
        metrics["maintainability_index"] = round(mi_visit(code, True), 2)
    except Exception:
        pass

    # Cyclomatic Complexity per function
    try:
        cc_results = cc_visit(code)
        if cc_results:
            complexities = [block.complexity for block in cc_results]
            metrics["cyclomatic_complexity"] = sum(complexities)
            metrics["num_functions"] = len(cc_results)
            metrics["avg_complexity_per_function"] = round(
                sum(complexities) / len(complexities), 2
            )
        else:
            metrics["cyclomatic_complexity"] = 1
            metrics["num_functions"] = 0
            metrics["avg_complexity_per_function"] = 0
    except Exception:
        pass

    # Raw metrics (LOC, SLOC, comments, etc.)
    try:
        raw = analyze(code)
        metrics["lines_of_code"] = raw.loc
        metrics["logical_lines"] = raw.sloc
    except Exception:
        pass

    # Halstead metrics (cognitive complexity)
    try:
        h_results = h_visit(code)
        if h_results and hasattr(h_results, "total"):
            total = h_results.total
            metrics["halstead_volume"] = (
                round(total.volume, 2) if total.volume else None
            )
            metrics["halstead_difficulty"] = (
                round(total.difficulty, 2) if total.difficulty else None
            )
            metrics["halstead_effort"] = (
                round(total.effort, 2) if total.effort else None
            )
    except Exception:
        pass

    return metrics


def interpret_maintainability(mi_score: float) -> str:
    """Interpret Maintainability Index score."""
    if mi_score is None:
        return "Unknown"
    if mi_score >= 80:
        return "Excellent"
    if mi_score >= 60:
        return "Good"
    if mi_score >= 40:
        return "Moderate"
    if mi_score >= 20:
        return "Poor"
    return "Very Poor"


def interpret_complexity(cc_score: int) -> str:
    """Interpret Cyclomatic Complexity score."""
    if cc_score is None:
        return "Unknown"
    if cc_score <= 5:
        return "Simple"
    if cc_score <= 10:
        return "Moderate"
    if cc_score <= 20:
        return "Complex"
    return "Very Complex"


def format_metrics_report(metrics: dict) -> str:
    """Format metrics as a human-readable report."""
    if metrics.get("parse_error"):
        return f"Code Quality: PARSE ERROR - {metrics['parse_error']}"

    mi = metrics.get("maintainability_index")
    cc = metrics.get("cyclomatic_complexity")

    lines = [
        "Code Quality Metrics:",
        f"  Maintainability Index : {mi} ({interpret_maintainability(mi)})",
        f"  Cyclomatic Complexity : {cc} ({interpret_complexity(cc)})",
        f"  Lines of Code (LOC)   : {metrics.get('lines_of_code')}",
        f"  Logical Lines (SLOC)  : {metrics.get('logical_lines')}",
        f"  Number of Functions   : {metrics.get('num_functions')}",
    ]

    if metrics.get("halstead_volume"):
        lines.extend(
            [
                f"  Halstead Volume       : {metrics.get('halstead_volume')}",
                f"  Halstead Difficulty   : {metrics.get('halstead_difficulty')}",
                f"  Halstead Effort       : {metrics.get('halstead_effort')}",
            ]
        )

    return "\n".join(lines)
