# Installation Guide

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (for OpenAI provider) OR Ollama installed locally (for Ollama provider)

## Step 1: Clone and Setup

```bash
git clone <repository-url>
cd figma-to-code
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install langchain langchain-openai langchain-ollama pydantic pillow
```

## Step 4: Configure API Access

### OpenAI Provider

Set your API key:

```bash
# Environment variable (recommended)
export API_KEY=sk-your-key-here

# Or pass via CLI argument
python main.py --api-key sk-your-key-here ...
```

### Ollama Provider

1. Install Ollama: https://ollama.ai/
2. Pull a vision-capable model:

```bash
ollama pull llama3.2-vision
```

3. Start Ollama server:

```bash
ollama serve
```

## Verification

Test your setup:

```bash
# OpenAI test
python -c "from providers.openai import openai; print('OpenAI provider OK')"

# Ollama test  
python -c "from providers.ollama import ollama; print('Ollama provider OK')"
```

## Dependencies

Core dependencies:
- `langchain` - LLM framework
- `langchain-openai` - OpenAI integration
- `langchain-ollama` - Ollama integration
- `pydantic` - Response schemas
- `pillow` - Image compression

Development dependencies:
- `pytest` - Testing (optional)