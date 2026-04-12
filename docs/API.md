# API Documentation

## Main Functions

### main()

Entry point. Orchestrates the conversion pipeline.

```python
def main():
    """
    Pipeline stages:
    1. Parse CLI arguments and load configuration
    2. Validate configuration
    3. Initialize LLM model
    4. Load input data
    5. Stage 1: Generate all blocks
    6. Stage 2: Assemble each page
    7. Save output files
    """
```

### generate_block()

Generate HTML/CSS/JS for a single design block.

```python
def generate_block(
    model,
    json_data: Dict[str, Any],
    block_name: str,
    config: Config
) -> Dict[str, str]:
    """
    Args:
        model: LangChain-compatible LLM
        json_data: Figma JSON (pc and mobile versions)
        block_name: Identifier for logging
        config: Configuration object
    
    Returns:
        {"html": "...", "css": "...", "js": "..."}
    
    Raises:
        RuntimeError: If retries exhausted
    """
```

### assemble_page()

Assemble a complete page from generated blocks.

```python
def assemble_page(
    model,
    page_name: str,
    header_result: Optional[Dict[str, str]],
    footer_result: Optional[Dict[str, str]],
    blocks: List[Dict[str, str]],
    page_image: Optional[str],
    config: Config
) -> Dict[str, str]:
    """
    Args:
        model: LangChain-compatible LLM
        page_name: Page identifier
        header_result: Generated header HTML/CSS/JS
        footer_result: Generated footer HTML/CSS/JS
        blocks: List of generated blocks
        page_image: Full page preview (base64)
        config: Configuration object
    
    Returns:
        {"html": "...", "css": "...", "js": "..."}
    """
```

### save_page()

Save page files to output directory.

```python
async def save_page(
    output_dir: Path,
    page_name: str,
    html: str,
    css: str,
    js: str
) -> bool:
    """
    Creates: output_dir/page_name/{index.html, styles.css, script.js}
    """
```

## Configuration

### Config class

Centralized configuration container.

```python
@dataclass
class Config:
    # Directory paths
    input_dir: Optional[Path]
    output_dir: Optional[Path]
    
    # LLM Provider settings
    provider: str = "openai"
    model: str = "gpt-5-nano"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.1
    reasoning_effort: bool = True
    
    # Retry settings
    max_retries: int = 2
    retry_delay_base: float = 1.0
    retry_delay_max: float = 30.0
    
    # Input validation
    max_file_size_mb: int = 50
    max_json_depth: int = 20
    max_pages: int = 50
    max_blocks_per_page: int = 100
    
    # Image processing
    compress_images: bool = True
    image_quality: int = 85
    max_image_dimension: int = 2048
    
    # LLM caching
    enable_cache: bool = True
    
    # Logging
    log_level: str = "INFO"
    hide_api_keys: bool = True
```

### create_parser()

Create CLI argument parser.

```python
def create_parser() -> argparse.ArgumentParser:
    """
    Returns parser with arguments:
    - -i/--input-dir: Input directory
    - -o/--output-dir: Output directory
    - -p/--provider: openai or ollama
    - -m/--model: Model name
    - --base-url: Custom API endpoint
    - --api-key: API key
    - -t/--temperature: Temperature (0-2)
    - --reasoning: Reasoning level
    - --max-retries: Max retries
    - --compress-images: Enable compression
    - --image-quality: JPEG quality
    - --cache: Enable caching
    - --log-level: Logging level
    """
```

### Config.from_env()

Load configuration from environment variables.

### Config.from_args()

Create configuration from CLI arguments (env vars used as defaults).

### Config.validate()

Validate configuration and return error list.

## Data Loading

### load_data()

Load Figma JSON exports and images.

```python
def load_data(root_dir: Union[str, Path]) -> Dict[str, Any]:
    """
    Expected structure:
    {
        "header": {"pc": {"json": ..., "image": ...}, "mobile": {...}},
        "footer": {...},
        "pages": {
            "page_name": {
                "blocks": [{"pc": {...}, "mobile": {...}}, ...],
                "page_image": "base64..."
            }
        }
    }
    """
```

## Image Processing

### compress_image_base64()

Compress a base64-encoded JPEG image.

```python
def compress_image_base64(
    image_base64: str,
    quality: int = 85,
    max_dimension: int = 2048
) -> Tuple[str, int]:
    """
    Args:
        image_base64: Base64-encoded image
        quality: JPEG quality (1-100)
        max_dimension: Max width/height
    
    Returns:
        (compressed_base64, reduction_percentage)
    """
```

### get_image_dimensions()

Get image dimensions.

```python
def get_image_dimensions(image_base64: str) -> Optional[Tuple[int, int]]:
    """Returns (width, height) or None"""
```

### estimate_token_count()

Estimate token count for vision models.

```python
def estimate_token_count(image_base64: str) -> int:
    """
    Based on OpenAI vision pricing:
    - <= 512x512: ~85 tokens
    - Larger: calculated by area
    """
```

## LLM Providers

### openai()

