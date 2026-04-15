"""
markitdown adapter — wraps Microsoft markitdown lib.

Returns plain Markdown body (no frontmatter — caller adds it).
Singleton converter to avoid re-initialising on every call.

Supported input formats (MARKITDOWN_FORMATS in convert_manual.py):
    .docx  .pdf  .pptx  .xlsx  .html  .epub  .zip
"""
import re
from pathlib import Path

from markitdown import MarkItDown

_converter: MarkItDown | None = None


def get_converter() -> MarkItDown:
    global _converter
    if _converter is None:
        # enable_plugins=False: skip LLM image-description plugin (no API key yet)
        # Activate via env OPENAI_API_KEY after PART 05.
        _converter = MarkItDown(enable_plugins=False)
    return _converter


def _clean_xlsx_markdown(text: str) -> str:
    """Post-process XLSX-sourced markdown to strip pandas artefacts.

    pandas represents merged/empty cells as ``NaN`` and auto-names unnamed
    columns as ``Unnamed: N``. Both create noise in LLM context.

    Rules applied (in order):
    1. Replace every ``| NaN |`` cell (and leading/trailing variants) with ``|  |``
    2. Drop table rows where every non-pipe token is empty / NaN → blank row noise
    3. Replace ``Unnamed: N`` header tokens with empty string
    4. Collapse 3+ consecutive blank lines → 2 blank lines (cosmetic)
    """
    # 1. Normalise NaN cells — handles "| NaN |", "|NaN|", "| nan |" etc.
    text = re.sub(r"\|\s*[Nn]a[Nn]\s*(?=\|)", "|  ", text)

    # 2. Drop rows that are all-empty after step 1
    #    A "table row" is a line starting with | that contains only pipes, spaces, dashes
    def _is_empty_table_row(line: str) -> bool:
        if not line.startswith("|"):
            return False
        cells = [c.strip() for c in line.split("|") if c.strip()]
        return all(c in ("", "-", "---", "--") for c in cells)

    lines = text.split("\n")
    lines = [l for l in lines if not _is_empty_table_row(l)]
    text = "\n".join(lines)

    # 3. Strip "Unnamed: N" column headers
    text = re.sub(r"Unnamed:\s*\d+", "", text)

    # 4. Cosmetic: collapse excess blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def convert_to_markdown(file_path: Path) -> str:
    """Convert *file_path* to Markdown using markitdown.

    For XLSX files, runs ``_clean_xlsx_markdown()`` automatically.

    Returns:
        Plain Markdown string (no YAML frontmatter).

    Raises:
        ValueError: if markitdown returns empty content.
    """
    result = get_converter().convert(str(file_path))
    text = result.text_content or ""

    if file_path.suffix.lower() == ".xlsx":
        text = _clean_xlsx_markdown(text)

    if not text.strip():
        raise ValueError(f"markitdown returned empty content for {file_path.name}")

    return text
