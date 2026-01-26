# Issue: Clean up orphaned bibliography entries

## Summary

The bibliography (`data/references/bibliography.json`) contains **562 entries** that are not referenced anywhere in the codebase. These should be investigated and either:
1. Linked via `ref_id` columns in the appropriate data files
2. Removed from the bibliography

## Background

The bibliography was auto-generated from source/DOI columns across all TSV files. However, most data files use inline source citations rather than the `ref_id` lookup system. This creates a mismatch:

| Category | Count |
|----------|-------|
| Total bibliography entries | 1,063 |
| Used via `ref_id` columns | 69 |
| Used via source/DOI columns only | 433 |
| **Truly orphaned** | **562** |

## Files

- **Orphaned entries list**: `data/references/orphaned_entries.json`
  - Contains full details for all 562 orphaned entries
  - Also lists 433 entries referenced via source columns only

## Suggested Actions

### Phase 1: Review orphaned entries
1. Review `orphaned_entries.json` to understand what's there
2. Identify entries that should be kept (may be referenced in report text)
3. Identify entries that can be safely removed

### Phase 2: Populate ref_id columns
For files that have source/DOI columns but empty `ref_id` columns:
- Match source values to bibliography entries
- Populate `ref_id` with the matching bibliography ID
- This would move ~433 entries from "source-only" to "properly linked"

### Phase 3: Clean up bibliography
- Remove truly orphaned entries that aren't needed
- Keep entries that are referenced in report prose (even if not in TSV files)

## Scripts Available

- `scripts/export_orphaned_refs.py` - Regenerates the orphaned entries list
- `scripts/fix_ref_ids.py` - Fixes common ref_id issues (already applied)

## Related

- This issue was created during the ref_id cleanup work
- The `ref_id` system was added to enable proper citation tracking
- Some "orphaned" entries may be valid (referenced in report text, not TSV files)
