# Core Pipeline Methods (`main.py`)

This document details the functions responsible for orchestrating the conversion pipeline.

## Functions

### `generate_block`
Generates HTML/CSS/JS for a single design block using an LLM with retry logic.
- **Signature**: `(model, json_data: Dict[str, Dict[str, str]], block_name: str, config: Config) -> Dict[str, str]`
- **Retry Logic**: Automatically retries up to `config.max_retries` times on failure.

### `assemble_page`
Combines individual block results into a complete HTML page (Stage 2).
- **Signature**: `(model, page_name, header_result, footer_result, blocks, pc_image, mobile_image, config) -> Dict[str, str]`
- **Validation**: Checks for empty HTML/CSS strings before returning.

### `save_page` & `save_block`
Writes generated files to disk with path traversal sanitization.
- **Return Type**: `bool` indicating success or failure.

### `block_exist`
Checks if a block has already been generated to enable caching/reuse during re-runs.
