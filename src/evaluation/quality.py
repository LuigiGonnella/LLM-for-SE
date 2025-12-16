from radon.metrics import mi_visit
from radon.complexity import cc_visit


def compute_quality_metrics(code: str) -> dict:
    return {
        "maintainability": mi_visit(code, True),
        "cyclomatic_complexity": len(cc_visit(code)),
    }
