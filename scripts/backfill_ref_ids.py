#!/usr/bin/env python3
"""
Backfill ref_id columns in TSV files using extraction_audit.json.

This script solves the "orphaned bibliography entries" problem by populating
the ref_id columns in TSV files with the ref_ids that were generated during
bibliography extraction but never written back.

Usage:
    python backfill_ref_ids.py              # Apply backfill
    python backfill_ref_ids.py --dry-run    # Preview changes without modifying
    python backfill_ref_ids.py --report-unmapped  # Generate unmapped_sources.json
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
REFERENCES_DIR = DATA_DIR / "references"
AUDIT_PATH = REFERENCES_DIR / "extraction_audit.json"
BIB_PATH = REFERENCES_DIR / "bibliography.json"
UNMAPPED_OUTPUT = REFERENCES_DIR / "unmapped_sources.json"

# Internal source patterns - these should NOT get ref_ids
INTERNAL_PATTERNS = [
    r'^estimated$',
    r'^computational demands analysis$',
    r'^internal\s',
    r'^s&k$',
    r'^analysis$',
    r'^derived',
    r'^calculated',
    r'^estimates$',
    r'^assumptions$',
    r'estimates,?\s*assumptions',
]


def is_internal_source(value):
    """Check if a source value is an internal reference (not a real citation)."""
    v = value.strip().lower()
    return any(re.match(p, v) for p in INTERNAL_PATTERNS)


def is_text_hash_ref(ref_id):
    """Check if ref_id is a text hash (internal label, not a real reference)."""
    return ref_id.startswith('text_')


def load_extraction_audit():
    """Load the extraction audit JSON."""
    with open(AUDIT_PATH) as f:
        return json.load(f)


def load_bibliography():
    """Load the bibliography JSON."""
    with open(BIB_PATH) as f:
        return json.load(f)


def read_tsv(filepath):
    """Read TSV file and return header + rows."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return [], []

    header = lines[0].rstrip('\n').split('\t')
    rows = []
    for line in lines[1:]:
        # Preserve exact content, just split by tab
        row = line.rstrip('\n').split('\t')
        rows.append(row)

    return header, rows


