# Figma to Code Converter

A tool that converts Figma design exports into responsive HTML/CSS/JavaScript code using LLMs.

## Overview

This project implements a two-stage conversion pipeline:

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Input Data     │ ──▶  │  Stage 1:        │ ──▶  │  Stage 2:   │
│  (JSON + images) │      │  Block Generation│      │  Assembly  │
└─────────────────┘      └──────────────────┘      └─────────────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │  Output    │
                                         │  (HTML/   │
                                         │   CSS/JS) │
                                         └─────────────┘
```

## Stage 1: Block Generation

Each design component (header, footer, page sections) is converted individually:

- Input: Figma JSON + reference image
- Output: HTML fragment, CSS, JavaScript for that block
- Uses LLM with vision capability to interpret designs

## Stage 2: Page Assembly

Generated blocks are combined into complete pages:

- Input: All blocks + full page preview
- Output: Complete HTML document with merged CSS/JS

## Supported LLM Providers

- **OpenAI**: GPT models with vision (gpt-4o, gpt-4o-mini, etc.)
- **Ollama**: Local LLM server with vision-capable models

## Directory Structure

```
figma-to-code/
├── main.py                 # Entry point
├── config/settings.py     # Configuration
├── data/
│   ├── load_data.py       # Input loader
│   └── image.py          # Image compression
├── providers/
│   ├── openai.py         # OpenAI provider
│   └── ollama.py        # Ollama provider
├── agents/
│   ├── build_block.py        # Block generation prompts
│   ├── build_assemble.py   # Assembly prompts
│   └── response/formats.py # Response schemas
└── docs/                 # Documentation
```

## Requirements

- Python 3.10+
- OpenAI API key (for OpenAI provider) or Ollama (for local provider)
- Figma JSON exports with reference images

## Quick Start

```bash
# OpenAI example
INPUT_DIR=./input OUTPUT_DIR=./output PROVIDER=openai API_KEY=sk-... python main.py

# Ollama example
INPUT_DIR=./input OUTPUT_DIR=./output PROVIDER=ollama MODEL=llama3.2-vision python main.py
```

See [USAGE.md](docs/USAGE.md) for detailed usage instructions.