"""Fake LLM replies so tests run without a network or a token."""
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from qa_tutor.schemas import DocumentAnalysis, LessonStep, SMEBrief


def fake_llm(*answers: str):
    steps = [
        LessonStep(title=f"Step {i}", objective="o", key_points=["k"], check_question="q?")
        for i in (1, 2)
    ]
    analysis = DocumentAnalysis(
        title="Caching 101", summary="About caching.", audience="Beginners",
        difficulty="beginner", topics=[], prerequisites=[], lesson_outline=steps,
    ).model_dump_json()
    sme = SMEBrief(
        glossary=[], key_facts=["f"], concept_links=[], misconceptions=[], practice_questions=[]
    ).model_dump_json()
    replies = ["<think>hmm</think>" + analysis, sme, *answers] + ["unused"] * 5
    return GenericFakeChatModel(messages=iter(AIMessage(content=r) for r in replies))
