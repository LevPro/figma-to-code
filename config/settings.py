"""
Configuration Management for Figma-to-Code Converter

Centralized configuration with sensible defaults and environment variable overrides.
Eliminates magic numbers and provides type-safe configuration access.
Supports both environment variables and CLI arguments (CLI takes precedence).
"""

import os
import argparse
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Figma to Code Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input-dir ./input --output-dir ./output --provider openai
  python main.py -i ./input -o ./output -p ollama --model llama3
  python main.py --api-key sk-xxx --temperature 0.5

Environment variables can also be used (CLI arguments take precedence):
  INPUT_DIR=./input OUTPUT_DIR=./output PROVIDER=openai python main.py
"""
    )
    
    parser.add_argument("-i", "--input-dir", type=str, help="Input directory path")
    parser.add_argument("-o", "--output-dir", type=str, help="Output directory path")
    parser.add_argument("-p", "--provider", type=str, choices=["openai", "ollama"], help="LLM provider")
    parser.add_argument("-m", "--model", type=str, help="Model name")
    parser.add_argument("--base-url", type=str, help="Custom API endpoint")
    parser.add_argument("--api-key", type=str, help="API key for OpenAI")
    parser.add_argument("-t", "--temperature", type=float, help="LLM temperature (0-2)")
    parser.add_argument("--reasoning", dest="reasoning", type=str, choices=["none", "low", "medium", "high"], help="Reasoning level")
    parser.add_argument("--max-retries", type=int, help="Maximum retry attempts")
    parser.add_argument("--compress-images", dest="compress_images", action=argparse.BooleanOptionalAction, help="Enable image compression")
    parser.add_argument("--image-quality", type=int, help="JPEG quality (1-100)")
    parser.add_argument("--cache", dest="enable_cache", action=argparse.BooleanOptionalAction, help="Enable LLM caching")
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Logging level")
    parser.add_argument("--hide-api-keys", dest="hide_api_keys", action=argparse.BooleanOptionalAction, help="Mask API keys in logs")
    
    return parser


@dataclass
class Config:
    """
    Centralized configuration container.
    
    All values can be set via environment variables or passed directly.
    Environment variables take precedence over defaults.
    """
    
    # Directory paths
    input_dir: Optional[Path] = None
    output_dir: Optional[Path] = None
    
    # LLM Provider settings
    provider: str = "openai"  # openai or ollama
    model: str = "gpt-5-nano"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.1
    reasoning_effort: bool = True
    
    # Retry and concurrency settings
    max_retries: int = 2
    retry_delay_base: float = 1.0  # Base delay for exponential backoff (seconds)
    retry_delay_max: float = 30.0  # Maximum delay between retries (seconds)
    
    # Input validation limits
    max_file_size_mb: int = 50  # Maximum input file size
    max_json_depth: int = 20  # Maximum JSON nesting depth
    max_pages: int = 50  # Maximum number of pages per project
    max_blocks_per_page: int = 100  # Maximum blocks per page
    
    # Image processing
    compress_images: bool = True
    image_quality: int = 85  # JPEG quality 1-100
    max_image_dimension: int = 2048  # Resize images larger than this
    
    # LLM caching
    enable_cache: bool = True
    
    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    hide_api_keys: bool = True  # Mask API keys in logs
    
    # Output settings
    save_reports: bool = True
    report_format: str = "json"  # json or text
    
    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Config":
        """Create configuration from CLI arguments with env var defaults."""
        config = cls.from_env()
        
        if args.input_dir is not None:
            config.input_dir = Path(args.input_dir)
        if args.output_dir is not None:
            config.output_dir = Path(args.output_dir)
        if args.provider is not None:
            config.provider = args.provider.lower()
        if args.model is not None:
            config.model = args.model
        if args.base_url is not None:
            config.base_url = args.base_url
        if args.api_key is not None:
            config.api_key = args.api_key
        if args.temperature is not None:
            config.temperature = args.temperature
        if args.reasoning is not None:
            config.reasoning_effort = args.reasoning
        if args.max_retries is not None:
            config.max_retries = args.max_retries
        if args.compress_images is not None:
            config.compress_images = args.compress_images
        if args.image_quality is not None:
            config.image_quality = args.image_quality
        if args.enable_cache is not None:
            config.enable_cache = args.enable_cache
        if args.log_level is not None:
            config.log_level = args.log_level.upper()
        if args.hide_api_keys is not None:
            config.hide_api_keys = args.hide_api_keys
        
        return config
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables with defaults.
        
        Environment variables:
        - INPUT_DIR, OUTPUT_DIR: Directory paths
        - PROVIDER: LLM provider (openai/ollama)
        - MODEL: Model name
        - BASE_URL: Custom API endpoint
        - API_KEY: API key for OpenAI
        - TEMPERATURE: LLM temperature
        - REASONING_EFFORT: Enable reasoning (true/false)
        - MAX_RETRIES: Maximum retry attempts
        - COMPRESS_IMAGES: Enable image compression (true/false)
        - LOG_LEVEL: Logging level
        - HIDE_API_KEYS: Mask API keys in logs (true/false)
        """
        config = cls()
        
        # Directory paths
        if env_val := os.getenv("INPUT_DIR"):
            config.input_dir = Path(env_val)
        if env_val := os.getenv("OUTPUT_DIR"):
            config.output_dir = Path(env_val)
        
        # LLM settings
        if env_val := os.getenv("PROVIDER"):
            config.provider = env_val.lower()
        if env_val := os.getenv("MODEL"):
            config.model = env_val
        if env_val := os.getenv("BASE_URL"):
            config.base_url = env_val
        if env_val := os.getenv("API_KEY"):
            config.api_key = env_val
        if env_val := os.getenv("TEMPERATURE"):
            config.temperature = float(env_val)
        if env_val := os.getenv("REASONING_EFFORT"):
            config.reasoning_effort = env_val.lower() == "true"
        
        # Retry and concurrency
        if env_val := os.getenv("MAX_RETRIES"):
            config.max_retries = int(env_val)
        
        # Image processing
        if env_val := os.getenv("COMPRESS_IMAGES"):
            config.compress_images = env_val.lower() == "true"
        if env_val := os.getenv("IMAGE_QUALITY"):
            config.image_quality = int(env_val)
        
        # LLM caching
        if env_val := os.getenv("ENABLE_CACHE"):
            config.enable_cache = env_val.lower() == "true"
        
        # Logging
        if env_val := os.getenv("LOG_LEVEL"):
            config.log_level = env_val.upper()
        if env_val := os.getenv("HIDE_API_KEYS"):
            config.hide_api_keys = env_val.lower() == "true"
        
        return config
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of errors.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if self.input_dir and not self.input_dir.exists():
            errors.append(f"Input directory does not exist: {self.input_dir}")
        
        if self.output_dir and not self.output_dir.parent.exists():
            errors.append(f"Output directory parent does not exist: {self.output_dir}")
        
        if self.provider not in ("openai", "ollama"):
            errors.append(f"Invalid provider: {self.provider}. Must be 'openai' or 'ollama'")
        
        if self.provider == "openai" and not self.api_key:
            errors.append("API_KEY is required for OpenAI provider")
        
        if not 0 <= self.temperature <= 2:
            errors.append(f"Temperature must be between 0 and 2, got {self.temperature}")
        
        if self.max_retries < 0:
            errors.append(f"MAX_RETRIES must be non-negative, got {self.max_retries}")
        
        if not 1 <= self.image_quality <= 100:
            errors.append(f"IMAGE_QUALITY must be between 1 and 100, got {self.image_quality}")
        
        return errors
    
    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        if isinstance(self.input_dir, str):
            self.input_dir = Path(self.input_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)


# Global default configuration instance
default_config = Config.from_env()