# Input Data Loader (`load_data.py`)

This module recursively traverses the input directory to load Figma JSON exports and reference images, assembling them into a unified format for the converter.

## Function: `load_data(root_dir)`
Recursively loads data from the specified root directory.

*   **Signature**: `(root_dir: Union[str, Path]) -> Dict[str, Any]`
*   **Returns**: A dictionary containing structured header, footer, and page data.

### Expected Directory Structure
```text
INPUT_DIR/
├── pc/
│   ├── header.json/header.jpg
│   ├── footer.json/footer.jpg
│   └── {page_name}/
│       ├── 1.json/1.jpg (Block)
│       └── page.jpg (Preview)
└── mobile/
    └── ...
```

### Output Structure
The function returns a dictionary with the following schema:
```python
{
    "header": {"pc": {...}, "mobile": {...}},
    "footer": {"pc": {...}, "mobile": {...}},
    "pages": {
        "{page_name}": {
            "blocks": [...],
            "pc_page_image": "...",
            "mobile_page_image": "..."
        }
    }
}
```