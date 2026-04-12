"""
Input Data Loader - Figma JSON and Image Parser

This module recursively traverses the input directory to load Figma JSON
exports and reference images. It handles the pc/mobile directory structure
and assembles the data into a unified format for the converter.

Expected directory structure:
    INPUT_DIR/
    ├── pc/
    │   ├── header.json, header.jpg
    │   ├── footer.json, footer.jpg
    │   └── page_name/
    │       ├── 1.json, 1.jpg
    │       └── page.jpg
    └── mobile/
        └── ...
"""

import json
import base64

from pathlib import Path
from typing import Dict, Any, Optional, Union


def load_data(root_dir: Union[str, Path]) -> Dict[str, Any]:
    """
    Recursively load Figma JSON exports and images from input directory.
    
    Processes the directory structure to extract:
    - Header and footer designs (from root pc/mobile directories)
    - Page blocks (from page subdirectories)
    - Reference images (JSON + JPG pairs)
    - Full page preview images
    
    Args:
        root_dir: Path to the input data directory
        
    Returns:
        Dict with structure:
        {
            "header": {"pc": {"json": ..., "image": ...}, "mobile": {...}},
            "footer": {...},
            "pages": {
                "page_name": {
                    "blocks": [{"pc": {...}, "mobile": {...}}, ...],
                    "page_image": "base64..."
                }
            }
        }
        
    Raises:
        FileNotFoundError: If root_dir doesn't exist or isn't a directory
    """
    root = Path(root_dir).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"⚠️ Directory not found: {root}")

    result = {
        "header": {},
        "footer": {},
        "pages": {}
    }

    def load_json(path: Path) -> Optional[Any]:
        if not path.is_file(): return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def load_image_base64(path: Path) -> Optional[str]:
        if not path.is_file(): return None
        try:
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except IOError:
            return None

    platforms = ["pc", "mobile"]

    for plat in platforms:
        plat_dir = root / plat
        if not plat_dir.is_dir():
            continue

        for section in ("header", "footer"):
            j_data = load_json(plat_dir / f"{section}.json")
            i_data = load_image_base64(plat_dir / f"{section}.jpg")

            entry = {}
            if j_data is not None:
                entry["json"] = j_data
            if i_data is not None:
                entry["image"] = i_data

            if entry:
                result[section][plat] = entry

    # {page_name: {num: {plat: {"json": ..., "image": ...}}}}
    pages_map: Dict[str, Dict[int, Dict[str, Dict[str, Any]]]] = {}

    for plat in platforms:
        plat_dir = root / plat
        if not plat_dir.is_dir():
            continue

        for page_dir in plat_dir.iterdir():
            if not page_dir.is_dir():
                continue
                
            page_name = page_dir.name
            pages_map.setdefault(page_name, {})

            for file in page_dir.iterdir():
                if file.suffix not in (".json", ".jpg"):
                    continue
                    
                try:
                    num = int(file.stem)
                except ValueError:
                    continue

                pages_map[page_name].setdefault(num, {}).setdefault(plat, {})

                if file.suffix == ".json":
                    val = load_json(file)
                    if val is not None:
                        pages_map[page_name][num][plat]["json"] = val
                elif file.suffix == ".jpg":
                    val = load_image_base64(file)
                    if val is not None:
                        pages_map[page_name][num][plat]["image"] = val

    for page_name in pages_map:
        page_list = []
        page_image = None
        
        plat_dir = root / "pc"
        if not plat_dir.is_dir():
            plat_dir = root / "mobile"
        
        page_dir = plat_dir / page_name if plat_dir.is_dir() else None
        if page_dir and page_dir.is_dir():
            page_image = (
                load_image_base64(page_dir / "page.jpg") or 
                load_image_base64(page_dir / "page.png")
            )
        
        for num in sorted(pages_map[page_name].keys()):
            entry = {}
            for plat in platforms:
                if plat in pages_map[page_name][num]:
                    entry[plat] = pages_map[page_name][num][plat]
            if entry:
                page_list.append(entry)
                
        if page_list:
            page_entry = {"blocks": page_list}
            if page_image:
                page_entry["page_image"] = page_image
            result["pages"][page_name] = page_entry

    return {k: v for k, v in result.items() if v}