#!/usr/bin/env python3
"""
Add reference management columns to all internal TSV files.

This script programmatically adds the new columns required for reference tracking:
- ref_id: Link to bibliography entry (empty - to be filled)
- supporting_refs: Additional references (empty - to be filled)
- ref_note: Contextual notes (empty - to be filled)
- confidence: Data quality flag (set to 'none' - needs human review)
- validated_by: Validation status (set to 'none' - needs human review)

All values are set to empty or 'none' to explicitly indicate they need
human review. NO values are inferred or guessed by this script.

The script automatically finds all TSV files in data/ that are missing
any of the required columns, excluding:
- data/external/ (third-party datasets)
- data/_metadata/ (JSON metadata files)

Usage:
    python add_reference_columns.py           # Preview changes (dry run)
    python add_reference_columns.py --apply   # Apply changes
"""

import argparse
import csv
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA_DIR

# Directories to exclude (external datasets, metadata)
EXCLUDED_DIRS = {"external", "_metadata"}

# New columns to add (in order they should appear at end of file)
NEW_COLUMNS = [
    ("ref_id", ""),           # Empty - needs human input
    ("supporting_refs", ""),  # Empty - needs human input
    ("ref_note", ""),         # Empty - needs human input
    ("confidence", "none"),   # Explicit 'none' - needs human review
    ("validated_by", "none"), # Explicit 'none' - needs human review
]


def find_files_needing_columns() -> list:
    """Find all TSV files missing any required reference columns."""
    files_to_fix = []

    for tsv_file in DATA_DIR.rglob("*.tsv"):
        # Skip excluded directories
        if any(excluded in tsv_file.parts for excluded in EXCLUDED_DIRS):
            continue

        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                header_line = f.readline()
                if not header_line:
                    continue

                # Handle BOM
                if header_line.startswith('\ufeff'):
                    header_line = header_line[1:]

                header = [col.strip() for col in header_line.strip().split('\t')]

                # Check which columns are missing
                missing = [col for col, _ in NEW_COLUMNS if col not in header]

                if missing:
                    files_to_fix.append({
                        'path': tsv_file,
                        'header': header,
                        'missing': missing,
                    })
        except Exception as e:
            print(f"Warning: Could not read {tsv_file}: {e}")

    return files_to_fix


def add_columns_to_file(filepath: Path, dry_run: bool = True) -> dict:
    """Add reference columns to a single TSV file.

    Returns dict with details of changes made.
    """
    result = {
        "file": str(filepath.relative_to(DATA_DIR)),
        "rows": 0,
        "columns_added": [],
        "columns_skipped": [],
    }

    # Read all lines
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Handle BOM
    if content.startswith('\ufeff'):
        content = content[1:]

    lines = content.split('\n')

    # Remove trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return result

    # Parse header
    header = lines[0].split('\t')

    # Determine which columns to add
    for col_name, default_value in NEW_COLUMNS:
        if col_name in header:
            result["columns_skipped"].append(col_name)
        else:
            result["columns_added"].append(col_name)

    result["rows"] = len(lines) - 1  # Exclude header

    if not result["columns_added"]:
        return result

    # Build new content
    new_lines = []

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        parts = line.split('\t')

        if i == 0:
            # Header - add new column names
            for col_name, _ in NEW_COLUMNS:
                if col_name not in header:
                    parts.append(col_name)
        else:
            # Data row - add default values
            for col_name, default_value in NEW_COLUMNS:
                if col_name not in header:
                    parts.append(default_value)

        new_lines.append('\t'.join(parts))

    # Write back if not dry run
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines) + '\n')

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Add reference management columns to TSV files"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry run/preview)"
    )
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 60)
    print("ADD REFERENCE COLUMNS TO TSV FILES")
    print("=" * 60)

    if dry_run:
        print("\n[DRY RUN MODE - no files will be modified]")
        print("Use --apply to make changes.\n")
    else:
        print("\n[APPLYING CHANGES]\n")

    # Find files needing columns
    files_to_fix = find_files_needing_columns()

    if not files_to_fix:
        print("All TSV files already have the required reference columns!")
        return 0

    print(f"Found {len(files_to_fix)} files missing reference columns:")
    print(f"Columns: {[c[0] for c in NEW_COLUMNS]}")
    print(f"Default values: ref_id='', confidence='none', validated_by='none'")
    print()

    results = []
    for file_info in files_to_fix:
        filepath = file_info['path']

        result = add_columns_to_file(filepath, dry_run=dry_run)
        results.append(result)

        status = "would add" if dry_run else "added"
        if result["columns_added"]:
            print(f"OK: {result['file']}")
            print(f"    {status}: {result['columns_added']}")
            if result["columns_skipped"]:
                print(f"    skipped (already exist): {result['columns_skipped']}")
        else:
            print(f"SKIP: {result['file']} (all columns already exist)")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_rows = sum(r["rows"] for r in results)
    files_modified = sum(1 for r in results if r["columns_added"])

    print(f"Files needing update: {len(files_to_fix)}")
    print(f"Files {'would be ' if dry_run else ''}modified: {files_modified}")
    print(f"Total rows affected: {total_rows}")

    if dry_run:
        print("\nRun with --apply to make changes.")
    else:
        print("\nDone! All new values are set to empty or 'none'.")
        print("Human review is required to fill in ref_id and confidence values.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
