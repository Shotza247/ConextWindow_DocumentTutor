# 🎓 Document Tutor

Upload documents or paste links, then chat with an AI that has studied them. It can also walk you through the material step by step.

## Quick start (Windows PowerShell)

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env        # open .env and paste your Hugging Face token
streamlit run app.py          # chat UI in your browser
```

Prefer the terminal? `python main.py --source my.pdf https://example.com/article`

## What happens when you click "Process documents"

```
load_document  ->  analyze  ->  sme_training  ->  (ready)  ->  tutor
 read + combine    title,        glossary, facts,              answers questions
 all sources       summary,      misconceptions,               or teaches the
                   lesson plan   practice Q&A                  lesson one step at a time
```

Analysis and the expert brief are saved in `cache/`, so re-opening the same documents is instant and free. Use `--refresh-cache` (terminal) to redo them.

## Where things live

| Path | What it does |
|---|---|
| `app.py` | Streamlit UI (sidebar + chat) |
| `main.py` | Terminal version |
| `qa_tutor/tutor.py` | **`Tutor` class: the one thing both apps use** |
| `qa_tutor/config.py` | Settings: model, token limit, cache folder |
| `qa_tutor/ingestion/` | Reading PDFs, web pages, text files |
| `qa_tutor/llm/model.py` | Creates the AI model (change provider here) |
| `qa_tutor/prompts/` | The instructions given to the AI, one file per node |
| `qa_tutor/graph/` | The LangGraph pipeline: `state.py`, `builder.py`, `nodes/` |
| `qa_tutor/schemas.py` | The shape of the analysis and expert brief |
| `tests/` | Run with `python -m pytest` (no token needed) |

## Reusing it in your own code

```python
from qa_tutor.tutor import Tutor

tutor = Tutor()
tutor.load(["notes.pdf", "https://example.com/article"])
print(tutor.ask("What is caching?"))
print(tutor.start_walkthrough())
```

## Adding a new node

1. Write the prompt in `prompts/my_node.py`.
2. Write `graph/nodes/my_node.py` with a `make_my_node(llm, settings)` function.
3. In `graph/builder.py`: `graph.add_node(...)` and connect it with `graph.add_edge(...)`.

## Good to know

- Supported: PDF, TXT, MD files and web links (PDF links or normal pages). Scanned PDFs (images only) are not supported without OCR.
- All text is sent to the model each time, so it is capped at 80,000 characters (`max_document_chars` in `config.py`). Very large material needs chunking.
- Pages that need JavaScript or a login can't be read. Save them as PDF and upload.
- Optional better PDF layout reading: `pip install -r requirements-docling.txt`, then set `use_docling=True` in `config.py`.
