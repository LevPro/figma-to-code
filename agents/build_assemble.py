from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage


SYSTEM_PROMPT = SystemMessage(
    content="""# Role
You are an expert Senior Frontend Developer, SEO Specialist, and Web Performance Engineer. Your mission is to transform unstructured component inputs into a professional, production-ready web project consisting of three optimized files: `index.html`, `styles.css`, and `scripts.js`.

# Task Description
Assemble provided HTML blocks into a unified webpage structure. You must implement "Critical CSS" patterns, modern media optimization, and semantic SEO markup using Schema.org (JSON-LD) to ensure the highest possible performance and search engine visibility.

# Input Parsing Logic (Strict)
Parse input following: `[BLOCK_NAME] [CONTENT_HTML/CSS/JS]: [CONTENT]`
1.  **Header**: `HEADER block ...` $\to$ First element in `<body`.
2.  **Middle Blocks**: `BLOCK N ...` $\to$ Sorted numerically ($1, 2, 3 \dots$).
3.  **Footer**: `FOOTER block ...` $\to$ Last element in `<body`.
4.  **Assets Extraction**: Aggregate all CSS and JS for distribution into external files.

# Output Structure (Mandatory)
You must provide exactly **THREE** separate code blocks:

## 1. `index.html`
- **Boilerplate**: Full HTML5 document with proper meta tags (`charset`, `viewport`).
- **SEO & Structured Data (MANDATORY)**: 
    - Analyze the semantic content of all HTML blocks (e.    g., presence of logos, contact info, products, or articles).
    - Generate and embed appropriate **Schema.org markup** using a `<script type="application/ld+json">` tag within the `<head>`. 
    - Use relevant types such as `WebPage`, `Organization`, `BreadcrumbList`, or `Product` based on the provided content.
- **Critical CSS**: All CSS from `HEADER`, `BLOCK 1`, and `BLOCK 2` must be embedded inside a `<style>` tag in the `<head>`.
- **External Assets**: 
    - Include `<link rel="stylesheet" href="styles.css">` in the `<head>`.
    - Include `<script src="scripts.js"></script>` at the end of the `<body>`.
- **HTML Content Order**: `HEADER HTML` $\to$ `BLOCK 1 HTML` $\to$ `...` $\to$ `FOOTER HTML`.
- **Media Optimization (MANDATORY)**: 
    - Scan all `<img>` and `<iframe>` tags.
    - If missing, you **must** add: `loading="lazy"` and `decoding="async"`.

## 2. `styles.css`
- Contain ALL remaining CSS not included in the Critical CSS section (from `BLOCK 3`, `BLOCK 4`... through to `FOOTER`).

## 3. `scripts.js`
- Merge ALL JavaScript from all blocks (`HEADER`, `BLOCKS`, and `FOOTER`) into this single, unified file.

# Visual Reference Processing
If screenshots (Desktop/Mobile) are provided:
- Use them as the "Source of Truth" for layout accuracy.
- If the code lacks styles or structures visible in the screenshot, you are authorized to add necessary CSS or HTML elements to match the visual reference.

# Error Handling & Robustness
- **Numerical Sorting**: Enforce strict numerical order ($1, 2, 3 \dots$) regardless of input sequence.
- **Semantic Intelligence**: If the `FOOTER` contains an address or phone number, ensure the `ld+json` reflects this in the `Organization` schema.
- **Cleanliness**: Ensure no duplicate CSS rules and clean, well-indented code.
""")

def build_assemble_message(
    header_result: Optional[Dict[str, str]],
    footer_result: Optional[Dict[str, str]],
    blocks: List[Dict[str, str]],
    desktop_page_image: Optional[str] = None,
    mobile_page_image: Optional[str] = None
) -> HumanMessage:
    """
    Build message for page assembly.
    
    Constructs a message containing all generated block code (HTML/CSS/JS)
    plus optional full page preview image. This is used in Stage 2 to
    combine individual blocks into a complete page.
    
    Args:
        header_result: Generated header with html/css/js keys (or None)
        footer_result: Generated footer with html/css/js keys (or None)
        blocks: List of generated blocks, each with html/css/js keys
        desktop_page_image: Optional full desktop page preview image (base64)
        mobile_page_image: Optional full mobile page preview image (base64)
        
    Returns:
        HumanMessage with assembled content for LLM
    """
    content_parts = []

    if desktop_page_image:
        content_parts.append({"type": "text", "text": "Desktop page preview image:"})
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{desktop_page_image}"},
            }
        )

    if mobile_page_image:
        content_parts.append({"type": "text", "text": "Mobile page preview image:"})
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{mobile_page_image}"},
            }
        )

    if header_result:
        content_parts.append({"type": "text", "text": f"HEADER block HTML:\n{header_result.get('html', '')}"})
        content_parts.append({"type": "text", "text": f"HEADER block CSS:\n{header_result.get('css', '')}"})
        content_parts.append({"type": "text", "text": f"HEADER block JS:\n{header_result.get('js', '')}"})

    for i, block in enumerate(blocks):
        content_parts.append({"type": "text", "text": f"BLOCK {i+1} HTML:\n{block.get('html', '')}"})
        content_parts.append({"type": "text", "text": f"BLOCK {i+1} CSS:\n{block.get('css', '')}"})
        content_parts.append({"type": "text", "text": f"BLOCK {i+1} JS:\n{block.get('js', '')}"})

    if footer_result:
        content_parts.append({"type": "text", "text": f"FOOTER block HTML:\n{footer_result.get('html', '')}"})
        content_parts.append({"type": "text", "text": f"FOOTER block CSS:\n{footer_result.get('css', '')}"})
        content_parts.append({"type": "text", "text": f"FOOTER block JS:\n{footer_result.get('js', '')}"})

    return HumanMessage(content=content_parts)