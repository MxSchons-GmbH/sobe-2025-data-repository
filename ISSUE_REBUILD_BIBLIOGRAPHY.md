# Issue: Rebuild bibliography system from scratch for validation

## Background

The bibliography system has accumulated issues since its initial implementation (commit `ff2b946`). While we've made targeted fixes to improve ref_id quality, a full rebuild from scratch is needed to:
1. Validate that our fixes are comprehensive
2. Ensure no edge cases were missed
3. Create a "golden reference" to compare against

## Current State (after hotfix)

| Metric | Before Fix | After Fix |
|--------|------------|-----------|
| Total entries | 1,063 | 692 |
| Author+year format | ~115 | 242 (35%) |
| URL-based (webpages) | 307 | 189 (27%) |
| Text hash (internal) | ~640 | 261 (38%) |

The fix improved 118 entries from URL-based to proper author+year format by extracting DOIs from publisher URLs.

## What was fixed

1. **DOI extraction from publisher URLs**: Added patterns for Nature, Science, PNAS, bioRxiv, Frontiers, PLoS, Cell, Wiley, Springer, Royal Society, Oxford, IEEE, ScienceDirect, Taylor & Francis, MDPI, eLife, and Annual Reviews.

2. **Proper year handling**: DOI-based refs now use publication year from CrossRef, not extraction date.

## Tasks for full rebuild

- [ ] Archive current `data/references/` as backup
- [ ] Remove all ref_id values from TSV files
- [ ] Clear bibliography.json and extraction_audit.json
- [ ] Run `build_bibliography.py` fresh
- [ ] Run `backfill_ref_ids.py` fresh
- [ ] Compare output with current state
- [ ] Document any discrepancies

## Pre-existing issues to fix during rebuild

1. **Malformed TSV files** (multiline quoted fields):
   - `data/simulations/neuron-simulations.tsv` (line 7)
   - `data/simulations/computational-models.tsv` (line 4)
   - `data/connectomics/brain-scans.tsv` (line 3)
   - `data/recordings/neural-information-rate.tsv` (line 128)

2. **CrossRef 404 errors** (need manual verification):
   - `10.1038/nn` (truncated DOI?)
   - `10.1101/2023.03.14.532674v4` (version suffix issue)
   - `10.1101/2023.06.05.543407v2` (version suffix issue)
   - `10.1101/2020.10.07.20207704v1` (version suffix issue)

## Acceptance criteria

- [ ] All DOIs from recognized publishers have author+year ref_ids
- [ ] Only true webpages without DOIs have URL-based ref_ids
- [ ] No `_2026` suffix on refs with known publication years
- [ ] All TSV files parse without errors
- [ ] Validation passes without failures

## Related

- Original issue: #21
