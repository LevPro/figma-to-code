# Usage Guide

## Input Directory Structure

The tool expects this directory structure:

```
INPUT_DIR/
├── pc/
│   ├── header.json      # Header design (JSON export from Figma)
│   ├── header.jpg      # Header reference image
│   ├── footer.json    # Footer design
│   ├── footer.jpg     # Footer reference image
│   └── page_name/
│       ├── 1.json     # Section 1 design
│       ├── 1.jpg      # Section 1 image
│       ├── 2.json     # Section 2 design
│       ├── 2.jpg      # Section 2 image
│       └── page.jpg   # Full page preview
└── mobile/
    ├── header.json
    ├── header.jpg
    ├── footer.json
    ├── footer.jpg
    └── page_name/
        ├── 1.json
        ├── 1.jpg
        └── page.jpg
```

## Running the Converter

### Basic Usage

```bash
# Using environment variables
INPUT_DIR=./input OUTPUT_DIR=./output PROVIDER=openai API_KEY=sk-... python main.py

# Using CLI arguments
python main.py -i ./input -o ./output -p openai --api-key sk-...
```

### OpenAI Provider

```bash
INPUT_DIR=./input \
OUTPUT_DIR=./output \
PROVIDER=openai \
API_KEY=sk-your-key \
MODEL=gpt-4o-mini \
TEMPERATURE=0.2 \
python main.py
```

### Ollama Provider

```bash
INPUT_DIR=./input \
OUTPUT_DIR=./output \
PROVIDER=ollama \
MODEL=llama3.2-vision \
BASE_URL=http://localhost:11434 \
python main.py
```

### Custom Provider

To use a custom LLM provider, see [API.md](API.md#custom-llm-provider-integration) for integration instructions.

## CLI Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--input-dir` | `-i` | Input directory path | (required) |
| `--output-dir` | `-o` | Output directory path | (required) |
| `--provider` | `-p` | LLM provider (openai/ollama) | openai |
| `--model` | `-m` | Model name | gpt-5-nano |
| `--base-url` | | Custom API endpoint | OpenAI default |
| `--api-key` | | OpenAI API key | (required for OpenAI) |
| `--temperature` | `-t` | LLM temperature (0-2) | 0.1 |
| `--reasoning` | | Reasoning level (none/low/medium/high) | none |
| `--max-retries` | | Max retry attempts | 2 |
| `--compress-images` | | Enable image compression | true |
| `--image-quality` | | JPEG quality (1-100) | 85 |
| `--cache` | | Enable LLM caching | true |
| `--log-level` | | Logging level | INFO |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `INPUT_DIR` | Input directory path |
| `OUTPUT_DIR` | Output directory path |
| `PROVIDER` | LLM provider (openai/ollama) |
| `MODEL` | Model name |
| `API_KEY` | OpenAI API key |
| `BASE_URL` | Custom API endpoint |
| `TEMPERATURE` | LLM temperature |
| `REASONING_EFFORT` | Enable reasoning |
| `MAX_RETRIES` | Max retry attempts |
| `COMPRESS_IMAGES` | Enable image compression |
| `IMAGE_QUALITY` | JPEG quality |
| `ENABLE_CACHE` | Enable LLM caching |
| `LOG_LEVEL` | Logging level |

## Output

The tool creates a directory for each page:

```
OUTPUT_DIR/
├── page_name/
│   ├── index.html    # Complete HTML document
│   ├── styles.css   # Merged CSS
│   └── script.js   # Combined JavaScript
└── another_page/
    └── ...
```

## Examples

### Minimal Example

```bash
INPUT_DIR=./input OUTPUT_DIR=./output PROVIDER=openai API_KEY=sk-... python main.py
```

### With Custom Model

```bash
python main.py \
  --input-dir ./designs \
  --output-dir ./output \
  --provider openai \
  --model gpt-4o \
  --temperature 0.3
```

### With Debug Logging

```bash
python main.py \
  --input-dir ./input \
  --output-dir ./output \
  --provider openai \
  --api-key sk-... \
  --log-level DEBUG
```

## Troubleshooting

### "No input directory specified"

Set `INPUT_DIR` or use `-i/--input-dir`:

```bash
INPUT_DIR=./input python main.py
```

### "API_KEY is required"

Pass your OpenAI API key:

```bash
python main.py --api-key sk-your-key ...
```

### Image compression too slow

Disable compression:

```bash
python main.py --compress-images false ...
```