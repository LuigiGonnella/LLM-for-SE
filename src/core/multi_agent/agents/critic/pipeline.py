"""
Multi-Node Critic Agent Pipeline

Architecture:
- Input Validator: Validates inputs
- Correctness Analyzer: Checks logic and bugs
- Quality Reviewer: Checks code quality
- Feedback Synthesizer: Combines into final critique
"""

from langgraph.graph import StateGraph, START, END
from src.core.multi_agent.agents.critic.state import CriticAgentState
from src.core.multi_agent.agents.critic.nodes.input_validator import (
    input_validator_node,
)
from src.core.multi_agent.agents.critic.nodes.correctness_analyzer import (
    correctness_analyzer_node,
)
from src.core.multi_agent.agents.critic.nodes.quality_reviewer import (
    quality_reviewer_node,
)
from src.core.multi_agent.agents.critic.nodes.feedback_synthesizer import (
    feedback_synthesizer_node,
)


def build_critic_graph():
    """
    Build the multi-node critic agent graph.
    """
    graph = StateGraph(CriticAgentState)

    # Add nodes
    graph.add_node("input_validator", input_validator_node)
    graph.add_node("correctness_analyzer", correctness_analyzer_node)
    graph.add_node("quality_reviewer", quality_reviewer_node)
    graph.add_node("feedback_synthesizer", feedback_synthesizer_node)

    # Define flow
    graph.add_edge(START, "input_validator")
    graph.add_edge("input_validator", "correctness_analyzer")
    graph.add_edge("correctness_analyzer", "quality_reviewer")
    graph.add_edge("quality_reviewer", "feedback_synthesizer")
    graph.add_edge("feedback_synthesizer", END)

    return graph.compile()
