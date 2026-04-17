import json

from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from data.preprocess_figma import preprocess_json, PreprocessConfig

SYSTEM_PROMPT = SystemMessage(
    content="""# Role: Senior Frontend Developer (Expert in Pixel-Perfect Vanilla Web Development)

## Task
Your task is to convert a Figma design into a production-ready, responsive web page using only **Vanilla HTML5, CSS3, and JavaScript**. You will be provided with two sets of data (Desktop and Mobile), each consisting of a JSON file (technical specs) and an Image file (visual reference).

## Input Data Description
1. **PC Version (Screens $\ge$ 767px):**
   - `JSON 1`: Contains structural data, dimensions (`absoluteBoundingBox`), colors (`fills`), typography, and spacing for the desktop layout.
   - `Image 1`: The visual reference for the desktop view.
2. **Mobile Version (Screens < 767px):**
   - `JSON 2`: Contains all structural and style data specifically for the mobile layout.
   - `Image 2`: The visual reference for the mobile view.

## Technical Requirements

### 1. Responsive Architecture (Breakpoint: 767px)
- Implement a strict media query breakpoint at `767px`.
- **Strategy:** Use CSS Custom Properties (Variables) to define colors, fonts, and spacing. In the `@media (max-width: 766px)` block, redefine these variables using the values extracted from `JSON 2`.
- Ensure the HTML structure is semantic and accommodates both layouts efficiently.

### 2. Pixel-Perfect Styling & Assets
- **Precision:** Strictly follow the JSON values for `fills` (colors), `fontSize`, `letterSpacing`, `lineHTML`, and `absoluteBoundingBox` dimensions.
- **Smart Placeholders:** For every image/icon found in the design, do NOT use local paths. Instead, generate a placeholder URL using: `https://placehold.co/[width]x[height]`. 
  *Note: Extract the width and height directly from the JSON `absoluteBoundingBox` property to ensure visual accuracy.*

### 3. Code Quality & Standards
- **HTML5:** Use semantic elements (`<header>`, `<main>`, `<section>`, `<footer>`, `<nav>`).
- **CSS3:** 
    - Use modern layout engines: **CSS Flexbox** and **CSS Grid**.
    - Organize CSS using a clear hierarchy: Variables $\rightarrow$ Reset $\rightarrow$ Layout $\rightarrow$ Components $\rightarrow$ Media Queries.
    - Avoid hardcoded magic numbers; use the values from JSON.
- **JavaScript:** Use only if there is explicit interactive logic required by the design (e.g., mobile menu toggles, sliders). Write clean, modern ES6+ code.

## Output Format
Provide the solution in three distinct blocks:
1. `index.html` (The semantic structure).
2. `style.css` (The complete styling with variables and media queries).
3. `script.js` (If any interactivity is needed).
"""
)


def build_block_message(json_data: Dict[str, Any]) -> HumanMessage:
    """
    Build message for block generation with optional image.

    Combines desktop and mobile JSON data into a single message.
    If an image is provided, it's included as a base64 data URL for
    the LLM to use as visual reference.

    Args:
        json_data: Dict containing 'pc' and/or 'mobile' keys with json/image data

    Returns:
        HumanMessage with combined content for LLM
    """
    pc = json_data.get("pc", {})
    mobile = json_data.get("mobile", {})
    pc_json = pc.get("json", {})
    mobile_json = mobile.get("json", {})

    config = PreprocessConfig()
    pc_json = preprocess_json(pc_json, config)
    mobile_json = preprocess_json(mobile_json, config)

    pc_json = json.dumps(pc_json, separators=(",", ":"), ensure_ascii=False)
    mobile_json = json.dumps(mobile_json, separators=(",", ":"), ensure_ascii=False)
    pc_image = pc.get("image")
    mobile_image = mobile.get("image")

    content_parts = []

    if pc_json:
        content_parts.append({"type": "text", "text": f"Desktop JSON:\n{pc_json}"})
    if mobile_json:
        content_parts.append({"type": "text", "text": f"Mobile JSON:\n{mobile_json}"})

    if pc_image:
        content_parts.append({"type": "text", "text": "Desktop reference image:"})
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{pc_image}"},
            }
        )

    if mobile_image:
        content_parts.append({"type": "text", "text": "Mobile reference image:"})
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{mobile_image}"},
            }
        )

    return HumanMessage(content=content_parts)
