#!/usr/bin/env python3
"""
Export orphaned bibliography entries to a separate file for investigation.

Orphaned entries are those in bibliography.json that are not referenced by:
1. ref_id columns in TSV files
2. supporting_refs columns in TSV files

Note: Many "orphaned" entries ARE actually referenced via source/DOI columns
in the original data. This script identifies both categories.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
BIB_PATH = DATA_DIR / "references" / "bibliography.json"
OUTPUT_PATH = DATA_DIR / "references" / "orphaned_entries.json"


def load_bibliography():
    """Load the bibliography JSON."""
    with open(BIB_PATH) as f:
        return json.load(f)


def get_used_ref_ids():
    """Get all ref_ids used in TSV files (ref_id and supporting_refs columns)."""
    used_ids = set()

    for tsv_file in DATA_DIR.rglob('*.tsv'):
        try:
            with open(tsv_file, 'r') as f:
                lines = f.readlines()

            if not lines:
                continue

            header = lines[0].strip().split('\t')
            ref_id_col = header.index('ref_id') if 'ref_id' in header else None
            supporting_refs_col = header.index('supporting_refs') if 'supporting_refs' in header else None

            if ref_id_col is None and supporting_refs_col is None:
                continue

            for line in lines[1:]:
                cols = line.strip().split('\t')

                if ref_id_col is not None and ref_id_col < len(cols):
                    ref = cols[ref_id_col].strip()
                    if ref and ref != 'none' and not ref.startswith('internal_'):
                        used_ids.add(ref)

                if supporting_refs_col is not None and supporting_refs_col < len(cols):
                    refs = cols[supporting_refs_col].strip()
                    if refs:
                        for r in refs.split(';'):
                            r = r.strip()
                            if r and r != 'none' and not r.startswith('internal_'):
                                used_ids.add(r)
        except Exception as e:
            print(f"Error processing {tsv_file}: {e}")

    return used_ids


def get_source_column_refs(bib_entries):
    """
    Check which bibliography entries are referenced via source/DOI columns.
    Returns a set of ref_ids that are matched.
    """
    # Build lookup indices
    bib_by_doi = {}
    bib_by_url = {}
    for entry in bib_entries:
        ref_id = entry.get('id')
        if 'DOI' in entry:
            bib_by_doi[entry['DOI'].lower()] = ref_id
        if 'URL' in entry:
            bib_by_url[entry['URL'].lower()] = ref_id

    matched_ids = set()

    for tsv_file in DATA_DIR.rglob('*.tsv'):
        try:
            with open(tsv_file, 'r') as f:
                lines = f.readlines()

            if not lines:
                continue

            header = lines[0].strip().split('\t')
            # Find source-like columns
            source_cols = []
            for i, col in enumerate(header):
                if col.lower() in ['source', 'doi', 'link', 'references', 'ref', 'url']:
                    source_cols.append(i)

            if not source_cols:
                continue

            for line in lines[1:]:
                cols = line.strip().split('\t')
                for col_idx in source_cols:
                    if col_idx < len(cols):
                        val = cols[col_idx].strip().lower()
                        if val:
                            # Check if it's a DOI
                            if '10.' in val:
                                doi_match = re.search(r'10\.\d{4,}/[^\s]+', val)
                                if doi_match:
                                    doi = doi_match.group(0).rstrip('.,;')
                                    if doi in bib_by_doi:
                                        matched_ids.add(bib_by_doi[doi])
                            # Check if it matches a URL
                            if val in bib_by_url:
                                matched_ids.add(bib_by_url[val])
        except Exception as e:
            pass

    return matched_ids


def main():
    print("=" * 60)
    print("Export Orphaned Bibliography Entries")
    print("=" * 60)

    # Load bibliography
    print("\nLoading bibliography...")
    bib = load_bibliography()
    all_ids = {e['id'] for e in bib['references']}
    print(f"  Total entries: {len(all_ids)}")

    # Get used ref_ids
    print("\nScanning TSV files for ref_id usage...")
    used_via_ref_id = get_used_ref_ids()
    print(f"  Used via ref_id/supporting_refs: {len(used_via_ref_id)}")

    # Get source column matches
    print("\nScanning TSV files for source/DOI matches...")
    used_via_source = get_source_column_refs(bib['references'])
    print(f"  Matched via source/DOI columns: {len(used_via_source)}")

    # Calculate categories
    all_used = used_via_ref_id | used_via_source
    truly_orphaned = all_ids - all_used
    referenced_via_source_only = used_via_source - used_via_ref_id

    print(f"\nSummary:")
    print(f"  Total bibliography entries: {len(all_ids)}")
    print(f"  Used via ref_id columns: {len(used_via_ref_id)}")
    print(f"  Used via source/DOI columns only: {len(referenced_via_source_only)}")
    print(f"  Truly orphaned (no references): {len(truly_orphaned)}")

    # Build output structure
    output = {
        "_generated": datetime.now().isoformat(),
        "_description": "Orphaned bibliography entries for investigation",
        "_note": "These entries are in bibliography.json but may not be actively referenced",
        "summary": {
            "total_bibliography_entries": len(all_ids),
            "used_via_ref_id_column": len(used_via_ref_id),
            "used_via_source_doi_column_only": len(referenced_via_source_only),
            "truly_orphaned": len(truly_orphaned)
        },
        "truly_orphaned": sorted(list(truly_orphaned)),
        "referenced_via_source_only": sorted(list(referenced_via_source_only)),
        "entries": {}
    }

    # Add full entry details for truly orphaned
    for entry in bib['references']:
        if entry['id'] in truly_orphaned:
            output['entries'][entry['id']] = entry

    # Save output
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved orphaned entries to: {OUTPUT_PATH}")
    print(f"  - {len(truly_orphaned)} truly orphaned entries (with full details)")
    print(f"  - {len(referenced_via_source_only)} entries used via source columns only (ids listed)")

    return output


if __name__ == "__main__":
    main()
