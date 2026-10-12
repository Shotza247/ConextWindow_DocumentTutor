"""Runs the real Streamlit app headlessly with a fake LLM."""
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from tests.helpers import fake_llm  # noqa: E402

APP = Path(__file__).resolve().parent.parent / "app.py"


def test_process_then_chat_and_walkthrough(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TUTOR_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(
        "qa_tutor.tutor.build_chat_model",
        lambda settings: fake_llm("Caching keeps copies nearby.", "Lesson one."),
    )
    doc = tmp_path / "notes.txt"
    doc.write_text("Caching stores copies of data closer to the user.", encoding="utf-8")

    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert "Process documents" in [b.label for b in at.button]

    at.text_area[0].set_value(str(doc)).run()
    next(b for b in at.button if b.label == "Process documents").click().run()
    assert not at.error, [e.value for e in at.error]
    assert at.session_state["tutor"] is not None

    at.chat_input[0].set_value("What is caching?").run()
    assert at.chat_message[-1].markdown[0].value == "Caching keeps copies nearby."

    next(b for b in at.button if "Start guided" in b.label).click().run()
    assert "Step 1 of 2" in at.session_state["chat"][-1]["content"]
