"""
Pydantic Models for LLM Structured Output

Defines response schemas for block generation and page assembly.
These models are used with LangChain's with_structured_output() to
enforce strict JSON output from LLMs, eliminating regex-based parsing.
"""

from pydantic import BaseModel, Field


class BlockResponse(BaseModel):
    """Response schema for single block generation (Stage 1)."""

    html_code: str = Field(
        description="HTML markup for the block. Use semantic HTML5 tags. "
        "No <html>, <body>, <head>, <style>, <script> wrappers."
    )
    css_code: str = Field(
        description="CSS styles for the block. Mobile-first, rem units, "
        "clamp() for fluid typography. No resets or global styles."
    )
    js_code: str = Field(
        description="JavaScript for the block. ES6 syntax, addEventListener. "
        "Return '// No JS required' if the block is static."
    )


class AssemblyResponse(BaseModel):
    """Response schema for page assembly (Stage 2)."""

    html_code: str = Field(
        description="Complete HTML page with DOCTYPE, html, head, body tags. "
        "Blocks merged in order: header -> blocks -> footer."
    )
    css_code: str = Field(
        description="Merged CSS from all blocks. Duplicate @import/@font-face "
        "removed. Base styles -> block styles -> media queries."
    )
    js_code: str = Field(
        description="Merged JS wrapped in DOMContentLoaded listener. "
        "Function names prefixed to avoid collisions. try/catch per block."
    )
