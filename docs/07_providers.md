# LLM Provider Wrappers

This section documents the factory functions and structured output wrappers for supported LLM providers (OpenAI, Ollama, Anthropic, Google).

## Factory Functions

Each provider module provides an initialization function:
*   **`openai(...)`**: Initializes `ChatOpenAI`.
*   **`anthropic(...)`**: Initializes `ChatAnthropic`.
*   **`google(...)`**: Initializes `ChatGoogleGenerativeAI`.
*   **`ollama(...)`**: Initializes `ChatOllama`.

**Common Parameters**:
*   `apiKey`: Provider API key.
*   `model`: Model identifier (e.g., `gpt-4`, `claude-3`).
*   `temperature`: Sampling rate.
*   `reasoning`: Enable reasoning mode (`none`, `low`, etc.).

## Structured Output Wrapper: `create_structured_llm`
Universal function to wrap any base LLM with structured output support.

*   **Signature**: `(base_llm, response_format: Type[T]) -> ChatModel`
*   **Logic**: Uses LangChain's `with_structured_output()`.
    *   **OpenAI/Anthropic/Google**: Uses method `"json_schema"`.
    *   **Ollama**: Uses method `"function_calling"` (due to tool-calling emulation).