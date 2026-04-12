import json

from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

SYSTEM_PROMPT = SystemMessage(
    content="""You are an expert frontend developer converting Figma JSON exports to HTML/CSS/JS.

INPUT:
- JSON data from Figma (desktop and mobile versions)
- Reference image of the block design

The JSON contains structured design data (layers, styles, dimensions, colors, typography).
Use the reference image to verify accuracy and fill gaps.

TASK:
Generate HTML/CSS/JS for this SINGLE BLOCK ONLY.
- NO wrapper elements (<html>, <body>, <head>)
- Just the block content
- Responsive: mobile default, desktop @media (min-width: 993px)

CONSTRAINTS:
- Semantic HTML5, CSS Grid/Flex, rem units (1rem=16px), clamp()
- Use descriptive CSS class names based on block purpose
- JS: ES6, camelCase, addEventListener, try/catch

IMPORTANT: Output ONLY valid JSON. No explanations, no markdown.

OUTPUT FORMAT (JSON):
{
  "html_code": "<!-- Block HTML only -->",
  "css_code": "/* Block CSS only */",
  "js_code": "// Block JS only"
}

EXAMPLE:
{
  "html_code": "<header class=\"site-header\"><div class=\"container\"><a href=\"/\" class=\"logo\">Logo</a><nav class=\"nav\">...</nav></div></header>",
  "css_code": ".site-header { background: #fff; padding: 1rem 0; } .container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; } .logo { font-size: 1.5rem; font-weight: bold; } @media (min-width: 993px) { .site-header { padding: 1.5rem 0; } }",
  "js_code": "// No JS needed for static header"
}
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
    pc_json = json.dumps(pc.get("json"), separators=(',', ':'), ensure_ascii=False)
    mobile_json = json.dumps(mobile.get("json"), separators=(',', ':'), ensure_ascii=False)
    pc_image = pc.get("image")
    mobile_image = pc.get("image")

    content_parts = []

    if pc_json:
        content_parts.append({"type": "text", "text": f"Desktop JSON:\n{pc_json}"})
    if mobile_json:
        content_parts.append({"type": "text", "text": f"Mobile JSON:\n{mobile_json}"})

    if pc_image:
        content_parts.append({"type": "text", "text": "Desktop image:"})
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{pc_image}"},
            }
        )

    if mobile_image:
        content_parts.append({"type": "text", "text": "Mobile image:"})
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{pc_image}"},
            }
        )

    return HumanMessage(content=content_parts)
