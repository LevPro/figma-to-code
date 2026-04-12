"""
Ollama LLM Provider

Wrapper around langchain_ollama.ChatOllama for use with the Figma to Code converter.
Supports local Ollama server with custom models and parameters.
"""

from typing import Optional
from langchain_ollama import ChatOllama


def ollama(
    model: str = "gpt-oos",
    base_url: str = "http://localhost:11434",
    temperature: float = 0.2,
    reasoning: str = "none",
    cache: bool = True,
    response_format: Optional[type] = None
) -> ChatOllama:
    """
    Initialize and return ChatOllama instance.
    
    Configuration priority (highest to lowest):
    1. Environment variables (MODEL, TEMPERATURE, REASONING_EFFORT, BASE_URL, ENABLE_CACHE)
    2. Function arguments (default values)
    
    Note: Ollama must be running locally (ollama serve) before use.
    
    Args:
        model: Model name from Ollama (overridden by MODEL env var)
        base_url: Ollama server URL (overridden by BASE_URL env var).
                  Default is http://localhost:11434 for local Ollama instances.
        temperature: Sampling temperature 0-1 (overridden by TEMPERATURE env var)
        reasoning: Enable reasoning (overridden by REASONING_EFFORT env var)
        cache: Enable langchain in-memory cache (overridden by ENABLE_CACHE env var)
        
    Returns:
        ChatOllama configured instance ready for invocation
    """
    llm_kwargs = {
        "model": model,
        "cache": cache,
        "temperature": temperature,
        "base_url": base_url,
        "streaming": False,
        "reasoning": {"effort": reasoning}
    }
    
    llm = ChatOllama(**llm_kwargs)
    
    if response_format:
        return llm.with_structured_output(response_format)
    
    return llm
    