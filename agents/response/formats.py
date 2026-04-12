from pydantic import BaseModel

class BlockResponse(BaseModel):
    """Response schema for block generation."""
    html_code: str
    css_code: str
    js_code: str


class AssemblyResponse(BaseModel):
    """Response schema for page assembly."""
    html_code: str
    css_code: str
    js_code: str