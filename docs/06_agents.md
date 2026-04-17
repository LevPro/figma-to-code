### 5. Agents & Providers Documentation

This section documents the logic for constructing LLM messages and system prompts for both generation stages.

## System Prompts
*   **Block Generation (`SYSTEM_PROMPT` in `build_block.py`)**: Instructs the model to convert Figma JSON nodes (Frames, Text, Rectangles) into clean HTML/CSS/JS using mobile-first principles.
*   **Page Assembly (`SYSTEM_PROMPT` in `build_assemble.py`)**: Instructs the model to merge blocks, handle style collisions, and consolidate media queries at 993px breakpoint.

## Message Builders

### `build_block_message(json_data)`
Constructs a `HumanMessage` for single block generation.
*   **Input**: Figma JSON (PC & Mobile) + optional reference images.
*   **Output**: Structured message containing text descriptions and Base64 image URLs.

### `build_assemble_message(...)`
Constructs a `HumanMessage` for page assembly.
*   **Input**: Header, Footer, Blocks (HTML/CSS/JS strings), Page Previews.
*   **Output**: Structured message containing all generated code segments ready for merging logic.