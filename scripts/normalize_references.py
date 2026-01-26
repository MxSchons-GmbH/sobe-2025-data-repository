#!/usr/bin/env python3
"""
Normalize References - Standardize all DOI formats to canonical form.

This script normalizes all DOIs in TSV files to the canonical format:
https://doi.org/10.xxxx/yyyy

Input formats handled:
- doi:10.xxxx/yyyy
- http://dx.doi.org/10.xxxx/yyyy
- https://dx.doi.org/10.xxxx/yyyy
- 10.xxxx/yyyy (bare DOI)
- URL-encoded DOIs

Usage:
    python normalize_references.py              # Normalize all DOIs
    python normalize_references.py --dry-run    # Preview changes
    python normalize_references.py --file FILE  # Normalize specific file
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA_DIR, DATA_REFERENCES

# Output paths
NORMALIZATION_REPORT = DATA_REFERENCES / "normalization_report.json"

# Reference column patterns
REF_COLUMNS = ["source", "ref", "references", "reference", "doi", "link", "doi/link"]

# DOI patterns for extraction
DOI_PATTERNS = [
    # dx.doi.org URLs
    r'https?://dx\.doi\.org/(10\.\d{4,}/[^\s,;\]]+)',
    # doi.org URLs (already canonical, but may need cleanup)
    r'https?://doi\.org/(10\.\d{4,}/[^\s,;\]]+)',
    # doi: prefix
    r'doi:(10\.\d{4,}/[^\s,;\]]+)',
    # Bare DOI
    r'^(10\.\d{4,}/[^\s,;\]]+)$',
]


@dataclass
class NormalizationResult:
    """Result of normalizing a single value."""
    file: str
    row: int
    column: str
    original: str
    normalized: str
    change_type: str  # "dx_to_canonical", "doi_prefix", "bare_doi", "url_decode", "no_change"


def extract_and_normalize_doi(value: str) -> tuple[str, str]:
    """
    Extract DOI from a value and return normalized form.
    Returns (normalized_value, change_type).
    """
    if pd.isna(value) or not str(value).strip():
        return "", "empty"

    value = str(value).strip()

    # Check if it's already canonical
    if re.match(r'^https://doi\.org/10\.\d{4,}/', value):
        return value, "no_change"

    # Try each pattern
    for pattern in DOI_PATTERNS:
        match = re.search(pattern, value, re.IGNORECASE)
        if match:
            doi = match.group(1)

            # URL decode if needed
            if '%' in doi:
                doi = unquote(doi)

            # Clean up trailing punctuation
            doi = re.sub(r'[.,;]+$', '', doi)

            # Handle unbalanced parentheses
            suffix = doi.split('/', 1)[1] if '/' in doi else doi
            open_parens = suffix.count('(')
            close_parens = suffix.count(')')
            while close_parens > open_parens and doi.endswith(')'):
                doi = doi[:-1]
                close_parens -= 1

            normalized = f"https://doi.org/{doi}"

            # Determine change type
            if 'dx.doi.org' in value.lower():
                return normalized, "dx_to_canonical"
            elif value.lower().startswith('doi:'):
                return normalized, "doi_prefix"
            elif re.match(r'^10\.\d{4,}/', value):
                return normalized, "bare_doi"
            elif '%' in value:
                return normalized, "url_decode"
            else:
                return normalized, "format_fix"

    # No DOI found
    return value, "not_doi"


def normalize_file(filepath: Path, dry_run: bool = False) -> list[NormalizationResult]:
    """Normalize DOIs in a single TSV file."""
    results = []

    try:
        df = pd.read_csv(filepath, sep='\t', dtype=str)
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return results

    # Find reference columns
    ref_cols = [col for col in df.columns if col.lower() in REF_COLUMNS]

    if not ref_cols:
        return results

    modified = False

    for col in ref_cols:
        for idx in range(len(df)):
            original = df.at[idx, col]
            normalized, change_type = extract_and_normalize_doi(original)

            if change_type not in ["no_change", "not_doi", "empty"]:
                results.append(NormalizationResult(
                    file=filepath.name,
                    row=idx + 2,  # +2 for 1-indexed + header
                    column=col,
                    original=str(original),
                    normalized=normalized,
                    change_type=change_type
                ))

                if not dry_run:
                    df.at[idx, col] = normalized
                    modified = True

    if modified and not dry_run:
        df.to_csv(filepath, sep='\t', index=False)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Normalize DOI formats to canonical https://doi.org/..."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Normalize specific file only"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress detailed output"
    )

    args = parser.parse_args()

    # Find files to process
    if args.file:
        files = [Path(args.file)]
    else:
        files = list(DATA_DIR.rglob("*.tsv"))
        files = [f for f in files if "_metadata" not in str(f)]

    all_results = []

    if not args.quiet:
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Normalizing DOIs in {len(files)} files...\n")

    for filepath in sorted(files):
        results = normalize_file(filepath, args.dry_run)

        if results and not args.quiet:
            print(f"{filepath.name}: {len(results)} normalizations")
            for r in results[:3]:  # Show first 3
                print(f"  Row {r.row}: {r.change_type}")
                print(f"    {r.original[:60]}...")
                print(f"    → {r.normalized[:60]}...")
            if len(results) > 3:
                print(f"  ... and {len(results) - 3} more")

        all_results.extend(results)

    # Summary
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Total normalizations: {len(all_results)}")

    # Count by type
    by_type = {}
    for r in all_results:
        by_type[r.change_type] = by_type.get(r.change_type, 0) + 1

    for change_type, count in sorted(by_type.items()):
        print(f"    {change_type}: {count}")

    # Write report
    if not args.dry_run:
        DATA_REFERENCES.mkdir(parents=True, exist_ok=True)

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_normalizations": len(all_results),
            "by_type": by_type,
            "changes": [
                {
                    "file": r.file,
                    "row": r.row,
                    "column": r.column,
                    "original": r.original,
                    "normalized": r.normalized,
                    "type": r.change_type
                }
                for r in all_results
            ]
        }

        with open(NORMALIZATION_REPORT, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {NORMALIZATION_REPORT}")


if __name__ == "__main__":
    main()
