#!/usr/bin/env python3
"""
Clean up connectomics TSV files by removing 'Unnamed' spacer columns.

These columns are artifacts from Excel export and contain no useful data.
Also extracts ref_id from the id column (author-year format).

Usage:
    python cleanup_connectomics.py           # Preview changes (dry run)
    python cleanup_connectomics.py --apply   # Apply changes
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA_DIR

# Connectomics files to clean
CONNECTOMICS_FILES = [
    DATA_DIR / "connectomics" / "connectomics-2nm.tsv",
    DATA_DIR / "connectomics" / "connectomics-10nm.tsv",
    DATA_DIR / "connectomics" / "connectomics-25nm.tsv",
    DATA_DIR / "connectomics" / "connectomics-50nm.tsv",
]


def extract_ref_id(id_value):
    """Extract ref_id from author-year id format.

    Examples:
        'Briggman 2011' -> 'briggman2011'
        'Shapson-Coe 2021' -> 'shapsoncoe2021'
        'MICrONS 2021' -> 'microns2021'
    """
    if not id_value or not isinstance(id_value, str):
        return ""

    # Match author-year pattern
    match = re.match(r'^([A-Za-z\-]+)\s+(\d{4})', id_value.strip())
    if match:
        author = match.group(1).lower().replace('-', '')
        year = match.group(2)
        return f"{author}{year}"

    return ""


def clean_file(filepath, dry_run=True):
    """Remove Unnamed columns and populate ref_id from id column."""
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    if not lines:
        return {"file": filepath.name, "error": "empty file"}

    # Parse header
    header = lines[0].split('\t')

    # Find columns to remove (Unnamed:*)
    cols_to_remove = []
    cols_to_keep = []
    for i, col in enumerate(header):
        if col.strip().startswith('Unnamed'):
            cols_to_remove.append(i)
        else:
            cols_to_keep.append(i)

    # Find ref_id and id column indices (in kept columns)
    id_idx = None
    ref_id_idx = None
    for new_idx, old_idx in enumerate(cols_to_keep):
        if header[old_idx].strip() == 'id':
            id_idx = new_idx
        if header[old_idx].strip() == 'ref_id':
            ref_id_idx = new_idx

    # Build new lines
    new_lines = []
    ref_ids_populated = 0

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        parts = line.split('\t')

        # Keep only non-Unnamed columns
        new_parts = []
        for idx in cols_to_keep:
            if idx < len(parts):
                new_parts.append(parts[idx])
            else:
                new_parts.append('')

        # Populate ref_id from id column (skip header and unit rows)
        if i > 1 and id_idx is not None and ref_id_idx is not None:
            id_value = new_parts[id_idx] if id_idx < len(new_parts) else ""
            current_ref_id = new_parts[ref_id_idx] if ref_id_idx < len(new_parts) else ""

            # Only populate if empty or 'none' (default value)
            if not current_ref_id.strip() or current_ref_id.strip() == 'none':
                extracted = extract_ref_id(id_value)
                if extracted:
                    new_parts[ref_id_idx] = extracted
                    ref_ids_populated += 1

        new_lines.append('\t'.join(new_parts))

    result = {
        "file": filepath.name,
        "cols_removed": len(cols_to_remove),
        "removed_names": [header[i] for i in cols_to_remove],
        "rows": len(lines) - 2,  # Exclude header and unit row
        "ref_ids_populated": ref_ids_populated,
    }

    # Write if not dry run
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines) + '\n')

    return result


def main():
    parser = argparse.ArgumentParser(description="Clean up connectomics TSV files")
    parser.add_argument('--apply', action='store_true', help='Apply changes')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 60)
    print("CLEAN UP CONNECTOMICS TSV FILES")
    print("=" * 60)

    if dry_run:
        print("\n[DRY RUN MODE - no files will be modified]")
        print("Use --apply to make changes.\n")
    else:
        print("\n[APPLYING CHANGES]\n")

    total_cols_removed = 0
    total_ref_ids = 0

    for filepath in CONNECTOMICS_FILES:
        if not filepath.exists():
            print(f"SKIP: {filepath.name} (not found)")
            continue

        result = clean_file(filepath, dry_run=dry_run)

        print(f"OK: {result['file']}")
        print(f"    {'Would remove' if dry_run else 'Removed'}: {result['cols_removed']} Unnamed columns")
        print(f"    {'Would populate' if dry_run else 'Populated'}: {result['ref_ids_populated']} ref_ids from id column")

        total_cols_removed += result['cols_removed']
        total_ref_ids += result['ref_ids_populated']

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Unnamed columns {'would be ' if dry_run else ''}removed: {total_cols_removed}")
    print(f"ref_ids {'would be ' if dry_run else ''}populated: {total_ref_ids}")

    if dry_run:
        print("\nRun with --apply to make changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
