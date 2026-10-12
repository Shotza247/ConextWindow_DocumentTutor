"""Streamlit chat UI.   Run:  streamlit run app.py"""
import os

import streamlit as st

from qa_tutor.config import Settings
from qa_tutor.ingestion.loader import clean_source, display_name, save_upload
from qa_tutor.llm.model import KEY_FIELDS, has_credentials, using_proxy
from qa_tutor.tutor import Tutor

settings = Settings()

st.set_page_config(page_title="Document Tutor", page_icon="🎓")
st.title("🎓 Document Tutor")

# st.session_state keeps values between reruns (Streamlit reruns this file on every click).
st.session_state.setdefault("tutor", None)
st.session_state.setdefault("chat", [])
st.session_state.setdefault("source_names", [])


def add_message(role: str, content: str) -> None:
    st.session_state.chat.append({"role": role, "content": content})


def process_sources(files, links_text: str) -> None:
    """Save uploads, read everything, and build a new Tutor."""
    sources = [save_upload(f.name, f.getvalue(), settings.cache_dir) for f in files]
    sources += [clean_source(line) for line in links_text.splitlines() if line.strip()]
    if not sources:
        st.sidebar.warning("Upload a file or paste a link first.")
        return
    try:
        with st.spinner("Reading and studying your material. This can take a minute..."):
            tutor = Tutor(settings)
            tutor.load(sources)
    except Exception as error:
        st.sidebar.error(f"Could not process your material: {error}")
        return
    st.session_state.tutor = tutor
    st.session_state.chat = []
    st.session_state.source_names = [display_name(s) for s in sources]


# ---------------- sidebar: add material ----------------
with st.sidebar:
    st.header("1. Add your material")
    files = st.file_uploader(
        "Upload documents", type=["pdf", "txt", "md"], accept_multiple_files=True
    )
    links_text = st.text_area("Links (one per line)", placeholder="https://example.com/article")

    if not using_proxy():
        with st.expander("API keys", expanded=not has_credentials()):
            st.caption("Hugging Face is tried first; OpenAI is used if it fails or runs out of credits.")
            for label, env_name in KEY_FIELDS.items():
                value = st.text_input(label, type="password", help="Or put it in your .env / secrets.")
                if value:
                    os.environ[env_name] = value
        if not has_credentials():
            st.warning("Add at least one API key to continue.")

    if st.button("Process documents", type="primary"):
        process_sources(files, links_text)

    if st.session_state.source_names:
        st.success(f"Loaded {len(st.session_state.source_names)} source(s):")
        for name in st.session_state.source_names:
            st.caption(f"• {name}")

# ---------------- main area ----------------
tutor = st.session_state.tutor

if tutor is None:
    st.info("👈 Upload documents or paste links in the sidebar, then click **Process documents**.")
else:
    analysis = tutor.analysis
    with st.expander(f"📘 {analysis['title']} ({analysis['difficulty']})", expanded=not st.session_state.chat):
        st.write(analysis["summary"])
        st.markdown("**Lesson outline**")
        for number, step in enumerate(analysis["lesson_outline"], start=1):
            st.markdown(f"{number}. {step['title']}")

    start_col, next_col = st.columns(2)
    finished = tutor.step >= tutor.total_steps
    if start_col.button("▶ Start guided walkthrough", use_container_width=True):
        with st.spinner("Preparing step 1..."):
            reply = tutor.start_walkthrough()
        add_message("assistant", f"**Step {tutor.step} of {tutor.total_steps}**\n\n{reply}")
        st.rerun()
    if next_col.button(
        "Next step ➡", use_container_width=True, disabled=tutor.step == 0 or finished
    ):
        with st.spinner("Preparing the next step..."):
            reply = tutor.next_step()
        add_message("assistant", f"**Step {tutor.step} of {tutor.total_steps}**\n\n{reply}")
        st.rerun()

for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask a question about your material", disabled=tutor is None):
    add_message("user", question)
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                answer = tutor.ask(question)
        except Exception as error:
            answer = f"Sorry, something went wrong: {error}"
        st.markdown(answer)
    add_message("assistant", answer)