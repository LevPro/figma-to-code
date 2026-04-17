"""
Image compression and optimization utilities.

Reduces image size before sending to LLM to minimize token usage
and improve response times while maintaining visual quality.
"""

import base64
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image


def compress_image_base64(
    image_base64: str,
    quality: int = 85,
    max_dimension: int = 2048
) -> Tuple[str, int]:
    """
    Compress a base64-encoded JPEG image.
    
    Args:
        image_base64: Base64-encoded image string
        quality: JPEG quality (1-100, higher = better quality, larger size)
        max_dimension: Maximum width/height in pixels (image will be resized if larger)
        
    Returns:
        Tuple of (compressed_base64_string, size_reduction_percentage)
    """
    try:
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_base64)
        original_size = len(image_bytes)
        
        # Open image with PIL
        img = Image.open(BytesIO(image_bytes))
        
        # Convert RGBA to RGB if necessary (JPEG doesn't support alpha)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if image exceeds maximum dimension
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            ratio = min(max_dimension / width, max_dimension / height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Compress image
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
        compressed_bytes = output.getvalue()
        
        # Calculate size reduction
        reduction = ((original_size - len(compressed_bytes)) / original_size) * 100
        
        # Encode back to base64
        compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
        
        return compressed_base64, max(0, reduction)
        
    except Exception as e:
        # If compression fails, return original image
        print(f"⚠️ Image compression failed: {e}")
        return image_base64, 0


def get_image_dimensions(image_base64: str) -> Optional[Tuple[int, int]]:
    """
    Get dimensions of a base64-encoded image.
    
    Args:
        image_base64: Base64-encoded image string
        
    Returns:
        Tuple of (width, height) or None if unable to read
    """
    try:
        image_bytes = base64.b64decode(image_base64)
        img = Image.open(BytesIO(image_bytes))
        return img.size
    except Exception:
        return None


def estimate_token_count(image_base64: str) -> int:
    """
    Estimate token count for an image based on its dimensions.
    
    Uses OpenAI's vision pricing model as reference:
    - Low resolution (512x512): ~85 tokens
    - High resolution: calculated based on grid cells
    
    Args:
        image_base64: Base64-encoded image string
        
    Returns:
        Estimated token count
    """
    dimensions = get_image_dimensions(image_base64)
    if not dimensions:
        return 0
    
    width, height = dimensions
    
    # Simple estimation: smaller images use fewer tokens
    if width <= 512 and height <= 512:
        return 85
    
    # For larger images, estimate based on area
    # This is a rough approximation
    base_tokens = 85
    area_factor = (width * height) / (512 * 512)
    return int(base_tokens * area_factor)