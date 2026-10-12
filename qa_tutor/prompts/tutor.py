"""Prompts for the tutor: one for questions, one for the guided walkthrough."""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

_CONTEXT = (
    "<analysis>\n{analysis}\n</analysis>\n\n"
    "<expert_brief>\n{sme_brief}\n</expert_brief>\n\n"
    "<document>\n{document}\n</document>"
)

_RULES = (
    "Ground every statement in the document or the expert brief.\n"
    'If something is not supported, say: "I don\'t know based on this document."\n'
    "Do not include reasoning or <think> tags.\n\n"
)

ASK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a patient tutor and subject-matter expert. Answer the learner's "
            "question clearly and concisely, using plain language and a short example "
            "when it helps. Watch for the misconceptions listed in the brief.\n"
            + _RULES
            + _CONTEXT,
        ),
        MessagesPlaceholder("history"),
        ("human", "{user_input}"),
    ]
)

WALKTHROUGH_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a guide walking a learner through this material one step at a time.\n"
            "Teach only the requested step: state its objective, explain the key points "
            "simply, give one example, then end with the step's check question.\n"
            "Do not jump ahead to later steps.\n"
            + _RULES
            + _CONTEXT,
        ),
        MessagesPlaceholder("history"),
        ("human", "{user_input}"),
    ]
)
