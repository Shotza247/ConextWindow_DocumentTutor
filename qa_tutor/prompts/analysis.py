"""Prompt for the 'analyze' node."""
from langchain_core.prompts import ChatPromptTemplate

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an instructional designer analysing a document before it is taught.\n"
            "Use only the document. Do not invent content.\n"
            "Produce an ordered lesson outline that moves from foundations to advanced ideas.\n"
            "Do not include reasoning or <think> tags. Return only the requested JSON.",
        ),
        ("human", "<document>\n{document}\n</document>\n\n{format_instructions}"),
    ]
)
