"""Prompt for the 'sme_training' node."""
from langchain_core.prompts import ChatPromptTemplate

SME_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are becoming a subject-matter expert on the document below.\n"
            "Build a study brief that an expert would carry in their head: a glossary, "
            "key facts, how concepts connect, common learner misconceptions, and "
            "practice questions with answers.\n"
            "Every item must be supported by the document. Do not invent facts.\n"
            "Do not include reasoning or <think> tags. Return only the requested JSON.",
        ),
        (
            "human",
            "<analysis>\n{analysis}\n</analysis>\n\n"
            "<document>\n{document}\n</document>\n\n{format_instructions}",
        ),
    ]
)
