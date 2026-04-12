"""
Figma to Code Converter - Main Entry Point

This module orchestrates the two-stage conversion pipeline:
1. Block Generation: Convert each design block to HTML/CSS/JS
2. Page Assembly: Combine blocks into complete pages

Usage:
    INPUT_DIR=./input OUTPUT_DIR=./output PROVIDER=openai API_KEY=... python main.py
"""

import logging
from pathlib import Path

from agents.build_assemble import build_assemble_message
from agents.build_block import build_block_message
from agents.build_block import SYSTEM_PROMPT as BLOCK_SYSTEM_PROMPT
from config.settings import Config, create_parser
from agents.response.formats import BlockResponse, AssemblyResponse
from data.load_data import load_data
from data.image import compress_image_base64


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def generate_block(
    model,
    json_data: Dict[str, Any],
    block_name: str,
    config: Config
) -> Dict[str, str]:
    """
    Generate HTML/CSS/JS for a single block with retry logic.
    
    Uses iterative retry with exponential backoff instead of recursion
    to avoid stack overflow risks.
    
    Args:
        model: LangChain-compatible LLM model
        json_data: Figma JSON data (pc and mobile versions)
        block_name: Identifier for logging purposes
        config: Configuration object
        
    Returns:
        Dict with keys: html, css, js
        
    Raises:
        RuntimeError: If all retry attempts are exhausted
    """

    # Apply image compression if enabled
    if config.compress_images and json_data.get("image"):
        compressed_image, reduction = compress_image_base64(
            json_data.get("image"),
            quality=config.image_quality,
            max_dimension=config.max_image_dimension
        )
        if reduction > 0:
            logger.debug(f"Compressed image for {block_name}: {reduction:.1f}% reduction")
        json_data["image"] = compressed_image

    message = build_block_message(json_data)
    
    current_retry = 0
    last_error = None
    
    while current_retry < config.max_retries:
        try:
            response = model.invoke([BLOCK_SYSTEM_PROMPT, message])
            
            result = {
                "html": response.html_code,
                "css": response.css_code,
                "js": response.js_code
            }
            
            logger.info(f"Generated: {block_name}")
            return result
            
        except Exception as e:
            last_error = e
            current_retry += 1
            
            if current_retry < config.max_retries:
                logger.warning(f"Retry {current_retry}/{config.max_retries} for {block_name} ")
            else:
                logger.error(f"Failed: {block_name} after {config.max_retries} attempts")
    
    raise RuntimeError(f"Failed to generate {block_name} after {config.max_retries} attempts") from last_error

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
    Assemble a complete page from header, blocks, footer using AI.
    
    Stage 2 of the pipeline: Takes individually generated blocks and
    combines them into a valid HTML document with merged CSS/JS.
    
    Args:
        model: LangChain-compatible LLM model
        page_name: Page identifier for logging
        header_result: Generated header HTML/CSS/JS or None
        footer_result: Generated footer HTML/CSS/JS or None
        blocks: List of generated block results
        page_image: Full page preview image (base64) or None
        config: Configuration object
        
    Returns:
        Dict with keys: html, css, js (complete page)
        
    Raises:
        RuntimeError: If assembly fails
    """

    # Apply image compression if enabled
    if config.compress_images and page_image:
        compressed_image, reduction = compress_image_base64(
            page_image,
            quality=config.image_quality,
            max_dimension=config.max_image_dimension
        )
        if reduction > 0:
            logger.debug(f"Compressed image for {page_name}: {reduction:.1f}% reduction")
        page_image = compressed_image
    
    message = build_assemble_message(header_result, footer_result, blocks, page_image)
    
    try:
        response = model.invoke([AssemblyResponse, message])
        
        result = {
                "html": response.html_code,
                "css": response.css_code,
                "js": response.js_code
            }
        
        if not result.get("html"):
            raise ValueError(f"Empty HTML result for {page_name}")
        
        if not result.get("css"):
            raise ValueError(f"Empty CSS result for {page_name}")
        
        print(f"Assembled: {page_name}")
        return result
        
    except Exception as e:
        raise RuntimeError(f"Failed to assemble page {page_name}") from e


async def save_page(output_dir: Path, page_name: str, html: str, css: str, js: str) -> bool:
    """
    Save page files (HTML, CSS, JS) to output directory.
    
    Creates a subdirectory for each page and writes three files:
    - index.html: Complete HTML document
    - styles.css: Merged CSS from all blocks
    - script.js: Combined JavaScript
    
    Args:
        output_dir: Root output directory path
        page_name: Name of the page (used as subdirectory name)
        html: Complete HTML content
        css: Merged CSS content
        js: Combined JavaScript content
        
    Returns:
        True if saved successfully, False otherwise
    """
    
    try:
        # Sanitize page name to prevent path traversal
        safe_page_name = Path(page_name).name
        if not safe_page_name or safe_page_name.startswith('.'):
            logger.error(f"Invalid page name: {page_name}")
            return False
        
        page_dir = output_dir / safe_page_name
        page_dir.mkdir(parents=True, exist_ok=True)
        
        async with open(page_dir / "index.html", "w", encoding="utf-8") as f:
            await f.write(html)
        
        async with open(page_dir / "styles.css", "w", encoding="utf-8") as f:
            await f.write(css)
        
        async with open(page_dir / "script.js", "w", encoding="utf-8") as f:
            await f.write(js)
        
        logger.info(f"Saved: {page_name}")
        return True
        
    except IOError as e:
        logger.error(f"Failed to save {page_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving {page_name}: {e}")
        return False

def main():
    """
    Main entry point - orchestrates the complete conversion pipeline.
    
    Pipeline stages:
    1. Parse CLI arguments and load configuration from environment variables
    2. Validate configuration
    3. Initialize LLM model based on provider
    4. Load input data (Figma JSON + images)
    5. Stage 1: Generate all blocks with concurrency limiting
    6. Stage 2: Assemble each page from blocks
    7. Save output files
    8. Generate conversion report
    
    CLI arguments (take precedence over environment variables):
    -i/--input-dir, -o/--output-dir, -p/--provider, -m/--model, etc.
    
    Environment variables:
    - INPUT_DIR: Path to input data directory
    - OUTPUT_DIR: Path to output directory  
    - PROVIDER: LLM provider (openai or ollama)
    
    Environment variables (optional):
    - API_KEY: For OpenAI provider
    - MODEL: Model name
    - BASE_URL: Custom API endpoint
    - TEMPERATURE: LLM temperature
    - COMPRESS_IMAGES: Enable image compression
    """
    
    # Parse CLI arguments and load configuration
    parser = create_parser()
    args = parser.parse_args()
    config = Config.from_args(args)
    
    # Validate required settings
    if not config.input_dir:
        logger.error("No input directory specified (INPUT_DIR)")
        return
    
    if not config.output_dir:
        logger.error("No output directory specified (OUTPUT_DIR)")
        return
    
    if not config.provider:
        logger.error("No provider specified (PROVIDER)")
        return
    
    # Validate configuration
    validation_errors = config.validate()
    if validation_errors:
        for error in validation_errors:
            logger.error(f"Configuration error: {error}")
        return
    
    # Log configuration (hide sensitive data)
    logger.info(f"Configuration: provider={config.provider}, model={config.model}, cache={config.enable_cache}")
    
    # Initialize LLM model based on configured provider
    model = None
    if config.provider == "openai":
        from providers.openai import openai
        model = openai(
            apiKey=config.api_key,
            model=config.model,
            base_url=config.base_url,
            temperature=config.temperature,
            reasoning=config.reasoning_effort,
            cache=config.enable_cache,
            response_format=BlockResponse
        )
    elif config.provider == "ollama":
        from providers.ollama import ollama
        model = ollama(
            model=config.model,
            base_url=config.base_url,
            temperature=config.temperature,
            reasoning=config.reasoning_effort,
            cache=config.enable_cache,
            response_format=BlockResponse
        )
    
    if not model:
        logger.error("Failed to initialize model")
        return
    
    # Load design data from input directory
    logger.info(f"Loading data from: {config.input_dir}")
    try:
        data = load_data(str(config.input_dir))
    except FileNotFoundError as e:
        logger.error(f"Input directory not found: {e}")
        return
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return
    
    logger.info(f"Loaded: header={'yes' if data.get('header') else 'no'}, "
                f"footer={'yes' if data.get('footer') else 'no'}, "
                f"pages={list(data.get('pages', {}).keys())}")
    
    # Validate input limits
    if len(data.get("pages", {})) > config.max_pages:
        logger.warning(f"Number of pages ({len(data['pages'])}) exceeds limit ({config.max_pages})")
    
    # Stage 1: Generate all design blocks
    # This creates HTML/CSS/JS for header, footer, and each page section
    logger.info("\n=== Stage 1: Generate all design blocks ===")
    
    header = generate_block(model, data.get('header'), 'header', config) # header
    footer = generate_block(model, data.get('footer'), 'footer', config) # footer

    result = {}

    for name, page_data in data.get("pages").items():
        result[name] = []
        for i, block in enumerate(page_data.get("blocks")):
            response = generate_block(model, block.get('pc'), f"{name}_block_{i+1}", config) # section
            result[name].append({"blocks": response, "image": page_data.get("page_image")})

    # Stage 2: Assemble each page from generated blocks
    # Combines blocks into complete HTML documents with merged CSS/JS
    logger.info("\n=== Stage 2: Assemble each page from generated blocks ===")
    
    saved_count = 0
    failed_count = 0

    output_path = Path(config.output_dir)

    for page_name, page_data in result.items():
        response = assemble_page(model, page_name, header, footer, page_data.get("blocks"), page_data.get("image"), config)

        success = save_page(output_path, page_name, response.get("html"), response.get("css"), response.get("js"))
        
        if success:
            saved_count += 1
        else:
            failed_count += 1
    
    # Summary
    logger.info(f"\n=== Done ===")
    logger.info(f"Successfully saved: {saved_count} pages")
    if failed_count > 0:
        logger.warning(f"Failed to save: {failed_count} pages")


if __name__ == "__main__":
    main()