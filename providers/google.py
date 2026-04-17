"""
Google LLM Provider

Wrapper around langchain_google.ChatGoogleGenerativeAI for use with the Figma to Code converter.
Supports custom models, temperature, and structured output.
"""

import os

from typing import TypeVar, Type
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def google(
    apiKey: str = "",
    model: str = "gemini-2.0-flash-exp",
    base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    temperature: float = 0.2,
    reasoning: str = "none",
    cache: bool = True,
) -> ChatGoogleGenerativeAI:
    """
    Initialize and return ChatGoogleGenerativeAI instance.

    Configuration priority (highest to lowest):
    1. Environment variables (API_KEY, MODEL, TEMPERATURE, REASONING, BASE_URL, ENABLE_CACHE)
    2. Function arguments (default values)

    Args:
        apiKey: Google API key
        model: Model name
        base_url: API endpoint URL
        temperature: Sampling temperature 0-1
        reasoning: Enable reasoning/thinking mode
        cache: Enable langchain in-memory cache

    Returns:
        ChatGoogleGenerativeAI configured instance ready for invocation
    """
    os.environ["GOOGLE_API_KEY"] = apiKey

    llm_kwargs = {
        "model": model,
        "streaming": False,
        "cache": cache,
        "temperature": temperature,
        "max_retries": 2,
        "api_key": apiKey,
    }

    llm = ChatGoogleGenerativeAI(**llm_kwargs)

    return llm


def create_structured_llm(
    base_llm: ChatGoogleGenerativeAI, response_format: Type[T]
) -> ChatGoogleGenerativeAI:
    """
    Wrap a base LLM with structured output support.

    Uses LangChain's with_structured_output() to enforce strict
    Pydantic schema validation on model responses. This eliminates
    the need for regex-based JSON parsing.

    Args:
        base_llm: Base ChatGoogleGenerativeAI instance from google()
        response_format: Pydantic BaseModel class for output validation

    Returns:
        ChatGoogleGenerativeAI wrapped with structured output support.
        When invoked, returns parsed Pydantic model instance.
    """
    structured_llm = base_llm.with_structured_output(
        response_format, method="json_schema", include_raw=False
    )
    return structured_llm
