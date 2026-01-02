from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Configuration for the single-agent code generation system."""

    # Model settings
    model_name: str = "qwen2.5-coder:7b-instruct"
    temperature: float = 0.0
    max_retries: int = 2

    # Paths
    data_dir: str = "./data"


# Default config instance
config = Config()