Initialize ChatOpenAI.

```python
def openai(
    apiKey: str = "",
    model: str = "gpt-5-nano",
    base_url: str = "https://api.openai.com/v1",
    temperature: float = 0.2,
    reasoning: str = "none",
    cache: bool = True,
    response_format: Optional[type] = None
) -> ChatOpenAI:
```

### ollama()

Initialize ChatOllama.

```python
def ollama(
    model: str = "gpt-oos",
    base_url: str = "http://localhost:11434",
    temperature: float = 0.2,
    reasoning: str = "none",
    cache: bool = True,
    response_format: Optional[type] = None
) -> ChatOllama:
```

## Response Schemas

### BlockResponse

Pydantic model for block generation responses.

```python
class BlockResponse(BaseModel):
    html_code: str
    css_code: str
    js_code: str
```

### AssemblyResponse

Pydantic model for page assembly responses.

```python
class AssemblyResponse(BaseModel):
    html_code: str
    css_code: str
    js_code: str
```

## Prompt Builders

### build_block_message()

Builds message for block generation.

```python
def build_block_message(json_data: Dict[str, Any]) -> HumanMessage:
    """
    Combines pc/mobile JSON and images into a single message.
    """
```

### build_assemble_message()

Builds message for page assembly.

```python
def build_assemble_message(
    header_result: Optional[Dict[str, str]],
    footer_result: Optional[Dict[str, str]],
    blocks: List[Dict[str, str]],
    page_image: Optional[str] = None
) -> HumanMessage:
```

## Custom LLM Provider Integration

The project uses LangChain to integrate LLM providers. You can add support for any LLM that has a LangChain integration.

### Adding a New Provider

Create a new file in `providers/`:

```python
# providers/my_provider.py
"""
My Custom LLM Provider

Description of the provider.
"""

from typing import Optional
from langchain_<provider_package> import Chat<Provider>

def my_provider(
    model: str = "default-model",
    base_url: str = "https://api.example.com",
    temperature: float = 0.2,
    reasoning: str = "none",
    cache: bool = True,
    response_format: Optional[type] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> Chat<Provider>:
    """
    Initialize and return Chat<Provider> instance.
    
    Args:
        model: Model name
        base_url: API endpoint URL
        temperature: Sampling temperature
        reasoning: Reasoning level
        cache: Enable LangChain caching
        response_format: Pydantic schema for structured output
        api_key: API key (if required)
        **kwargs: Additional provider-specific arguments
    
    Returns:
        Chat<Provider> configured instance
    """
    llm_kwargs = {
        "model": model,
        "cache": cache,
        "temperature": temperature,
        "base_url": base_url,
        "streaming": False,
        **kwargs
    }
    
    if api_key:
        llm_kwargs["api_key"] = api_key
    
    llm = Chat<Provider>(**llm_kwargs)
    
    if response_format:
        return llm.with_structured_output(response_format)
    
    return llm
```

### Registering the Provider in main.py

Update the model initialization section in `main.py`:

```python
# Add your provider import
if config.provider == "my_provider":
    from providers.my_provider import my_provider
    model = my_provider(
        model=config.model,
        base_url=config.base_url,
        temperature=config.temperature,
        reasoning=config.reasoning_effort,
        cache=config.enable_cache,
        response_format=BlockResponse,
        api_key=config.api_key
    )
```

### Adding CLI Support

Update `config/settings.py` to add the provider to CLI choices:

```python
parser.add_argument("-p", "--provider", type=str, 
    choices=["openai", "ollama", "my_provider"], 
    help="LLM provider")
```

### Requirements for Vision Support

If your provider needs to process images (recommended for Figma conversion):

1. Use a model with vision capability
2. Ensure the LangChain integration supports multi-modal input
3. Test with the image input format used in `build_block_message()`:

```python
content_parts = [
    {"type": "text", "text": "Desktop JSON:\n{...}"},
    {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
    }
]
message = HumanMessage(content=content_parts)
response = model.invoke([SYSTEM_PROMPT, message])
```

### Example: Anthropic Claude Provider

```python
# providers/anthropic.py
from typing import Optional
from langchain_anthropic import ChatAnthropic

def anthropic(
    model: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.2,
    cache: bool = True,
    response_format: Optional[type] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> ChatAnthropic:
    llm = ChatAnthropic(
        model=model,
        temperature=temperature,
        cache=cache,
        anthropic_api_key=api_key,
        **kwargs
    )
    
    if response_format:
        return llm.with_structured_output(response_format)
    
    return llm
```

### Testing Your Provider

```python
# Test basic invocation
from langchain_core.messages import HumanMessage, SystemMessage

model = my_provider(model="my-model", api_key="...")
response = model.invoke([
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Say hello in JSON: {\"greeting\": \"...\"}")
])
print(response)

# Test with image
from agents.build_block import build_block_message
json_data = {"pc": {"json": {...}, "image": "base64..."}}
message = build_block_message(json_data)
response = model.invoke([SYSTEM_PROMPT, message])
print(response.html_code)
```