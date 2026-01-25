#!/usr/bin/env python3
"""
Build script to sync data files from data/ to dist/data/

This script:
1. Copies all TSV files from data/ to dist/data/ (maintaining directory structure)
2. Generates dist/data/_metadata.json from individual metadata files in data/_metadata/

Run from repository root:
    python scripts/build_dist_data.py
"""

import json
import shutil
from pathlib import Path

# Repository paths
REPO_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = REPO_ROOT / "data"
METADATA_DIR = DATA_DIR / "_metadata"
DIST_DATA_DIR = REPO_ROOT / "dist" / "data"
OUTPUT_METADATA = DIST_DATA_DIR / "_metadata.json"

# Category configuration - maps directory names to display info
CATEGORIES = {
    "simulations": {
        "title": "Neural Simulations",
        "description": "Comprehensive data on computational brain models and neural simulations across organisms.",
        "icon": "cpu",
    },
    "recordings": {
        "title": "Neural Recordings",
        "description": "Historical and contemporary data on neural recording techniques, capabilities, and information rates.",
        "icon": "activity",
    },
    "connectomics": {
        "title": "Connectomics",
        "description": "Data on brain connectivity mapping at various resolutions, from synaptic to regional scales.",
        "icon": "share-2",
    },
    "compute": {
        "title": "Compute & Hardware",
        "description": "Computational requirements and hardware data for AI and neural simulations.",
        "icon": "zap",
    },
    "costs": {
        "title": "Costs & Funding",
        "description": "Economic analysis of neuroscience projects, hardware costs, and comparisons to other megaprojects.",
        "icon": "dollar-sign",
    },
    "imaging": {
        "title": "Imaging",
        "description": "Neuroimaging technologies and modalities.",
        "icon": "eye",
    },
    "organisms": {
        "title": "Model Organisms",
        "description": "Reference data on model organisms used in neuroscience research.",
        "icon": "database",
    },
    "initiatives": {
        "title": "Brain Initiatives",
        "description": "Overview of major brain research programs and their goals.",
        "icon": "globe",
    },
    "formulas": {
        "title": "Calculator Formulas",
        "description": "Formula definitions for the brain emulation calculator.",
        "icon": "calculator",
    },
    "parameters": {
        "title": "Shared Parameters",
        "description": "Shared parameter definitions used across calculations.",
        "icon": "settings",
    },
    "recording": {
        "title": "Recording Capabilities",
        "description": "Neural recording capabilities and costs by organism.",
        "icon": "radio",
    },
}


def read_tsv_headers(tsv_path: Path) -> list[str]:
    """Read column headers from a TSV file."""
    with open(tsv_path, 'r', encoding='utf-8') as f:
        header_line = f.readline().strip()
        return header_line.split('\t')


def count_tsv_rows(tsv_path: Path) -> int:
    """Count data rows in a TSV file (excluding header)."""
    with open(tsv_path, 'r', encoding='utf-8') as f:
        lines = [l for l in f.readlines() if l.strip()]
        return max(0, len(lines) - 1)  # Exclude header


def format_row_count(count: int) -> str:
    """Format row count for display."""
    if count >= 100:
        return "100+"
    elif count >= 50:
        return "50+"
    elif count >= 30:
        return "30+"
    elif count >= 20:
        return "20+"
    elif count >= 10:
        return "10+"
    else:
        return str(count)


def copy_data_files() -> dict[str, list[Path]]:
    """
    Copy all TSV files from data/ to dist/data/.
    Returns a dict mapping category -> list of copied files.
    """
    copied_files: dict[str, list[Path]] = {}

    # Get all TSV files, excluding _metadata directory
    for tsv_file in DATA_DIR.rglob("*.tsv"):
        if "_metadata" in tsv_file.parts:
            continue

        # Get relative path from data/
        rel_path = tsv_file.relative_to(DATA_DIR)
        category = rel_path.parts[0]

        # Create destination path
        dest_path = DIST_DATA_DIR / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(tsv_file, dest_path)

        # Track by category
        if category not in copied_files:
            copied_files[category] = []
        copied_files[category].append(dest_path)

    return copied_files


def load_metadata(category: str, filename: str) -> dict | None:
    """Load metadata for a specific file from data/_metadata/."""
    # Try exact path first
    metadata_path = METADATA_DIR / category / f"{Path(filename).stem}.json"
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def generate_dataset_entry(tsv_path: Path, category: str) -> dict:
    """Generate a dataset entry for _metadata.json."""
    filename = tsv_path.name
    stem = tsv_path.stem

    # Load metadata if available
    metadata = load_metadata(category, filename)

    # Read TSV info
    columns = read_tsv_headers(tsv_path)
    row_count = count_tsv_rows(tsv_path)

    # Build entry
    entry = {
        "id": stem.replace("-", "_") if not stem.replace("-", "_").replace("_", "").isalnum() else stem,
        "title": metadata.get("title", stem.replace("-", " ").title()) if metadata else stem.replace("-", " ").title(),
        "description": metadata.get("description", f"Data from {filename}") if metadata else f"Data from {filename}",
        "filename": filename,
        "path": f"data/{category}",
        "rows": format_row_count(row_count),
        "columns": columns,
    }

    # Add optional fields from metadata
    if metadata:
        if metadata.get("source") and metadata["source"] != "State of Brain Emulation Report 2025":
            entry["source"] = metadata["source"]
        if metadata.get("license") and metadata["license"] != "CC BY 4.0":
            entry["license"] = metadata["license"]

    return entry


def build_metadata(copied_files: dict[str, list[Path]]) -> dict:
    """Build the consolidated _metadata.json structure."""
    categories = []

    for category_id, category_info in CATEGORIES.items():
        if category_id not in copied_files:
            continue

        datasets = []
        for tsv_path in sorted(copied_files[category_id]):
            entry = generate_dataset_entry(tsv_path, category_id)
            datasets.append(entry)

        if datasets:
            categories.append({
                "id": category_id,
                "title": category_info["title"],
                "description": category_info["description"],
                "icon": category_info["icon"],
                "datasets": datasets,
            })

    return {
        "categories": categories,
        "github": {
            "repo": "https://github.com/mxschons/sobe-2025-data-repository",
            "dataPath": "data",
            "issuesUrl": "https://github.com/mxschons/sobe-2025-data-repository/issues",
        },
        "license": {
            "name": "CC BY 4.0",
            "fullName": "Creative Commons Attribution 4.0 International",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "attribution": "Zanichelli & Schons et al., State of Brain Emulation Report 2025",
        },
    }


def main():
    """Main entry point."""
    print("Building dist/data/ from source data files...\n")

    # Ensure output directory exists
    DIST_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Copy TSV files
    print("Copying TSV files...")
    copied_files = copy_data_files()
    total_files = sum(len(files) for files in copied_files.values())
    print(f"  Copied {total_files} files across {len(copied_files)} categories\n")

    # Generate metadata
    print("Generating _metadata.json...")
    metadata = build_metadata(copied_files)

    with open(OUTPUT_METADATA, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"  Generated {OUTPUT_METADATA}\n")

    # Summary
    print("=" * 50)
    print("Summary:")
    for category_id, files in sorted(copied_files.items()):
        print(f"  {category_id}: {len(files)} files")
    print("=" * 50)
    print("\n✅ Build complete!")


if __name__ == "__main__":
    main()
