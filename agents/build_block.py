import json
from pathlib import Path

from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from data.preprocess_figma import preprocess_json, PreprocessConfig

SYSTEM_PROMPT = SystemMessage(
    content=(Path(__file__).parent.parent / "prompts" / "block_system.md").read_text(
        encoding="utf-8"
    )
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
