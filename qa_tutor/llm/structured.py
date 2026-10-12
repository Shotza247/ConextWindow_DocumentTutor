"""Helpers to run a prompt and get plain text or validated JSON back."""
from __future__ import annotations

import re
from typing import TypeVar

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def strip_thinking_tags(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # unclosed tag = output was truncated mid-reasoning
    if "<think>" in text:
        raise RuntimeError(
            "Model output was truncated while still reasoning. "
            "Increase max_new_tokens or use a non-reasoning model."
        )
    return text.strip()


def text_chain(prompt, llm):
    """prompt -> llm -> plain text with reasoning tags removed."""
    return prompt | llm | StrOutputParser() | RunnableLambda(strip_thinking_tags)


def run_structured(llm, prompt, schema: type[T], inputs: dict, retries: int = 1) -> T:
    parser = PydanticOutputParser(pydantic_object=schema)
    chain = text_chain(prompt, llm)
    payload = {**inputs, "format_instructions": parser.get_format_instructions()}

    last_error, last_text = None, ""
    for _ in range(retries + 1):
        last_text = chain.invoke(payload)
        try:
            return parser.parse(last_text)
        except OutputParserException as error:
            last_error = error
    raise RuntimeError(
        f"Model did not return valid {schema.__name__} JSON after {retries + 1} attempts.\n"
        f"Last output (first 500 chars): {last_text[:500]!r}\n"
        f"Parser error: {last_error}"
    ) from last_error