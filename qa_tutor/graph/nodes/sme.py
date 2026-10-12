"""Node 3: build an 'expert brief' (glossary, facts, misconceptions) so answers are expert-level."""
from __future__ import annotations

import json

from qa_tutor.cache import load_cached, save_cached
from qa_tutor.config import Settings
from qa_tutor.llm.structured import run_structured
from qa_tutor.prompts.sme import SME_PROMPT
from qa_tutor.schemas import SMEBrief


def make_sme_node(llm, settings: Settings):
    """'Trains' the agent in-context: builds an expert brief from the document."""

    def sme_training(state: dict) -> dict:
        path = settings.cache_dir / f"{state['cache_key']}.sme.json"
        if not settings.refresh_cache:
            cached = load_cached(path, SMEBrief)
            if cached:
                return {"sme_brief": cached}

        result = run_structured(
            llm,
            SME_PROMPT,
            SMEBrief,
            {
                "document": state["document_markdown"],
                "analysis": json.dumps(state["analysis"], indent=2),
            },
        )
        data = result.model_dump()
        save_cached(path, data)
        return {"sme_brief": data}

    return sme_training
