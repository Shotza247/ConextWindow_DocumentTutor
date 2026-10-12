"""Node 4: answer questions, or teach one lesson step at a time."""
from __future__ import annotations

import json

from langchain_core.messages import AIMessage, HumanMessage

from qa_tutor.config import Settings
from qa_tutor.llm.structured import text_chain
from qa_tutor.prompts.tutor import ASK_PROMPT, WALKTHROUGH_PROMPT


def make_tutor_node(llm, settings: Settings):
    ask_chain = text_chain(ASK_PROMPT, llm)
    walk_chain = text_chain(WALKTHROUGH_PROMPT, llm)

    def tutor(state: dict) -> dict:
        analysis = state["analysis"]
        outline = analysis["lesson_outline"]
        step = state.get("current_step", 0)
        history = state.get("messages", [])[-settings.history_window :]

        context = {
            "analysis": json.dumps(analysis, indent=2),
            "sme_brief": json.dumps(state["sme_brief"], indent=2),
            "document": state["document_markdown"],
            "history": history,
        }

        if state.get("mode") == "walkthrough":
            if step >= len(outline):
                text = "You've completed the walkthrough. Ask me anything, or type /start to begin again."
                return {"answer": text, "messages": [AIMessage(content=text)]}

            current = outline[step]
            user_input = (
                f"Teach step {step + 1} of {len(outline)}: {current['title']}.\n"
                f"Objective: {current['objective']}\n"
                f"Key points: {json.dumps(current['key_points'])}\n"
                f"Finish with this check question: {current['check_question']}"
            )
            text = walk_chain.invoke({**context, "user_input": user_input})
            return {
                "answer": text,
                "current_step": step + 1,
                "messages": [
                    HumanMessage(content=f"Walk me through step {step + 1}: {current['title']}"),
                    AIMessage(content=text),
                ],
            }

        question = state["question"]
        text = ask_chain.invoke({**context, "user_input": question})
        return {
            "answer": text,
            "messages": [HumanMessage(content=question), AIMessage(content=text)],
        }

    return tutor
