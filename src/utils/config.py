from dataclasses import dataclass
from enum import Enum


class Model(str, Enum):
    """Supported LLM models for code generation."""

    QWEN_2_5_CODER_7B = "qwen2.5-coder:7b-instruct"
    DEEPSEEK_CODER_V2_16B = "deepseek-coder-v2:16b"
    DEEPSEEK_CODER_6_7B = "deepseek-coder:6.7b"
    CODELLAMA_7B = "codellama:7b-instruct"
    MISTRAL_7B = "mistral:7b-instruct"


@dataclass(frozen=True)
class Config:
    """Configuration for the single-agent code generation system."""

    # Model settings
    # NOTE: 6.7B models may struggle with complex tasks. Consider using:
    # - deepseek-coder-v2:16b for better quality (requires more RAM)
    # - qwen2.5-coder:14b for good balance
    base_model: str = Model.QWEN_2_5_CODER_7B.value
    planner_model: str = Model.MISTRAL_7B.value
    coder_model: str = Model.DEEPSEEK_CODER_6_7B.value
    critic_model: str = Model.DEEPSEEK_CODER_6_7B.value
    temperature: float = 0.0
    max_retries: int = 2  # 2 retries = 3 total attempts (initial + 2 refinements)

    # Paths
    data_dir: str = "./data"


# Default config instance
config = Config()
