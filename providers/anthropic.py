"""
Anthropic LLM Provider

Wrapper around langchain_anthropic.ChatAnthropic for use with the Figma to Code converter.
Supports custom models, temperature, and structured output.
"""

import os
from typing import TypeVar, Type

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def anthropic(
    apiKey: str = "",
    model: str = "claude-3-5-sonnet-latest",
    base_url: str = "https://api.anthropic.com/v1",
    temperature: float = 0.2,
    reasoning: str = "none",
    cache: bool = True,
) -> ChatAnthropic:
    """
    Initialize and return ChatAnthropic instance.

    Configuration priority (highest to lowest):
    1. Environment variables (API_KEY, MODEL, TEMPERATURE, REASONING, BASE_URL, ENABLE_CACHE)
    2. Function arguments (default values)

    Args:
        apiKey: Anthropic API key
        model: Model name
        base_url: API endpoint URL
        temperature: Sampling temperature 0-1
        reasoning: Enable reasoning/thinking mode
        cache: Enable langchain in-memory cache

    Returns:
        ChatAnthropic configured instance ready for invocation
    """
    os.environ["ANTHROPIC_API_KEY"] = apiKey

    llm_kwargs = {
        "model": model,
        "streaming": False,
        "cache": cache,
        "temperature": temperature,
        "max_retries": 2,
        "api_key": apiKey,
    }

    llm = ChatAnthropic(**llm_kwargs)

    return llm


def create_structured_llm(
    base_llm: ChatAnthropic, response_format: Type[T]
) -> ChatAnthropic:
    """
    Wrap a base LLM with structured output support.

    Uses LangChain's with_structured_output() to enforce strict
    Pydantic schema validation on model responses. This eliminates
    the need for regex-based JSON parsing.

    Args:
        base_llm: Base ChatAnthropic instance from anthropic()
        response_format: Pydantic BaseModel class for output validation

    Returns:
        ChatAnthropic wrapped with structured output support.
        When invoked, returns parsed Pydantic model instance.
    """
    structured_llm = base_llm.with_structured_output(
        response_format, method="json_schema", include_raw=False
    )
    return structured_llm
