"""Node 1: read all sources and combine them into one text document."""
from __future__ import annotations

from qa_tutor.config import Settings
from qa_tutor.ingestion.loader import load_sources, sources_key


def make_load_document_node(settings: Settings):
    def load_document(state: dict) -> dict:
        sources = state["sources"]
        return {
            "cache_key": sources_key(sources),
            "document_markdown": load_sources(sources, settings),
        }

    return load_document
