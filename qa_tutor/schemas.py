"""The shapes of the data the AI must return (analysis and expert brief)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Topic(BaseModel):
    name: str
    summary: str


class LessonStep(BaseModel):
    title: str
    objective: str = Field(description="What the learner can do after this step.")
    key_points: list[str]
    check_question: str = Field(description="One question to test understanding.")


class DocumentAnalysis(BaseModel):
    title: str
    summary: str
    audience: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    topics: list[Topic]
    prerequisites: list[str]
    lesson_outline: list[LessonStep] = Field(
        description="Ordered teaching steps, from foundations to advanced ideas."
    )


class GlossaryTerm(BaseModel):
    term: str
    definition: str


class Misconception(BaseModel):
    misconception: str
    correction: str


class PracticeQA(BaseModel):
    question: str
    answer: str


class SMEBrief(BaseModel):
    glossary: list[GlossaryTerm]
    key_facts: list[str]
    concept_links: list[str] = Field(
        description="Sentences explaining how the main concepts relate to each other."
    )
    misconceptions: list[Misconception]
    practice_questions: list[PracticeQA]
