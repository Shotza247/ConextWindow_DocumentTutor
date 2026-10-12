"""The 'state': the data that flows between nodes."""
from __future__ import annotations

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

Mode = Literal["prep", "ask", "walkthrough"]


class TutorState(TypedDict, total=False):
    # what you pass in
    sources: list[str]
    mode: Mode
    question: str
    # what the nodes produce (kept as plain dicts so they are easy to save)
    cache_key: str
    document_markdown: str
    analysis: dict
    sme_brief: dict
    # conversation
    messages: Annotated[list[AnyMessage], add_messages]
    current_step: int
    answer: str
