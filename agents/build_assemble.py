from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage


SYSTEM_PROMPT = SystemMessage(
    content="""You have generated HTML/CSS/JS for individual blocks.
Now assemble them into a single responsive HTML page.

IMPORTANT: Output ONLY valid JSON. No explanations, no markdown.

OUTPUT FORMAT (JSON):
{
  "html_code": "<!-- Complete HTML -->",
  "css_code": "/* Merged CSS */",
  "js_code": "// Merged JS"
}
"""
)

def build_assemble_message(
    header_result: Optional[Dict[str, str]],
    footer_result: Optional[Dict[str, str]],
    blocks: List[Dict[str, str]],
    page_image: Optional[str] = None
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
        page_image: Optional full page preview image (base64)
        
    Returns:
        HumanMessage with assembled content for LLM
    """
    content_parts = []
    
    if page_image:
        content_parts.append(f"FULL PAGE PREVIEW (base64):\ndata:image/jpeg;base64,{page_image}")
    
    if header_result:
        content_parts.append(f"HEADER HTML:\n{header_result.get('html', '')}")
        content_parts.append(f"HEADER CSS:\n{header_result.get('css', '')}")
        content_parts.append(f"HEADER JS:\n{header_result.get('js', '')}")
    
    for i, block in enumerate(blocks):
        content_parts.append(f"BLOCK {i+1} HTML:\n{block.get('html', '')}")
    
    if footer_result:
        content_parts.append(f"FOOTER HTML:\n{footer_result.get('html', '')}")
        content_parts.append(f"FOOTER CSS:\n{footer_result.get('css', '')}")
        content_parts.append(f"FOOTER JS:\n{footer_result.get('js', '')}")
    
    all_css = []
    all_js = []
    
    if header_result:
        all_css.append(header_result.get('css', ''))
        all_js.append(header_result.get('js', ''))
    
    for block in blocks:
        all_css.append(block.get('css', ''))
        all_js.append(block.get('js', ''))
    
    if footer_result:
        all_css.append(footer_result.get('css', ''))
        all_js.append(footer_result.get('js', ''))
    
    content_parts.append(f"\nALL CSS:\n" + "\n".join(all_css))
    content_parts.append(f"\nALL JS:\n" + "\n".join(all_js))
    
    return HumanMessage(content="\n\n".join([str(c) for c in content_parts]))