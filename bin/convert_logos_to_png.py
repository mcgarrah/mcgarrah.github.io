#!/usr/bin/env python3
"""Convert SVG logos to PNG with transparent backgrounds for XeLaTeX.

XeLaTeX handles PNG with transparency well. This replaces the PDF
conversion approach with PNGs that preserve transparent backgrounds.

Output: assets/images/company-logos/latex-logos/
"""

from pathlib import Path
import cairosvg

LOGOS_DIR = Path("assets/images/company-logos")
OUTPUT_DIR = LOGOS_DIR / "latex-logos"
OUTPUT_DIR.mkdir(exist_ok=True)

# Render at 4x for crisp output at small sizes (logo displays at ~0.9cm)
RENDER_SIZE = 400  # pixels wide — gives plenty of resolution for 0.9cm print


def convert_svg_to_png(svg_path, png_path, unsafe=False):
    """Convert SVG to PNG with transparent background."""
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=RENDER_SIZE,
        unsafe=unsafe,
    )


def main():
    print("Converting SVG logos to PNG (transparent backgrounds)...")

    svg_files = sorted(LOGOS_DIR.glob("*.svg"))
    for svg in svg_files:
        png_name = svg.stem + ".png"
        png_path = OUTPUT_DIR / png_name

        # Skip if a hand-crafted PNG already exists at top level with same name
        # (e.g., akc-shield.png is already a cropped PNG, not from SVG)
        if (LOGOS_DIR / png_name).exists() and not svg.stem.startswith("nc-seal"):
            # Already have a PNG version — still convert SVG for consistency
            pass

        try:
            convert_svg_to_png(svg, png_path)
            size_kb = png_path.stat().st_size / 1024
            print(f"  {svg.name} → {png_name} ({size_kb:.1f} KB)")
        except Exception as e:
            # Try with unsafe=True for SVGs with XML entities
            try:
                convert_svg_to_png(svg, png_path, unsafe=True)
                size_kb = png_path.stat().st_size / 1024
                print(f"  {svg.name} → {png_name} ({size_kb:.1f} KB) [unsafe]")
            except Exception as e2:
                print(f"  FAILED: {svg.name} — {e2}")

    # Remove old PDF files that are no longer needed
    for pdf in OUTPUT_DIR.glob("*.pdf"):
        pdf.unlink()
        print(f"  Removed old: {pdf.name}")

    print(f"\nDone. All logos in {OUTPUT_DIR}/ are now PNG or JPG.")


if __name__ == "__main__":
    main()
