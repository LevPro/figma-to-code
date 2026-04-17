# Image Utilities (`image.py`)

This module contains utilities for compressing and optimizing images before sending them to the LLM, reducing token usage and improving response times.

## Functions

### `compress_image_base64(image_base64, quality, max_dimension)`
Compresses a Base64-encoded JPEG image using PIL.

*   **Parameters**:
    *   `image_base64` (str): Input image string.
    *   `quality` (int): JPEG quality (1–100). Default: 85.
    *   `max_dimension` (int): Maximum pixel dimension. Default: 2048px.
*   **Returns**: Tuple `(compressed_base64_string, reduction_percentage)`.
*   **Logic**: Converts RGBA to RGB if needed, resizes using LANCZOS filter, and saves as optimized JPEG.

### `get_image_dimensions(image_base64)`
Extracts pixel width and height from a Base64 image string.

*   **Returns**: Tuple `(width, height)` or `None` on failure.

### `estimate_token_count(image_base64)`
Estimates the token cost for sending an image to a vision model (e.g., GPT-4o).

*   **Logic**: Uses OpenAI's pricing model as reference (512x512px ≈ 85 tokens), scaling by area.
