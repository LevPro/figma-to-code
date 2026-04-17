from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage


SYSTEM_PROMPT = SystemMessage(
    content=(Path(__file__).parent.parent / "prompts" / "assemble_system.md").read_text(
        encoding="utf-8"
    )
)


def build_assemble_message(
    header_result: Optional[Dict[str, str]],
    footer_result: Optional[Dict[str, str]],
    blocks: List[Dict[str, str]],
    desktop_page_image: Optional[str] = None,
    mobile_page_image: Optional[str] = None,
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
        content_parts.append(
            {"type": "text", "text": f"HEADER block HTML:\n{header_result.get('html', '')}"}
        )
        content_parts.append(
            {"type": "text", "text": f"HEADER block CSS:\n{header_result.get('css', '')}"}
        )
        content_parts.append(
            {"type": "text", "text": f"HEADER block JS:\n{header_result.get('js', '')}"}
        )

    for i, block in enumerate(blocks):
        content_parts.append(
            {"type": "text", "text": f"BLOCK {i + 1} HTML:\n{block.get('html', '')}"}
        )
        content_parts.append(
            {"type": "text", "text": f"BLOCK {i + 1} CSS:\n{block.get('css', '')}"}
        )
        content_parts.append({"type": "text", "text": f"BLOCK {i + 1} JS:\n{block.get('js', '')}"})

    if footer_result:
        content_parts.append(
            {"type": "text", "text": f"FOOTER block HTML:\n{footer_result.get('html', '')}"}
        )
        content_parts.append(
            {"type": "text", "text": f"FOOTER block CSS:\n{footer_result.get('css', '')}"}
        )
        content_parts.append(
            {"type": "text", "text": f"FOOTER block JS:\n{footer_result.get('js', '')}"}
        )

    return HumanMessage(content=content_parts)
