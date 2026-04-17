# Pydantic Schema Models (`models.py`)

This module defines response schemas used with LangChain's `with_structured_output()` to enforce strict JSON compliance from LLMs, eliminating the need for regex parsing.

## Class: `BlockResponse`
Schema for **Stage 1** (Single Block Generation).

*   **Fields**:
    *   `html_code` (str): HTML markup without `<html>`/`<body>` wrappers.
    *   `css_code` (str): Mobile-first CSS styles, no global resets.
    *   `js_code` (str): ES6 JavaScript logic or `"// No JS required"`.

## Class: `AssemblyResponse`
Schema for **Stage 2** (Page Assembly).

*   **Fields**:
    *   `html_code` (str): Complete HTML document including DOCTYPE and head/body tags.
    *   `css_code` (str): Merged CSS with deduplicated imports and consolidated media queries.
    *   `js_code` (str): Combined JavaScript wrapped in `DOMContentLoaded`.

## Usage Example
```python
from data.models import BlockResponse
response: BlockResponse = model.invoke(messages)
html = response.html_code  # Type-safe access
```