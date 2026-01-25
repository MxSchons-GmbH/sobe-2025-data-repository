#!/usr/bin/env python3
"""
Add reference management columns to parameter and formula TSV files.

This script programmatically adds the new columns required for reference tracking:
- ref_id: Link to bibliography entry (empty - to be filled)
- supporting_refs: Additional references (empty - to be filled)
- ref_note: Contextual notes (empty - to be filled)
- confidence: Data quality flag (set to 'none' - needs human review)
- validated_by: Validation status (set to 'none' - needs human review)

All values are set to empty or 'none' to explicitly indicate they need
human review. NO values are inferred or guessed by this script.

Usage:
    python add_reference_columns.py           # Add columns to all files
    python add_reference_columns.py --dry-run # Preview without writing
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA_DIR

# Files to update with new reference columns
TARGET_FILES = [
    DATA_DIR / "parameters" / "shared.tsv",
    DATA_DIR / "formulas" / "costs.tsv",
    DATA_DIR / "formulas" / "storage.tsv",
    DATA_DIR / "formulas" / "connectomics.tsv",
]

# New columns to add (in order)
NEW_COLUMNS = [
    ("ref_id", ""),           # Empty - needs human input
    ("supporting_refs", ""),  # Empty - needs human input
    ("ref_note", ""),         # Empty - needs human input
    ("confidence", "none"),   # Explicit 'none' - needs human review
    ("validated_by", "none"), # Explicit 'none' - needs human review
]


def add_columns_to_file(filepath: Path, dry_run: bool = False) -> dict:
    """Add reference columns to a single TSV file.

    Returns dict with details of changes made.
    """
    result = {
        "file": str(filepath.relative_to(DATA_DIR)),
        "rows": 0,
        "columns_added": [],
        "columns_skipped": [],
    }

    # Read the file
    df = pd.read_csv(filepath, sep='\t', dtype=str)
    result["rows"] = len(df)

    # Add each new column if not already present
    for col_name, default_value in NEW_COLUMNS:
        if col_name in df.columns:
            result["columns_skipped"].append(col_name)
        else:
            df[col_name] = default_value
            result["columns_added"].append(col_name)

    # Write back if not dry run and changes were made
    if not dry_run and result["columns_added"]:
        df.to_csv(filepath, sep='\t', index=False)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Add reference management columns to TSV files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("ADD REFERENCE COLUMNS TO TSV FILES")
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY RUN MODE - no files will be modified]\n")

    print(f"Target files: {len(TARGET_FILES)}")
    print(f"Columns to add: {[c[0] for c in NEW_COLUMNS]}")
    print(f"Default values: ref_id='', confidence='none', validated_by='none'")
    print()

    results = []
    for filepath in TARGET_FILES:
        if not filepath.exists():
            print(f"SKIP: {filepath.name} (file not found)")
            continue

        result = add_columns_to_file(filepath, dry_run=args.dry_run)
        results.append(result)

        status = "would add" if args.dry_run else "added"
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
    total_added = sum(len(r["columns_added"]) for r in results)

    print(f"Files processed: {len(results)}")
    print(f"Total rows: {total_rows}")
    print(f"Column additions: {total_added}")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")
    else:
        print("\nDone! All new values are set to empty or 'none'.")
        print("Human review is required to fill in ref_id and confidence values.")


if __name__ == "__main__":
    main()
