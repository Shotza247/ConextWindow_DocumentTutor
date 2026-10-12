"""Settings used across the project. Change defaults here, or pass your own Settings(...)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Some Windows setups fail on Hugging Face's faster download path, so turn it off.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = os.getenv("QA_TUTOR_MODEL", "deepseek-ai/DeepSeek-R1-0528")  # Hugging Face repo id (primary)
DEFAULT_FALLBACK_MODEL = os.getenv("QA_TUTOR_FALLBACK_MODEL", "openai/gpt-5.1")  # used when HF fails (e.g. 402 credits)
DEFAULT_CACHE_DIR = Path(os.getenv("QA_TUTOR_CACHE_DIR", PROJECT_ROOT / "cache"))


@dataclass(frozen=True)
class Settings:
    model: str = DEFAULT_MODEL                    # primary: Hugging Face repo id
    fallback_model: str = DEFAULT_FALLBACK_MODEL  # backup: any LiteLLM model string
    cache_dir: Path = DEFAULT_CACHE_DIR
    use_docling: bool = False       # True = layout-aware PDF reading (needs requirements-docling.txt)
    refresh_cache: bool = False     # True = ignore saved results and redo everything
    max_new_tokens: int = 8192      # longest answer the model may write
    request_timeout: float = 600    # seconds to wait for the model before giving up
    max_retries: int = 2            # LiteLLM retries on rate limits / transient errors
    temperature: float = 0.1        # 0 = very predictable, higher = more creative
    history_window: int = 8         # how many past chat messages the tutor remembers
    max_document_chars: int = 80_000  # the whole text is sent to the model, so keep a cap