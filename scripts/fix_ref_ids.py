#!/usr/bin/env python3
"""
Fix ref_id issues across TSV files.

This script:
1. Replaces "none" with empty string
2. Moves internal_* prefixes to ref_note column
3. Adds missing references to bibliography
4. Validates all ref_ids exist in bibliography
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
BIB_PATH = DATA_DIR / "references" / "bibliography.json"

# References to add to bibliography
NEW_REFERENCES = [
    {
        "id": "sobe_2025",
        "type": "report",
        "title": "State of Brain Emulation Report 2025",
        "author": [
            {"family": "Zanichelli", "given": "N."},
            {"family": "Schons", "given": "M."}
        ],
        "issued": {"date-parts": [[2025]]},
        "URL": "https://brainemulation.org"
    },
    {
        "id": "nvidia_h100_2024",
        "type": "webpage",
        "title": "NVIDIA H100 Tensor Core GPU",
        "author": [{"literal": "NVIDIA"}],
        "issued": {"date-parts": [[2024]]},
        "URL": "https://www.nvidia.com/en-us/data-center/h100/"
    },
    {
        "id": "aws_s3_pricing_2025",
        "type": "webpage",
        "title": "Amazon S3 Pricing",
        "author": [{"literal": "Amazon Web Services"}],
        "issued": {"date-parts": [[2025]]},
        "URL": "https://aws.amazon.com/s3/pricing/"
    },
    {
        "id": "wellcome_connectomics_2024",
        "type": "webpage",
        "title": "Wellcome Connectomics Initiative",
        "author": [{"literal": "Wellcome Trust"}],
        "issued": {"date-parts": [[2024]]},
        "URL": "https://wellcome.org/what-we-do/our-work/wellcome-connectomics"
    },
    {
        "id": "microns_2021",
        "type": "article-journal",
        "title": "Functional connectomics spanning multiple areas of mouse visual cortex",
        "author": [{"literal": "MICrONS Consortium"}],
        "issued": {"date-parts": [[2021]]},
        "DOI": "10.1101/2021.07.28.454025",
        "URL": "https://www.microns-explorer.org/"
    },
    {
        "id": "januszewski2018",
        "type": "article-journal",
        "title": "High-precision automated reconstruction of neurons with flood-filling networks",
        "author": [
            {"family": "Januszewski", "given": "Michał"},
            {"family": "Kornfeld", "given": "Jörgen"},
            {"family": "Li", "given": "Peter H."},
            {"family": "Pope", "given": "Art"},
            {"family": "Blakely", "given": "Tim"},
            {"family": "Lindsey", "given": "Larry"},
            {"family": "Maitin-Shepard", "given": "Jeremy"},
            {"family": "Tyka", "given": "Mike"},
            {"family": "Denk", "given": "Winfried"},
            {"family": "Jain", "given": "Viren"}
        ],
        "container-title": "Nature Methods",
        "issued": {"date-parts": [[2018]]},
        "volume": "15",
        "page": "605-610",
        "DOI": "10.1038/s41592-018-0049-4"
    },
    {
        "id": "schwartz2018",
        "type": "article-journal",
        "title": "High-throughput, high-resolution neuroimaging with multibeam scanning electron microscopy",
        "author": [
            {"family": "Schwartz", "given": "A."},
            # Add more authors as needed
        ],
        "container-title": "bioRxiv",
        "issued": {"date-parts": [[2018]]},
        "DOI": "10.1101/386250"
    },
    {
        "id": "chen2020",
        "type": "article-journal",
        "title": "An interactive framework for whole-brain maps at cellular resolution",
        "author": [
            {"family": "Chen", "given": "X."},
            # Add more authors as needed
        ],
        "container-title": "Nature Neuroscience",
        "issued": {"date-parts": [[2020]]},
        "DOI": "10.1038/s41593-020-0633-2"
    }
]


def load_bibliography():
    """Load the bibliography JSON."""
    with open(BIB_PATH) as f:
        return json.load(f)


def save_bibliography(bib):
    """Save the bibliography JSON."""
    bib["_generated"] = datetime.now().isoformat()
    with open(BIB_PATH, "w") as f:
        json.dump(bib, f, indent=2, ensure_ascii=False)
    print(f"Saved bibliography to {BIB_PATH}")


def add_missing_references(bib):
    """Add missing references to bibliography."""
    existing_ids = {e["id"] for e in bib["references"]}
    added = []

    for ref in NEW_REFERENCES:
        if ref["id"] not in existing_ids:
            bib["references"].append(ref)
            added.append(ref["id"])
            print(f"  Added: {ref['id']}")

    return added


def fix_tsv_file(filepath, bib_ids, dry_run=True):
    """Fix ref_id issues in a single TSV file."""
    changes = []

    with open(filepath, 'r') as f:
        lines = f.readlines()

    if not lines:
        return changes

    header = lines[0].strip().split('\t')
    if 'ref_id' not in header:
        return changes

    ref_id_col = header.index('ref_id')
    ref_note_col = header.index('ref_note') if 'ref_note' in header else None

    new_lines = [lines[0]]  # Keep header

    for row_num, line in enumerate(lines[1:], start=2):
        cols = line.rstrip('\n').split('\t')

        # Ensure we have enough columns
        while len(cols) <= max(ref_id_col, ref_note_col or 0):
            cols.append('')

        original_ref_id = cols[ref_id_col]
        ref_id = original_ref_id.strip()

        # Fix 1: Replace "none" with empty
        if ref_id == 'none':
            cols[ref_id_col] = ''
            changes.append({
                'file': str(filepath),
                'row': row_num,
                'change': 'Replaced "none" with empty',
                'before': original_ref_id,
                'after': ''
            })

        # Fix 2: Move internal_* to ref_note
        elif ref_id.startswith('internal_'):
            cols[ref_id_col] = ''
            if ref_note_col is not None:
                existing_note = cols[ref_note_col].strip()
                # Convert internal_estimate_2025 -> "Internal estimate"
                # Convert internal_methodology_2025 -> "Internal methodology"
                note_text = ref_id.replace('internal_', '').replace('_', ' ').replace('2025', '').strip().capitalize()
                if note_text == 'Estimate':
                    note_text = 'Internal estimate'
                elif note_text == 'Methodology':
                    note_text = 'Internal methodology'

                if existing_note:
                    cols[ref_note_col] = f"{existing_note}; {note_text}"
                else:
                    cols[ref_note_col] = note_text

                changes.append({
                    'file': str(filepath),
                    'row': row_num,
                    'change': f'Moved to ref_note',
                    'before': original_ref_id,
                    'after': f'ref_id="", ref_note="{cols[ref_note_col]}"'
                })

        # Fix 3: Validate ref_id exists in bibliography
        elif ref_id and ref_id not in bib_ids:
            changes.append({
                'file': str(filepath),
                'row': row_num,
                'change': 'WARNING: ref_id not in bibliography',
                'before': original_ref_id,
                'after': '(needs manual fix or bibliography addition)'
            })

        new_lines.append('\t'.join(cols) + '\n')

    if not dry_run and changes:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print(f"  Updated: {filepath}")

    return changes


def main(dry_run=True):
    print("=" * 60)
    print("Fix ref_id Issues Script")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    print()

    # Load bibliography
    print("Loading bibliography...")
    bib = load_bibliography()
    bib_ids = {e["id"] for e in bib["references"]}
    print(f"  Found {len(bib_ids)} existing entries")

    # Add missing references
    print("\nAdding missing references to bibliography...")
    added = add_missing_references(bib)
    if added:
        bib_ids.update(added)
        if not dry_run:
            save_bibliography(bib)
    else:
        print("  No new references to add")

    # Process TSV files
    print("\nProcessing TSV files...")
    all_changes = []

    for tsv_file in DATA_DIR.rglob('*.tsv'):
        if 'external' in str(tsv_file):
            continue

        changes = fix_tsv_file(tsv_file, bib_ids, dry_run=dry_run)
        all_changes.extend(changes)

    # Report
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    # Group by change type
    none_fixes = [c for c in all_changes if 'none' in c['change'].lower()]
    internal_fixes = [c for c in all_changes if 'ref_note' in c['change'].lower()]
    warnings = [c for c in all_changes if 'WARNING' in c['change']]

    print(f"Total changes: {len(all_changes)}")
    print(f"  - 'none' -> empty: {len(none_fixes)}")
    print(f"  - internal_* -> ref_note: {len(internal_fixes)}")
    print(f"  - Warnings (need manual fix): {len(warnings)}")

    if warnings:
        print("\nWarnings that need attention:")
        for w in warnings:
            print(f"  {w['file']}:{w['row']} - {w['before']}")

    if dry_run:
        print("\n*** DRY RUN - No files were modified ***")
        print("Run with --apply to make changes")

    return all_changes


if __name__ == "__main__":
    import sys
    dry_run = "--apply" not in sys.argv
    main(dry_run=dry_run)
