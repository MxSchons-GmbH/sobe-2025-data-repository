#!/usr/bin/env python3
"""
Rename all figures to follow SEO and data science best practices.

This script:
1. Renames all generated and hand-drawn figure files
2. Updates figures-metadata.json
3. Updates hand-drawn-metadata.json
4. Updates run_all_figures.py code references

Naming conventions:
- 2-5 words per filename
- Hyphens as separators (never underscores or spaces)
- Lowercase only
- Most important keyword first
- Descriptive of actual content
- No abbreviations (simulation not sim)
- No dates in filename
"""

import json
import os
import re
import shutil
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent
GENERATED_DIR = REPO_ROOT / "data-and-figures" / "figures" / "generated"
HAND_DRAWN_DIR = REPO_ROOT / "data-and-figures" / "figures" / "hand-drawn"
FIGURES_METADATA = REPO_ROOT / "data-and-figures" / "metadata" / "figures-metadata.json"
HAND_DRAWN_METADATA = REPO_ROOT / "data-and-figures" / "metadata" / "hand-drawn-metadata.json"
RUN_ALL_FIGURES = REPO_ROOT / "scripts" / "run_all_figures.py"

# =============================================================================
# GENERATED FIGURES MAPPING
# Format: "old_filename": "new_filename" (without extension)
# =============================================================================
GENERATED_MAPPING = {
    # Main overview figures
    "all-sim-rec": "neural-simulations-recordings-overview",
    "num-neurons": "neuron-counts-organism-comparison",

    # Technology figures
    "imaging-speed": "neuroimaging-speed-comparison",
    "compute": "compute-hardware-trends-brain-emulation",
    "storage-costs": "storage-cost-trends-brain-data",
    "compute-storage-parallel": "compute-storage-trends-parallel",
    "hardware-scaling": "gpu-memory-interconnect-scaling",
    "bandwidth-scaling": "brain-imaging-bandwidth-requirements",

    # Recording figures
    "neuro-recordings": "neural-recording-timeline-overview",
    "recording-modalities": "neural-recording-modalities-comparison",
    "rec-heatmap": "neural-recording-capabilities-heatmap",

    # Simulation figures
    "sim-heatmap": "neural-simulation-capabilities-heatmap",

    # Connectomics figures
    "scanned-brain-tissue": "connectomics-tissue-scanning-progress",
    "cost-per-neuron": "connectomics-neuron-reconstruction-cost",
    "cost-per-neuron-no-illust": "connectomics-neuron-cost-estimates",

    # Emulation figures
    "emulation-compute-time-based": "brain-emulation-compute-time-based",
    "emulation-compute-event-driven": "brain-emulation-compute-event-driven",
    "emulation-storage-requirements": "brain-emulation-storage-requirements",
    "organism-compute": "brain-simulation-compute-by-organism",

    # Funding/Initiatives figures
    "funding": "brain-research-initiative-funding",
    "initiatives1": "brain-initiatives-timeline-overview",
    "initiatives2": "brain-initiatives-funding-comparison",
    "initiatives3": "brain-initiatives-budget-categories-timeline",
    "initiatives4": "brain-initiatives-budget-categories-bars",
}

# Organism-specific simulation figures (in neuro-sim/ subdirectory)
NEURO_SIM_MAPPING = {
    "C. elegans": "neural-simulation-celegans",
    "Drosophila": "neural-simulation-drosophila",
    "Zebrafish": "neural-simulation-zebrafish",
    "Mouse": "neural-simulation-mouse",
    "Human": "neural-simulation-human",
}

# Organism-specific recording figures (in neuro-rec/ subdirectory)
NEURO_REC_MAPPING = {
    "C. elegans-fixated": "neural-recording-celegans-fixated",
    "C. elegans-moving": "neural-recording-celegans-moving",
    "Drosophila-fixated": "neural-recording-drosophila-fixated",
    "Zebrafish-fixated": "neural-recording-zebrafish-fixated",
    "Mouse-fixated": "neural-recording-mouse-fixated",
    "Mouse-moving": "neural-recording-mouse-moving",
    "Human-fixated": "neural-recording-human-fixated",
}

# =============================================================================
# HAND-DRAWN FIGURES MAPPING
# =============================================================================
HAND_DRAWN_MAPPING = {
    "brain-emulation-pipeline": "brain-emulation-pipeline-overview",
    "LLM vs BEM Pipelines": "llm-vs-brain-emulation-pipelines",
    "mouse-to-digital": "mouse-digital-twin-concept",
    "structure-to-function": "structure-function-pipeline-brain",
    "celegans multiple": "celegans-multiple-connectomes",
    "celegans original": "celegans-original-connectome",
    "drosophila brain and spine": "drosophila-brain-ventral-nerve-cord",
    "drosophila half brain": "drosophila-hemisphere-brain",
    "drosophila spine": "drosophila-ventral-nerve-cord",
    "drosophila whole brain": "drosophila-whole-brain-anatomy",
    "human brain": "human-brain-anatomy",
    "larval zebrafish brain": "zebrafish-larval-brain-anatomy",
    "larval zebrafish spine": "zebrafish-larval-spinal-cord",
    "mouse brain": "mouse-brain-anatomy",
    "neuron count scale organisms": "neuron-count-scale-comparison",
    "brain-fab": "brain-fab-prototype-illustration",
    "neurorecording scale comparison": "neural-recording-scale-comparison",
    "feature illustration": "brain-emulation-feature-illustration",
}


