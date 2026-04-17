"""
OpenAI LLM Provider

Wrapper around langchain_openai.ChatOpenAI for use with the Figma to Code converter.
Supports custom models, temperature, base_url, reasoning mode, and structured output.
"""

import os
import json
import re
import logging
from typing import TypeVar, Generic, Type

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def parse_json_from_text(text: str) -> dict:
    """
    Extract JSON from LLM response text.

    Handles various formats:
    - Raw JSON: {"key": "value"}
    - JSON in markdown code blocks: ```json\n{...}\n```
    - JSON with surrounding text

    Args:
        text: Raw text response from LLM

    Returns:
        Parsed JSON dict

    Raises:
        ValueError: If no valid JSON found
    """
    # Try to find JSON in markdown code blocks
    code_block_pattern = r"```(?:json)?\s*\n(.*?)```"
    code_block_match = re.search(code_block_pattern, text, re.DOTALL)
    
    if code_block_match:
        json_str = code_block_match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Try to find JSON object in text
    json_pattern = r"\{.*\}"
    json_match = re.search(json_pattern, text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON in response: {json_str}") from e

    raise ValueError(f"No JSON found in response: {text}")


def fallback_structured_output(text: str, response_format: Type[T]) -> T:
    """
    Fallback parser for when with_structured_output fails.

    Manually extracts JSON from text and validates against Pydantic schema.

    Args:
        text: Raw text response from LLM
        response_format: Pydantic BaseModel class for validation

    Returns:
        Validated Pydantic model instance

    Raises:
        ValueError: If JSON parsing or validation fails
    """
    json_data = parse_json_from_text(text)
    return response_format(**json_data)


def openai(
    apiKey: str = "",
    model: str = "gpt-5-nano",
    base_url: str = "https://api.openai.com/v1",
    temperature: float = 0.2,
    reasoning: str = "none",
    cache: bool = True
) -> ChatOpenAI:
    """
    Initialize and return ChatOpenAI instance.

    Configuration priority (highest to lowest):
    1. Environment variables (API_KEY, MODEL, TEMPERATURE, REASONING, BASE_URL, ENABLE_CACHE)
    2. Function arguments (default values)

    Args:
        apiKey: OpenAI API key
        model: Model name
        base_url: API endpoint URL
        temperature: Sampling temperature 0-1
        reasoning: Enable reasoning/thinking mode
        cache: Enable langchain in-memory cache

    Returns:
        ChatOpenAI configured instance ready for invocation
    """
    os.environ["OPENAI_API_KEY"] = apiKey

    llm_kwargs = {
        "model": model,
        "streaming": False,
        "cache": cache,
        "temperature": temperature,
        "max_retries": 2,
        "api_key": apiKey,
        "base_url": base_url,
    }

    if reasoning and reasoning != "none":
        llm_kwargs["reasoning_effort"] = reasoning

    llm = ChatOpenAI(**llm_kwargs)

    return llm


def create_structured_llm(
    base_llm: ChatOpenAI,
    response_format: Type[T]
) -> "StructuredOutputWrapper":
    """
    Wrap a base LLM with structured output support.

    Uses LangChain's with_structured_output() to enforce strict
    Pydantic schema validation on model responses. If that fails
    (e.g., with LM Studio or incompatible models), falls back to
    manual JSON parsing.

    Args:
        base_llm: Base ChatOpenAI instance from openai()
        response_format: Pydantic BaseModel class for output validation

    Returns:
        StructuredOutputWrapper that tries structured output first,
        then falls back to manual JSON parsing.
    """
    return StructuredOutputWrapper(base_llm, response_format)


class StructuredOutputWrapper:
    """
    Wrapper that attempts to use with_structured_output, but falls back
    to manual JSON parsing if it fails.

    This is needed because some OpenAI-compatible servers (like LM Studio
    with Qwen models) don't properly support function calling or JSON schema.
    """

    def __init__(self, base_llm: ChatOpenAI, response_format: Type[T]):
        self.base_llm = base_llm
        self.response_format = response_format
        self.use_fallback = False

        # Try to create structured output wrapper
        try:
            self.structured_llm = base_llm.with_structured_output(
                response_format,
                method="json_schema",
                include_raw=False
            )
        except Exception as e:
            logger.warning(f"Failed to create structured output: {e}. Using fallback parser.")
            self.use_fallback = True
            self.structured_llm = None

    def invoke(self, messages, **kwargs):
        """
        Invoke LLM with structured output.

        Tries with_structured_output first, falls back to manual parsing.

        Args:
            messages: List of messages (same as LangChain invoke)
            **kwargs: Additional arguments to pass to invoke

        Returns:
            Pydantic model instance
        """
        if self.use_fallback or self.structured_llm is None:
            return self._invoke_with_fallback(messages, **kwargs)
        
        try:
            return self.structured_llm.invoke(messages, **kwargs)
        except Exception as e:
            logger.warning(f"Structured output failed, using fallback: {e}")
            self.use_fallback = True
            return self._invoke_with_fallback(messages, **kwargs)

    def _invoke_with_fallback(self, messages, **kwargs):
        """
        Fallback: invoke without structured output, then parse JSON manually).

        Args:
            messages: List of messages
            **kwargs: Additional arguments

        Returns:
            Pydantic model instance
        """
        # Get raw text response
        raw_response: AIMessage = self.base_llm.invoke(messages, **kwargs)
        
        # Extract content from AIMessage
        text_content = raw_response.content
        if isinstance(text_content, list):
            # Sometimes content is a list of content parts
            text_content = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in text_content
            )

        logger.debug(f"Raw response: {text_content[:200]}...")

        # Parse JSON manually
        return fallback_structured_output(text_content, self.response_format)
    