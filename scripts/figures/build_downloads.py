#!/usr/bin/env python3
"""
Build script for generating downloadable ZIP files of figures.

Creates two ZIP archives:
1. generated-figures.zip - All programmatically generated figures (from output/)
2. hand-drawn-figures.zip - All hand-drawn figures (from images/hand-drawn/)

Each ZIP includes both PNG and SVG versions, plus a LICENSE.txt and README.txt.
"""

import os
import sys
import zipfile
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from paths import OUTPUT_FIGURES, OUTPUT_FIGURES_HAND_DRAWN, OUTPUT_DOWNLOADS

# License text
LICENSE_TEXT = """Creative Commons Attribution 4.0 International (CC BY 4.0)

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license,
  and indicate if changes were made.

Attribution: Zanichelli, Schons et al., State of Brain Emulation Report 2025

Full license text: https://creativecommons.org/licenses/by/4.0/legalcode
"""

def create_readme(figure_type: str, figure_count: int) -> str:
    """Generate README content for the ZIP file."""
    return f"""State of Brain Emulation Report 2025 - {figure_type} Figures
{'=' * 60}

This archive contains {figure_count} figures from the State of Brain Emulation Report 2025.

Contents:
- PNG files (150 DPI, suitable for web and presentations)
- SVG files (vector format, suitable for editing and high-resolution printing)

License: CC BY 4.0 (Creative Commons Attribution 4.0 International)
Attribution: Zanichelli, Schons et al., State of Brain Emulation Report 2025

For more information, visit the report website or see LICENSE.txt.

Generated: {datetime.now().strftime('%Y-%m-%d')}
"""


def collect_figure_pairs(directory: Path, recursive: bool = True) -> list:
    """
    Collect PNG/SVG pairs from a directory.
    Returns list of tuples: (base_name, png_path, svg_path, relative_path)
    """
    pairs = []

    if not directory.exists():
        print(f"  Warning: Directory does not exist: {directory}")
        return pairs

    # Find all PNG files
    pattern = "**/*.png" if recursive else "*.png"
    for png_path in directory.glob(pattern):
        # Skip .DS_Store and other hidden files
        if png_path.name.startswith('.'):
            continue

        svg_path = png_path.with_suffix('.svg')

        # Calculate relative path within the directory
        rel_path = png_path.relative_to(directory).parent
        base_name = png_path.stem

        if svg_path.exists():
            pairs.append((base_name, png_path, svg_path, rel_path))
        else:
            # Include PNG even without SVG
            pairs.append((base_name, png_path, None, rel_path))
            print(f"  Warning: No SVG found for {png_path.name}")

    return pairs


def create_zip(output_path: Path, figure_pairs: list, figure_type: str):
    """Create a ZIP file with figures, license, and readme."""

    # Ensure downloads directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add figures
        for base_name, png_path, svg_path, rel_path in figure_pairs:
            # Build archive path (preserve subdirectory structure)
            if rel_path and str(rel_path) != '.':
                archive_base = f"figures/{rel_path}/{base_name}"
            else:
                archive_base = f"figures/{base_name}"

            # Add PNG
            zf.write(png_path, f"{archive_base}.png")

            # Add SVG if exists
            if svg_path and svg_path.exists():
                zf.write(svg_path, f"{archive_base}.svg")

        # Add LICENSE.txt
        zf.writestr("LICENSE.txt", LICENSE_TEXT)

        # Add README.txt
        readme_content = create_readme(figure_type, len(figure_pairs))
        zf.writestr("README.txt", readme_content)

    return output_path


def build_generated_figures_zip():
    """Build ZIP for generated figures."""
    print("Building generated-figures.zip...")

    pairs = collect_figure_pairs(OUTPUT_FIGURES, recursive=True)

    if not pairs:
        print("  No generated figures found!")
        return None

    print(f"  Found {len(pairs)} figure pairs")

    output_path = OUTPUT_DOWNLOADS / "generated-figures.zip"
    create_zip(output_path, pairs, "Generated")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Created: {output_path} ({size_mb:.2f} MB)")

    return output_path


def build_hand_drawn_figures_zip():
    """Build ZIP for hand-drawn figures."""
    print("Building hand-drawn-figures.zip...")

    pairs = collect_figure_pairs(OUTPUT_FIGURES_HAND_DRAWN, recursive=False)

    # Filter out any non-image files (like metadata.json)
    pairs = [(name, png, svg, rel) for name, png, svg, rel in pairs
             if not name.endswith('.json')]

    if not pairs:
        print("  No hand-drawn figures found (this is expected if you haven't added any yet)")
        # Create an empty placeholder ZIP with just license
        output_path = OUTPUT_DOWNLOADS / "hand-drawn-figures.zip"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("LICENSE.txt", LICENSE_TEXT)
            zf.writestr("README.txt", create_readme("Hand-Drawn", 0) +
                       "\n\nNote: No hand-drawn figures have been added yet.\n"
                       "Add PNG/SVG pairs to images/hand-drawn/ and rebuild.\n")

        print(f"  Created placeholder: {output_path}")
        return output_path

    print(f"  Found {len(pairs)} figure pairs")

    output_path = OUTPUT_DOWNLOADS / "hand-drawn-figures.zip"
    create_zip(output_path, pairs, "Hand-Drawn")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Created: {output_path} ({size_mb:.2f} MB)")

    return output_path


def main():
    """Main entry point."""
    print("=" * 60)
    print("Building Figure Downloads")
    print("=" * 60)
    print()

    build_generated_figures_zip()
    print()
    build_hand_drawn_figures_zip()

    print()
    print("=" * 60)
    print("Done! ZIP files are in the 'downloads/' directory.")
    print("=" * 60)


if __name__ == "__main__":
    main()
