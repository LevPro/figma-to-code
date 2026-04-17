# Figma to Code Converter

A Python-based tool that automatically converts Figma design exports (JSON + Images) into production-ready HTML/CSS/JS pages using Large Language Models (LLMs). It employs a two-stage AI pipeline to ensure structural integrity and responsive design compliance.

## 📖 Description

This project bridges the gap between design and development by automating the conversion of Figma files into frontend code. Unlike simple image-to-code tools, this converter parses structured JSON data exported from Figma (representing layout, typography, colors, etc.) to generate semantic HTML5, mobile-first CSS3, and isolated JavaScript logic.

**Key Features:**
*   **Two-Stage Pipeline**: 
    1.  **Block Generation**: Converts individual design sections into isolated code blocks.
    2.  **Page Assembly**: Merges blocks with header/footer into a complete page, handling style collisions and responsive media queries.
*   **Multi-Provider Support**: Works with OpenAI (GPT), Ollama (local models), Anthropic (Claude), and Google (Gemini).
*   **Mobile-First Approach**: Generates code specifically targeting mobile viewports first (`<993px`), then applies desktop overrides.
*   **Structured Output**: Uses Pydantic schemas to enforce strict JSON compliance from LLMs, eliminating parsing errors.
*   **Image Optimization**: Compresses reference images to reduce token usage before sending them to the model.

## 🚀 Quick Start

### 1. Installation

Ensure you have Python 3.10+ installed. Install the required dependencies:

```bash
pip install langchain langchain-openai langchain-anthropic langchain-google-genai pydantic pillow
# For Ollama support if needed:
pip install langchain-ollama
```

### 2. Prepare Input Data

Create an `input` directory with the following structure containing Figma exports (JSON) and reference images (JPG/PNG):

```text
INPUT_DIR/
├── pc/
│   ├── header.json, header.jpg
│   ├── footer.json, footer.jpg
│   └── page_name/
│       ├── 1.json, 1.jpg
│       └── page.jpg (Full desktop preview)
└── mobile/
    ├── header.json, header.jpg
    ├── footer.json, footer.jpg
    └── page_name/
        ├── 1.json, 1.jpg
        └── page.jpg (Full mobile preview)
```

### 3. Run the Converter

**Option A: Using Environment Variables**
```bash
export INPUT_DIR=./input
export OUTPUT_DIR=./output
export PROVIDER=openai
export API_KEY=sk-...

python main.py
```

**Option B: Using CLI Arguments (Recommended)**
```bash
python main.py -i ./input -o ./output -p openai -m gpt-5-nano --api-key sk-xxx
```

## ⚙️ Parameters Description

The application supports configuration via Environment Variables or Command Line Interface. CLI arguments take precedence over environment variables.

| Parameter | Alias | Default | Description |
| :--- | :--- | :--- | :--- |
| `--input-dir` | `-i` | *Required* | Path to the directory containing Figma JSON exports and images. |
| `--output-dir` | `-o` | *Required* | Path to save generated HTML/CSS/JS files. |
| `--provider` | `-p` | `openai` | LLM Provider: `openai`, `ollama`, `anthropic`, `google`. |
| `--model` | `-m` | `gpt-5-nano` | Model identifier (e.g., `claude-3-haiku`, `llama3`). |
| `--api-key` | - | *Required* for OpenAI | API key for the selected provider. |
| `--base-url` | - | *Provider Default* | Custom LLM endpoint URL (useful for Ollama or proxies). |
| `--temperature` | `-t` | `0.1` | Sampling temperature (0-2). Lower = more deterministic. |
| `--reasoning` | - | `none` | Reasoning effort: `none`, `low`, `medium`, `high`. |
| `--compress-images` | - | `True` | Enable automatic compression of reference images to save tokens. |
| `--image-quality` | - | `85` | JPEG quality for compressed images (1-100). |
| `--enable-cache` | - | `True` | Cache LLM responses to avoid re-processing identical inputs. |
| `--max-retries` | - | `2` | Retry attempts if the model fails during generation. |

## 📋 Requirements

*   **Python**: 3.10 or higher
*   **Core Libraries**:
    *   `langchain-core`: Message handling and LLM interface.
    *   `pydantic`: Schema validation for structured JSON output.
    *   `Pillow (PIL)`: Image processing, resizing, and compression.
    *   `argparse`: Command-line argument parsing.
*   **LLM Providers**:
    *   OpenAI (`langchain_openai`)
    *   Ollama (`langchain_ollama`)
    *   Anthropic (`langchain_anthropic`)
    *   Google (`langchain_google_genai`)

## 📐 Specifications & Pipeline Details

### 1. Input Format
The tool expects Figma JSON exports that include:
*   **Node Types**: `FRAME`, `GROUP`, `SECTION` (containers), `TEXT`, `RECTANGLE`, `COMPONENT`.
*   **Properties**: `absoluteBoundingBox`, `layoutMode` (Flexbox mapping), `fill` (colors), `stroke`, `effects` (shadows/blurs).
*   **Responsive Data**: Separate JSON files for "pc" (Desktop, ≥993px) and "mobile" (<993px) views.

### 2. Output Structure
For every page processed, the tool generates a subdirectory containing:
```text
output_dir/
└── {page_name}/
    ├── index.html   # Complete HTML document with DOCTYPE & body
    ├── styles.css   # Merged CSS (Reset + Block Styles + Media Queries)
    └── script.js    # Combined JS wrapped in DOMContentLoaded
```

### 3. Conversion Logic
*   **Step 1: Block Generation**
    *   The LLM parses Figma JSON nodes recursively.
    *   Maps layout properties (e.g., `HORIZONTAL` → `flex-direction: row`).
    *   Generates isolated code wrapped in unique class prefixes (`.fig-block-{id}`) to prevent CSS leakage.
*   **Step 2: Page Assembly**
    *   Assembles Header + Blocks + Footer into a single document.
    *   Merges CSS, deduplicating imports and consolidating `@media` queries at the end.
    *   Wraps JS in `try/catch` blocks for safety.

### 4. Error Handling & Safety
*   **Retry Logic**: Automatically retries generation up to `max_retries` times if errors occur.
*   **Image Compression**: Reduces image size dynamically before sending to LLM to prevent token limits and speed up processing.
*   **Path Traversal Protection**: Sanitizes file names during output saving.

## ⚠️ Notes
*   Ensure your Figma export JSON includes `characters`, `style` (typography), and `fill` properties for accurate rendering.
*   For local Ollama usage, ensure the server is running (`ollama serve`) and the model is pulled before execution.
*   The tool assumes a breakpoint at **993px** based on standard responsive design practices (Mobile < 993px).

## 📚 Documentation

For detailed API references and method documentation, please visit our [API Reference Guide](docs/API_REFERENCE.md).