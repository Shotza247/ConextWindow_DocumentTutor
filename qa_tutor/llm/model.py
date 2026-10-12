"""Chat model via LiteLLM: Hugging Face first, automatic fallback to OpenAI.

SDK mode  (default): an in-process LiteLLM Router. HF is tried first; if it fails
                     (402 credits depleted, rate limit, outage...) the same call is
                     re-sent to the fallback model.
Proxy mode (later):  set LITELLM_API_BASE to your Render proxy. The proxy owns the keys
                     and the fallback rules (see litellm_config.yaml).
"""
from __future__ import annotations

import os

from qa_tutor.config import Settings

HF_KEY = "HUGGINGFACEHUB_API_TOKEN"
OPENAI_KEY = "OPENAI_API_KEY"
PROXY_KEY = "LITELLM_API_KEY"
HF_BASE = "https://router.huggingface.co/v1"

PRIMARY, FALLBACK = "tutor-primary", "tutor-fallback"
KEY_FIELDS = {"Hugging Face token": HF_KEY, "OpenAI API key": OPENAI_KEY}


def _load_env() -> None:
    from dotenv import load_dotenv

    load_dotenv()


def using_proxy() -> bool:
    _load_env()
    return bool(os.getenv("LITELLM_API_BASE"))


def has_credentials() -> bool:
    _load_env()
    if using_proxy():
        return bool(os.getenv(PROXY_KEY))
    return bool(os.getenv(HF_KEY) or os.getenv(OPENAI_KEY))


def build_router(settings: Settings):
    """Return (router, first_deployment_name) for whichever keys are available."""
    from litellm import Router

    hf, oai = os.getenv(HF_KEY), os.getenv(OPENAI_KEY)
    base = {"timeout": settings.request_timeout}
    models = []
    if hf:
        models.append({
            "model_name": PRIMARY,
            "litellm_params": {
                "model": f"openai/{settings.model}",  # HF's router speaks the OpenAI protocol
                "api_base": HF_BASE, "api_key": hf, **base,
            },
        })
    if oai:
        models.append({
            "model_name": FALLBACK,
            "litellm_params": {"model": settings.fallback_model, "api_key": oai, **base},
        })
    first = models[0]["model_name"]
    fallbacks = [{PRIMARY: [FALLBACK]}] if hf and oai else []
    router = Router(model_list=models, fallbacks=fallbacks, num_retries=settings.max_retries)
    return router, first


def build_chat_model(settings: Settings):
    _load_env()
    if not has_credentials():
        raise RuntimeError(
            f"Add {HF_KEY} and/or {OPENAI_KEY} to your .env (or LITELLM_API_BASE + {PROXY_KEY} for a proxy)."
        )

    if using_proxy():
        from langchain_litellm import ChatLiteLLM

        return ChatLiteLLM(
            model=f"litellm_proxy/{os.getenv('QA_TUTOR_PROXY_MODEL', PRIMARY)}",
            api_base=os.getenv("LITELLM_API_BASE"),
            api_key=os.getenv(PROXY_KEY),
            temperature=settings.temperature,
            max_tokens=settings.max_new_tokens,
            request_timeout=settings.request_timeout,
        )

    from langchain_litellm import ChatLiteLLMRouter

    router, first = build_router(settings)
    return ChatLiteLLMRouter(
        router=router,
        model_name=first,
        temperature=settings.temperature,
        max_tokens=settings.max_new_tokens,
    ) 