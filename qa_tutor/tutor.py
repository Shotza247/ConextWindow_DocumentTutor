"""The Tutor class: the ONE thing the terminal app and the Streamlit app both use.

    tutor = Tutor()
    tutor.load(["notes.pdf", "https://example.com/article"])
    print(tutor.ask("What is caching?"))
    print(tutor.start_walkthrough())
    print(tutor.next_step())
"""
from __future__ import annotations

from uuid import uuid4

from qa_tutor.config import Settings
from qa_tutor.graph.builder import build_graph
from qa_tutor.llm.model import build_chat_model


class Tutor:
    def __init__(self, settings: Settings | None = None, llm=None):
        """Pass `llm` to use your own chat model (handy for tests)."""
        self.settings = settings or Settings()
        self.llm = llm or build_chat_model(self.settings)
        self._app = build_graph(self.llm, self.settings)
        self._config = {"configurable": {"thread_id": uuid4().hex}}
        self.analysis: dict = {}
        self.step = 0  # how many walkthrough steps have been taught

    @property
    def total_steps(self) -> int:
        return len(self.analysis.get("lesson_outline", []))

    def load(self, sources: list[str]) -> dict:
        """Read the sources, analyse them, and build the expert brief. Returns the analysis."""
        state = self._app.invoke(
            {"sources": sources, "mode": "prep", "current_step": 0}, self._config
        )
        self.analysis = state["analysis"]
        self.step = 0
        return self.analysis

    def ask(self, question: str) -> str:
        result = self._app.invoke({"mode": "ask", "question": question}, self._config)
        return result["answer"]

    def start_walkthrough(self) -> str:
        result = self._app.invoke({"mode": "walkthrough", "current_step": 0}, self._config)
        self.step = result["current_step"]
        return result["answer"]

    def next_step(self) -> str:
        result = self._app.invoke({"mode": "walkthrough"}, self._config)
        self.step = result["current_step"]
        return result["answer"]