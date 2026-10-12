from qa_tutor.config import Settings
from qa_tutor.tutor import Tutor
from tests.helpers import fake_llm


def test_load_ask_and_walkthrough(tmp_path):
    doc = tmp_path / "notes.txt"
    doc.write_text("Caching stores copies of data closer to the user.", encoding="utf-8")
    settings = Settings(cache_dir=tmp_path / "cache")

    tutor = Tutor(settings, llm=fake_llm("Caching keeps copies nearby.", "Lesson 1.", "Lesson 2."))
    analysis = tutor.load([str(doc)])
    assert analysis["title"] == "Caching 101"
    assert tutor.total_steps == 2

    assert tutor.ask("What is caching?") == "Caching keeps copies nearby."
    assert tutor.start_walkthrough() == "Lesson 1." and tutor.step == 1
    assert tutor.next_step() == "Lesson 2." and tutor.step == 2
    assert "completed" in tutor.next_step()

    # analysis + SME brief were saved, so a second run costs no AI calls for them
    assert len(list((tmp_path / "cache").glob("*.json"))) == 2