def rename_files(directory: Path, mapping: dict, dry_run: bool = True) -> list:
    """Rename files according to mapping."""
    operations = []

    for old_name, new_name in mapping.items():
        for ext in [".svg", ".png"]:
            old_path = directory / f"{old_name}{ext}"
            new_path = directory / f"{new_name}{ext}"

            if old_path.exists():
                operations.append((old_path, new_path))
                if dry_run:
                    print(f"  Will rename: {old_name}{ext} -> {new_name}{ext}")
                else:
                    shutil.move(old_path, new_path)
                    print(f"  Renamed: {old_name}{ext} -> {new_name}{ext}")
            else:
                # Check if already renamed
                if new_path.exists():
                    print(f"  Already renamed: {new_name}{ext}")
                else:
                    print(f"  WARNING: Not found: {old_path}")

    return operations


def update_figures_metadata(dry_run: bool = True):
    """Update figures-metadata.json with new filenames."""
    with open(FIGURES_METADATA) as f:
        data = json.load(f)

    # Build reverse mapping for lookups
    all_mappings = {}
    all_mappings.update(GENERATED_MAPPING)
    all_mappings.update(NEURO_SIM_MAPPING)
    all_mappings.update(NEURO_REC_MAPPING)

    changes = 0
    for fig in data.get("figures", []):
        old_filename = fig.get("filename", "")
        if old_filename in all_mappings:
            new_filename = all_mappings[old_filename]
            print(f"  Metadata: {old_filename} -> {new_filename}")
            if not dry_run:
                fig["filename"] = new_filename
            changes += 1

    if not dry_run and changes > 0:
        with open(FIGURES_METADATA, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    return changes


def update_hand_drawn_metadata(dry_run: bool = True):
    """Update hand-drawn-metadata.json with new filenames."""
    with open(HAND_DRAWN_METADATA) as f:
        data = json.load(f)

    changes = 0
    for fig in data.get("figures", []):
        old_filename = fig.get("filename", "")
        if old_filename in HAND_DRAWN_MAPPING:
            new_filename = HAND_DRAWN_MAPPING[old_filename]
            print(f"  Metadata: {old_filename} -> {new_filename}")
            if not dry_run:
                fig["filename"] = new_filename
            changes += 1

    if not dry_run and changes > 0:
        with open(HAND_DRAWN_METADATA, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    return changes


def update_run_all_figures(dry_run: bool = True):
    """Update run_all_figures.py with new filenames."""
    with open(RUN_ALL_FIGURES) as f:
        content = f.read()

    original = content
    changes = 0

    # Update all mappings
    all_mappings = {}
    all_mappings.update(GENERATED_MAPPING)
    all_mappings.update(NEURO_SIM_MAPPING)
    all_mappings.update(NEURO_REC_MAPPING)

    for old_name, new_name in all_mappings.items():
        # Match patterns like f"{old_name}.svg" or f'{old_name}.png' or "{old_name}"
        patterns = [
            (f'"{old_name}.svg"', f'"{new_name}.svg"'),
            (f'"{old_name}.png"', f'"{new_name}.png"'),
            (f"'{old_name}.svg'", f"'{new_name}.svg'"),
            (f"'{old_name}.png'", f"'{new_name}.png'"),
            (f'f"{old_name}', f'f"{new_name}'),
            (f"f'{old_name}", f"f'{new_name}"),
            (f'"{old_name}"', f'"{new_name}"'),
            (f"'{old_name}'", f"'{new_name}'"),
        ]

        for old_pattern, new_pattern in patterns:
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                changes += 1
                print(f"  Code: {old_pattern} -> {new_pattern}")

    if not dry_run and content != original:
        with open(RUN_ALL_FIGURES, "w") as f:
            f.write(content)

    return changes


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Rename figures to follow SEO best practices")
    parser.add_argument("--apply", action="store_true", help="Actually rename files (default is dry run)")
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("=" * 60)
        print("DRY RUN - No files will be changed")
        print("Run with --apply to actually rename files")
        print("=" * 60)
    else:
        print("=" * 60)
        print("APPLYING CHANGES")
        print("=" * 60)

    print("\n1. Renaming generated figures (main directory)...")
    rename_files(GENERATED_DIR, GENERATED_MAPPING, dry_run)

    print("\n2. Renaming neuro-sim figures...")
    rename_files(GENERATED_DIR / "neuro-sim", NEURO_SIM_MAPPING, dry_run)

    print("\n3. Renaming neuro-rec figures...")
    rename_files(GENERATED_DIR / "neuro-rec", NEURO_REC_MAPPING, dry_run)

    print("\n4. Renaming hand-drawn figures...")
    rename_files(HAND_DRAWN_DIR, HAND_DRAWN_MAPPING, dry_run)

    print("\n5. Updating figures-metadata.json...")
    update_figures_metadata(dry_run)

    print("\n6. Updating hand-drawn-metadata.json...")
    update_hand_drawn_metadata(dry_run)

    print("\n7. Updating run_all_figures.py...")
    update_run_all_figures(dry_run)

    if dry_run:
        print("\n" + "=" * 60)
        print("DRY RUN COMPLETE - Run with --apply to make changes")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("RENAME COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    main()
