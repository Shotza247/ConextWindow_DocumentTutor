"""Node 2: understand the document and plan a lesson outline."""
from __future__ import annotations

from qa_tutor.cache import load_cached, save_cached
from qa_tutor.config import Settings
from qa_tutor.llm.structured import run_structured
from qa_tutor.prompts.analysis import ANALYSIS_PROMPT
from qa_tutor.schemas import DocumentAnalysis


def make_analyze_node(llm, settings: Settings):
    def analyze(state: dict) -> dict:
        path = settings.cache_dir / f"{state['cache_key']}.analysis.json"
        if not settings.refresh_cache:
            cached = load_cached(path, DocumentAnalysis)
            if cached:
                return {"analysis": cached}

        result = run_structured(
            llm, ANALYSIS_PROMPT, DocumentAnalysis, {"document": state["document_markdown"]}
        )
        data = result.model_dump()
        save_cached(path, data)
        return {"analysis": data}

    return analyze
