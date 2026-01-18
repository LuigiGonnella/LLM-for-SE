from dataclasses import dataclass
from enum import Enum


class Model(str, Enum):
    """Supported LLM models for code generation."""

    QWEN_2_5_CODER_7B = "qwen2.5-coder:7b-instruct"
    DEEPSEEK_CODER_V2_16B = "deepseek-coder-v2:16b"
    CODELLAMA_7B = "codellama:7b-instruct"
    MISTRAL_7B = "mistral"


@dataclass(frozen=True)
class Config:
    """Configuration for the single-agent code generation system."""

    # Model settings
    model_name: str = Model.QWEN_2_5_CODER_7B.value
    temperature: float = 0.0
    max_retries: int = 2

    # Paths
    data_dir: str = "./data"


# Default config instance
config = Config()
