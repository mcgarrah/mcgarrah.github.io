# PDF Text Extraction

## Approach

When extracting text from PDF files, always use a Python virtual environment.
Never install packages globally or with `--user`/`--break-system-packages`.

Use paths relative to the repo root so the commands work on both macOS and WSL2
(`$HOME` differs between environments — never hardcode it).

```bash
# From the mcgarrah.github.io repo root
python3 -m venv .venv
source .venv/bin/activate
pip install pypdf
python3 - <<'EOF' "path/to/file.pdf"
# (paste the inline script below, or use the heredoc form)
EOF
deactivate
```

## Inline Extraction Script

Copy this into a temporary file or run inline. Takes the PDF path as the first argument
and writes extracted text to stdout.

```python
#!/usr/bin/env python3
"""Extract text from a PDF and print to stdout.

Usage:
    python3 extract-pdf.py "relative/or/absolute/path/to/file.pdf"

Run from the repo root inside a .venv with pypdf installed:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install pypdf
    python3 extract-pdf.py "Google Gemini - Some Conversation.pdf"
    deactivate

Works on macOS and WSL2 — uses no hardcoded $HOME paths.
"""
import sys
from pathlib import Path
from pypdf import PdfReader

if len(sys.argv) < 2:
    print("Usage: extract-pdf.py <path-to-pdf>", file=sys.stderr)
    sys.exit(1)

pdf_path = Path(sys.argv[1])
if not pdf_path.exists():
    print(f"File not found: {pdf_path}", file=sys.stderr)
    sys.exit(1)

reader = PdfReader(pdf_path)
print(f"# Extracted from: {pdf_path.name}")
print(f"# Pages: {len(reader.pages)}")
print()
for i, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""
    print(f"=== PAGE {i} ===")
    print(text)
    print()
```

## When to Use

- Extracting content from saved AI conversation PDFs (e.g., Gemini, ChatGPT exports)
- Migrating PDF content into convenience markdown files in `_drafts/`
- Any time a PDF needs to be read before the file is deleted

## Notes

- `.venv/` is in `.gitignore` — never commit it
- `pypdf` is the maintained successor to `PyPDF2`; always use `pypdf`
- PDF text extraction is imperfect for chat exports — review output for garbled lines,
  missing code blocks, or merged paragraphs before using in markdown files
- Always use relative paths or `Path(sys.argv[1])` — never `$HOME` or hardcoded user paths