def write_tsv(filepath, header, rows):
    """Write TSV file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\t'.join(header) + '\n')
        for row in rows:
            f.write('\t'.join(row) + '\n')


def group_extractions_by_file(extractions):
    """Group extractions by file path, then by row number."""
    by_file = defaultdict(lambda: defaultdict(list))

    for ext in extractions:
        filepath = ext['file']
        row_num = ext['row']
        by_file[filepath][row_num].append(ext)

    return by_file


def backfill_file(tsv_path, extractions_by_row, dry_run=False):
    """
    Backfill ref_id columns for a single TSV file.

    Returns: dict with statistics
    """
    header, rows = read_tsv(tsv_path)

    # Find column indices
    try:
        ref_id_idx = header.index('ref_id')
    except ValueError:
        return {'file': str(tsv_path), 'status': 'no_ref_id_column', 'changes': []}

    try:
        supporting_refs_idx = header.index('supporting_refs')
    except ValueError:
        supporting_refs_idx = None

    try:
        ref_note_idx = header.index('ref_note')
    except ValueError:
        ref_note_idx = None

    changes = []

    for row_num, extraction_list in extractions_by_row.items():
        # Row numbers in audit are 1-indexed with header at row 1
        # So row 2 in audit = index 0 in rows list
        idx = row_num - 2

        if idx < 0 or idx >= len(rows):
            changes.append({
                'row': row_num,
                'status': 'row_out_of_range',
                'idx': idx,
                'total_rows': len(rows)
            })
            continue

        row = rows[idx]

        # Ensure row has enough columns
        while len(row) <= ref_id_idx:
            row.append('')

        current_ref_id = row[ref_id_idx].strip()

        # Skip if already has a non-empty, non-"none" ref_id
        if current_ref_id and current_ref_id.lower() not in ['', 'none']:
            changes.append({
                'row': row_num,
                'status': 'already_has_ref_id',
                'existing': current_ref_id
            })
            continue

        # Filter out text_* ref_ids (internal labels)
        valid_refs = []
        skipped_internal = []

        for ext in extraction_list:
            ref_id = ext['ref_id']
            if is_text_hash_ref(ref_id):
                skipped_internal.append({
                    'ref_id': ref_id,
                    'original': ext.get('original', '')
                })
            else:
                valid_refs.append(ref_id)

        if not valid_refs:
            # All refs were internal - optionally populate ref_note
            if skipped_internal and ref_note_idx is not None:
                while len(row) <= ref_note_idx:
                    row.append('')
                if not row[ref_note_idx].strip():
                    # Use original text as note
                    note_text = skipped_internal[0]['original']
                    if not dry_run:
                        row[ref_note_idx] = note_text
                    changes.append({
                        'row': row_num,
                        'status': 'internal_source_noted',
                        'ref_note': note_text,
                        'skipped': skipped_internal
                    })
                else:
                    changes.append({
                        'row': row_num,
                        'status': 'skipped_internal',
                        'skipped': skipped_internal
                    })
            else:
                changes.append({
                    'row': row_num,
                    'status': 'skipped_internal',
                    'skipped': skipped_internal
                })
            continue

        # Populate ref_id with first valid reference
        primary_ref = valid_refs[0]
        if not dry_run:
            row[ref_id_idx] = primary_ref

        change = {
            'row': row_num,
            'status': 'backfilled',
            'ref_id': primary_ref
        }

        # Populate supporting_refs with additional references
        if len(valid_refs) > 1 and supporting_refs_idx is not None:
            while len(row) <= supporting_refs_idx:
                row.append('')
            supporting = ';'.join(valid_refs[1:])
            if not dry_run:
                current_supporting = row[supporting_refs_idx].strip()
                if current_supporting and current_supporting.lower() != 'none':
                    # Append to existing
                    row[supporting_refs_idx] = current_supporting + ';' + supporting
                else:
                    row[supporting_refs_idx] = supporting
            change['supporting_refs'] = valid_refs[1:]

        if skipped_internal:
            change['skipped_internal'] = skipped_internal

        changes.append(change)

    # Write if not dry run and there were changes
    if not dry_run and any(c.get('status') == 'backfilled' for c in changes):
        write_tsv(tsv_path, header, rows)

    return {
        'file': str(tsv_path),
        'status': 'processed',
        'changes': changes
    }


def find_unmapped_sources(bibliography):
    """
    Find source values in TSV files that don't have bibliography entries.
    """
    # Build lookup indices from bibliography
    bib_by_doi = {}
    bib_by_url = {}
    for entry in bibliography['references']:
        ref_id = entry.get('id')
        if 'DOI' in entry:
            bib_by_doi[entry['DOI'].lower()] = ref_id
        if 'URL' in entry:
            bib_by_url[entry['URL'].lower()] = ref_id

    unmapped = []

    for tsv_file in DATA_DIR.rglob('*.tsv'):
        if '_metadata' in str(tsv_file) or 'references' in str(tsv_file):
            continue

        try:
            header, rows = read_tsv(tsv_file)
        except Exception:
            continue

        # Find source-like columns
        source_cols = []
        for i, col in enumerate(header):
            if col.lower() in ['source', 'doi', 'link', 'references', 'ref', 'url']:
                source_cols.append((i, col))

        if not source_cols:
            continue

        for row_idx, row in enumerate(rows):
            row_num = row_idx + 2  # Convert to 1-indexed with header

            for col_idx, col_name in source_cols:
                if col_idx >= len(row):
                    continue

                val = row[col_idx].strip()
                if not val or val.lower() in ['none', '', 'n/a', 'na']:
                    continue

                # Skip internal sources
                if is_internal_source(val):
                    continue

                # Try to match
                matched = False
                matched_ref_id = None

                # Check DOI
                if '10.' in val:
                    doi_match = re.search(r'10\.\d{4,}/[^\s]+', val)
                    if doi_match:
                        doi = doi_match.group(0).rstrip('.,;').lower()
                        if doi in bib_by_doi:
                            matched = True
                            matched_ref_id = bib_by_doi[doi]

                # Check URL
                if not matched:
                    val_lower = val.lower()
                    if val_lower in bib_by_url:
                        matched = True
                        matched_ref_id = bib_by_url[val_lower]

                if not matched:
                    # Categorize the unmapped source
                    category = 'unknown'
                    if val.count('http') > 1 or (val.count(' ') > 3 and 'http' in val):
                        category = 'multi_url'
                    elif 'doi:' in val.lower() or ('10.' in val and 'http' not in val.lower()):
                        category = 'doi_format_issue'
                    elif 'http' in val.lower():
                        category = 'url_not_in_bib'
                    else:
                        category = 'text_reference'

                    unmapped.append({
                        'file': str(tsv_file.relative_to(DATA_DIR)),
                        'row': row_num,
                        'column': col_name,
                        'value': val[:200],  # Truncate long values
                        'category': category
                    })

    return unmapped


def main():
    parser = argparse.ArgumentParser(
        description='Backfill ref_id columns in TSV files from extraction audit'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without modifying files')
    parser.add_argument('--file', type=str,
                        help='Process only this specific file')
    parser.add_argument('--report', action='store_true',
                        help='Generate detailed JSON report')
    parser.add_argument('--report-unmapped', action='store_true',
                        help='Generate unmapped_sources.json')
    args = parser.parse_args()

    print("=" * 60)
    print("Backfill ref_id Columns from Extraction Audit")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY RUN MODE - No files will be modified ***\n")

    # Load data
    print("Loading extraction audit...")
    audit = load_extraction_audit()
    extractions = audit.get('extractions', [])
    print(f"  Total extractions: {len(extractions)}")

    print("Loading bibliography...")
    bibliography = load_bibliography()
    print(f"  Total entries: {len(bibliography['references'])}")

    # Group extractions by file
    by_file = group_extractions_by_file(extractions)
    print(f"  Files with extractions: {len(by_file)}")

    # Process files
    results = []
    stats = {
        'files_processed': 0,
        'rows_backfilled': 0,
        'rows_skipped_internal': 0,
        'rows_already_have_ref_id': 0,
        'rows_out_of_range': 0,
        'supporting_refs_added': 0
    }

    for filename, extractions_by_row in by_file.items():
        # Find the actual file path
        tsv_path = None
        for potential_path in DATA_DIR.rglob('*.tsv'):
            if potential_path.name == filename:
                tsv_path = potential_path
                break

        if tsv_path is None:
            results.append({
                'file': filename,
                'status': 'file_not_found',
                'changes': []
            })
            continue

        # Filter by --file argument if specified
        if args.file and tsv_path.name != args.file:
            continue

        result = backfill_file(tsv_path, extractions_by_row, dry_run=args.dry_run)
        results.append(result)

        # Update stats
        stats['files_processed'] += 1
        for change in result.get('changes', []):
            status = change.get('status')
            if status == 'backfilled':
                stats['rows_backfilled'] += 1
                if 'supporting_refs' in change:
                    stats['supporting_refs_added'] += len(change['supporting_refs'])
            elif status in ['skipped_internal', 'internal_source_noted']:
                stats['rows_skipped_internal'] += 1
            elif status == 'already_has_ref_id':
                stats['rows_already_have_ref_id'] += 1
            elif status == 'row_out_of_range':
                stats['rows_out_of_range'] += 1

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Rows backfilled: {stats['rows_backfilled']}")
    print(f"  Supporting refs added: {stats['supporting_refs_added']}")
    print(f"  Rows skipped (internal): {stats['rows_skipped_internal']}")
    print(f"  Rows skipped (already has ref_id): {stats['rows_already_have_ref_id']}")
    print(f"  Rows out of range: {stats['rows_out_of_range']}")

    # Show sample changes
    print("\n--- Sample Changes ---")
    shown = 0
    for result in results:
        for change in result.get('changes', []):
            if change.get('status') == 'backfilled' and shown < 10:
                print(f"  {result['file']}:{change['row']} -> {change['ref_id']}")
                shown += 1

    if args.report:
        report_path = REFERENCES_DIR / 'backfill_report.json'
        report = {
            '_generated': datetime.now().isoformat(),
            '_dry_run': args.dry_run,
            'stats': stats,
            'results': results
        }
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {report_path}")

    # Handle unmapped sources report
    if args.report_unmapped:
        print("\n" + "=" * 60)
        print("Finding Unmapped Sources")
        print("=" * 60)

        unmapped = find_unmapped_sources(bibliography)

        # Categorize
        by_category = defaultdict(list)
        for item in unmapped:
            by_category[item['category']].append(item)

        print(f"\nUnmapped sources by category:")
        for cat, items in sorted(by_category.items()):
            print(f"  {cat}: {len(items)}")

        output = {
            '_generated': datetime.now().isoformat(),
            '_description': 'TSV source values that could not be matched to bibliography entries',
            'summary': {
                'total': len(unmapped),
                'by_category': {cat: len(items) for cat, items in by_category.items()}
            },
            'unmapped': unmapped
        }

        with open(UNMAPPED_OUTPUT, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\nUnmapped sources saved to: {UNMAPPED_OUTPUT}")

    if args.dry_run:
        print("\n*** DRY RUN COMPLETE - No files were modified ***")
    else:
        print("\n*** BACKFILL COMPLETE ***")

    return stats


if __name__ == "__main__":
    main()
