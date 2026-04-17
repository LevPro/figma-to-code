# API Reference Index

Welcome to the Figma-to-Code Converter API documentation. This index provides direct access to detailed method references for each module.

## 📋 Module Documentation

### Core Pipeline
- **[Core Methods (`main.py`)](docs/01_core_methods.md)**: Entry points, generation logic, and assembly functions.

### Configuration & Settings
- **[Configuration Management (`settings.py`)](docs/02_config_settings.md)**: CLI arguments, environment variables, and `Config` class details.

### Data Processing
- **[Data Loading (`load_data.py`)](docs/03_data_loading.md)**: Input parsing and Figma JSON handling.
- **[Image Utilities (`image.py`)](docs/04_image_utils.md)**: Compression, dimension extraction, and token estimation.

### Schema & Models
- **[Pydantic Models (`models.py`)](docs/05_models.md)**: Response schemas for structured LLM output.

### LLM Integration
- **[Agent Prompts](docs/06_agents.md)**: System prompts and message builders for block generation and assembly.
- **[Provider Wrappers](docs/07_providers.md)**: Configuration wrappers for OpenAI, Ollama, Anthropic, and Google.

## 🔗 Main Reference
For a complete consolidated view of all methods, see the [Full API Reference](API_REFERENCE.md).
