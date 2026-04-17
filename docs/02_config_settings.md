# Configuration Management (`settings.py`)

This module handles centralized configuration with sensible defaults and environment variable overrides. It supports both CLI arguments and environment variables, where CLI takes precedence.

## Class: `Config`

A dataclass container for all application settings. All values can be set via environment variables or passed directly to the constructor.

### Attributes
| Attribute | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `input_dir` | `Path` | `None` | Path to input Figma data directory. |
| `output_dir` | `Path` | `None` | Path to output generated code directory. |
| `provider` | `str` | `"openai"` | LLM Provider (`openai`, `ollama`, etc.). |
| `model` | `str` | `"gpt-5-nano"` | Specific model identifier. |
| `temperature` | `float` | `0.1` | Sampling temperature (0–2). |
| `max_retries` | `int` | `2` | Retry attempts on LLM failure. |
| `compress_images` | `bool` | `True` | Enable image compression optimization. |

### Methods

#### `from_args(cls, args)`
Creates configuration from CLI arguments with environment variable defaults.
*   **Precedence**: CLI Arguments > Environment Variables > Defaults.
*   **Usage**: Called during startup in `main.py`.

#### `from_env(cls)`
Initializes configuration strictly from environment variables (e.g., `INPUT_DIR`, `API_KEY`).
*   **Environment Variables Supported**:
    *   `INPUT_DIR`, `OUTPUT_DIR`
    *   `PROVIDER`, `MODEL`, `BASE_URL`, `API_KEY`
    *   `TEMPERATURE`, `REASONING_EFFORT`, `MAX_RETRIES`
    *   `COMPRESS_IMAGES`, `IMAGE_QUALITY`
    *   `ENABLE_CACHE`, `LOG_LEVEL`, `HIDE_API_KEYS`

#### `validate()`
Validates configuration and returns a list of error messages (empty if valid).
*   **Checks**: Directory existence, provider validity, API key presence for OpenAI, temperature range (0–2), image quality range (1–100).

---

### CLI Arguments (`create_parser`)

The argument parser supports the following flags:
*   `-i/--input-dir`: Input directory path.
*   `-o/--output-dir`: Output directory path.
*   `-p/--provider`: LLM provider choice.
*   `-m/--model`: Model name.
*   `--api-key`: API key for OpenAI.
*   `-t/--temperature`: Sampling temperature.
*   `--compress-images`: Enable/disable image compression.
