"""
OpenAI LLM Provider

Wrapper around langchain_openai.ChatOpenAI for use with the Figma to Code converter.
Supports custom models, temperature, base_url, and reasoning mode.
"""

import os

from typing import Optional
from langchain_openai import ChatOpenAI


def openai(
    apiKey: str = "",
    model: str = "gpt-5-nano",
    base_url: str = "https://api.openai.com/v1",
    temperature: float = 0.2,
    reasoning: str = "none",
    cache: bool = True,
    response_format: Optional[type] = None
) -> ChatOpenAI:
    """
    Initialize and return ChatOpenAI instance.
    
    Configuration priority (highest to lowest):
    1. Environment variables (API_KEY, MODEL, TEMPERATURE, REASONING, BASE_URL, ENABLE_CACHE)
    2. Function arguments (default values)
    
    Args:
        apiKey: OpenAI API key (overridden by API_KEY env var)
        model: Model name (overridden by MODEL env var)
        base_url: API endpoint URL (overridden by BASE_URL env var)
        temperature: Sampling temperature 0-1 (overridden by TEMPERATURE env var)
        reasoning: Enable reasoning/thinking mode (overridden by REASONING env var)
        cache: Enable langchain in-memory cache (overridden by ENABLE_CACHE env var)
        
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
        "reasoning": {"effort": reasoning}
    }
    
    llm = ChatOpenAI(**llm_kwargs)
    
    if response_format:
        return llm.with_structured_output(response_format)
    
    return llm
    