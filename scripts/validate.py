#!/usr/bin/env python3
"""
SOBE 2025 Data Repository - Quality Validation Script

Runs comprehensive quality checks before major pushes to ensure:
- All figures have both SVG and PNG formats
- No zero-size files exist
- Metadata matches actual files on disk
- Data files are valid and readable
- Taxonomy values are correct
- Naming conventions are followed
- SEO meta tags are present in HTML files
- Heading hierarchy is correct (H1 → H2 → H3)
- External links have proper security attributes
- Figure titles are descriptive enough for SEO/alt text

Usage:
    python3 validate.py          # Run all checks
    python3 validate.py --strict # Fail on warnings too
    python3 validate.py --ci     # Skip checks requiring generated content
    python3 validate.py --fix    # Auto-fix some issues (future)
"""

import json
import re
import sys
from pathlib import Path
from typing import NamedTuple, Optional, List, Tuple

import paths


# Known exceptions - legacy assets that don't follow all conventions
# These should be documented and ideally fixed over time
KNOWN_EXCEPTIONS = {
    "svg_png_pairs": [
        # Hand-drawn figures - PNG only, no SVG source available
        "hand-drawn/brain-emulation-feature-illustration.png",
        "hand-drawn/neural-recording-scale-comparison.png",
    ],
}

# ANSI color codes for terminal output
class Colors:
    PASS = "\033[92m"  # Green
    FAIL = "\033[91m"  # Red
    WARN = "\033[93m"  # Yellow
    INFO = "\033[94m"  # Blue
    RESET = "\033[0m"
    BOLD = "\033[1m"


class CheckResult(NamedTuple):
    """Result of a single validation check."""
    status: str  # 'pass', 'fail', 'warn', 'skip'
    message: str
    details: List[str] = []


class ValidationReport:
    """Aggregates validation results and provides summary."""

    def __init__(self):
        self.results: List[Tuple[str, CheckResult]] = []
        self.current_tier = ""

    def add(self, check_name: str, result: CheckResult):
        self.results.append((check_name, result))

    def print_tier_header(self, tier: str, description: str):
        self.current_tier = tier
        print(f"\n{Colors.BOLD}{tier}: {description}{Colors.RESET}")
        print("-" * 50)

    def print_result(self, check_name: str, result: CheckResult):
        if result.status == "pass":
            icon = f"{Colors.PASS}[PASS]{Colors.RESET}"
        elif result.status == "fail":
            icon = f"{Colors.FAIL}[FAIL]{Colors.RESET}"
        elif result.status == "warn":
            icon = f"{Colors.WARN}[WARN]{Colors.RESET}"
        else:
            icon = f"{Colors.INFO}[SKIP]{Colors.RESET}"

        print(f"{icon} {check_name}: {result.message}")
        for detail in result.details[:10]:  # Limit details shown
            print(f"       - {detail}")
        if len(result.details) > 10:
            print(f"       ... and {len(result.details) - 10} more")

    def summary(self) -> Tuple[int, int, int]:
        """Returns (fail_count, warn_count, pass_count)."""
        fails = sum(1 for _, r in self.results if r.status == "fail")
        warns = sum(1 for _, r in self.results if r.status == "warn")
        passes = sum(1 for _, r in self.results if r.status == "pass")
        return fails, warns, passes

    def print_summary(self):
        fails, warns, passes = self.summary()
        total = fails + warns + passes
        print("\n" + "=" * 50)
        print(f"{Colors.BOLD}Summary: ", end="")
        if fails > 0:
            print(f"{Colors.FAIL}{fails} FAIL{Colors.RESET}, ", end="")
        else:
            print(f"0 FAIL, ", end="")
        if warns > 0:
            print(f"{Colors.WARN}{warns} WARN{Colors.RESET}, ", end="")
        else:
            print(f"0 WARN, ", end="")
        print(f"{Colors.PASS}{passes} PASS{Colors.RESET}")
        print("=" * 50)


def load_json(filepath: Path) -> Optional[dict]:
    """Safely load a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"{Colors.FAIL}Error loading {filepath}: {e}{Colors.RESET}")
        return None


# =============================================================================
# TIER 1: Critical Checks
# =============================================================================

def check_svg_png_pairs(report: ValidationReport) -> CheckResult:
    """Verify every generated figure has both SVG and PNG formats."""
    figures_dir = paths.OUTPUT_FIGURES
    missing_pairs = []
    known_exceptions = []
    valid_pairs = 0

    # Get known exceptions for this check
    exceptions = set(KNOWN_EXCEPTIONS.get("svg_png_pairs", []))

    # Collect all PNG files across all subdirectories
    png_files = list(figures_dir.rglob("*.png"))
    svg_files = {f.stem: f for f in figures_dir.rglob("*.svg")}

    for png_file in png_files:
        stem = png_file.stem
        # Look for corresponding SVG in the same directory
        expected_svg = png_file.with_suffix(".svg")
        rel_path = str(png_file.relative_to(figures_dir))

        if expected_svg.exists():
            valid_pairs += 1
        elif rel_path in exceptions:
            known_exceptions.append(rel_path)
        else:
            # Report relative path from figures/generated
            missing_pairs.append(f"{rel_path} (missing .svg)")

    # Also check for orphan SVGs (SVG without PNG)
    png_stems = {f.stem: f for f in png_files}
    for svg_file in figures_dir.rglob("*.svg"):
        if svg_file.stem not in [p.stem for p in png_files if p.parent == svg_file.parent]:
            rel_path = svg_file.relative_to(figures_dir)
            missing_pairs.append(f"{rel_path} (missing .png)")

    if missing_pairs:
        return CheckResult(
            "fail",
            f"{len(missing_pairs)} figures missing format pair",
            missing_pairs
        )

    if known_exceptions:
        return CheckResult(
            "pass",
            f"{valid_pairs} pairs valid, {len(known_exceptions)} known exceptions",
            [f"(known exception) {e}" for e in known_exceptions[:3]]
        )

    return CheckResult("pass", f"All {valid_pairs} figures have both SVG and PNG")


def check_zero_size_files(report: ValidationReport) -> CheckResult:
    """Detect any zero-byte output files."""
    output_dir = paths.OUTPUT_ROOT
    zero_files = []
    checked = 0

    for ext in ["*.png", "*.svg", "*.csv", "*.json"]:
        for f in output_dir.rglob(ext):
            checked += 1
            if f.stat().st_size == 0:
                zero_files.append(str(f.relative_to(output_dir)))

    if zero_files:
        return CheckResult("fail", f"{len(zero_files)} zero-size files found", zero_files)
    return CheckResult("pass", f"No zero-size files among {checked} checked")


def check_figures_metadata_sync(report: ValidationReport) -> CheckResult:
    """Verify every metadata entry has a corresponding file."""
    metadata_path = paths.OUTPUT_FIGURES_METADATA
    data = load_json(metadata_path)
    if not data:
        return CheckResult("fail", "Could not load figures-metadata.json")

    missing_files = []
    found_files = 0

    for fig in data.get("figures", []):
        filename = fig.get("filename", "")
        fig_path = fig.get("path", "")
        fig_id = fig.get("id", "unknown")

        # Construct full path - path is relative to data-and-figures/
        full_dir = paths.OUTPUT_ROOT / fig_path
        png_path = full_dir / f"{filename}.png"

        if not png_path.exists():
            missing_files.append(f"{fig_id}: {fig_path}/{filename}.png")
        else:
            found_files += 1

    if missing_files:
        return CheckResult(
            "fail",
            f"{len(missing_files)} metadata entries have no file",
            missing_files
        )
    return CheckResult("pass", f"All {found_files} metadata entries have files")


def check_orphan_figures(report: ValidationReport) -> CheckResult:
    """Find generated figures not listed in metadata."""
    metadata_path = paths.OUTPUT_FIGURES_METADATA
    data = load_json(metadata_path)
    if not data:
        return CheckResult("fail", "Could not load figures-metadata.json")

    # Build set of expected files from metadata
    expected_files = set()
    for fig in data.get("figures", []):
        filename = fig.get("filename", "")
        fig_path = fig.get("path", "")
        # Store relative path from OUTPUT_ROOT
        expected_files.add(f"{fig_path}/{filename}.png")

    # Find all actual PNG files
    orphans = []
    figures_dir = paths.OUTPUT_FIGURES
    for png in figures_dir.rglob("*.png"):
        rel_path = f"figures/generated/{png.relative_to(figures_dir)}"
        # Normalize path separators
        rel_path = rel_path.replace("\\", "/")
        if rel_path not in expected_files:
            orphans.append(rel_path)

    if orphans:
        return CheckResult(
            "warn",
            f"{len(orphans)} figures not in metadata",
            orphans
        )
    return CheckResult("pass", "All generated figures are in metadata")


# =============================================================================
# TIER 2: Data Quality Checks
# =============================================================================

def check_data_files_exist(report: ValidationReport) -> CheckResult:
    """Verify all referenced CSV files exist and are readable."""
    metadata_path = paths.OUTPUT_DATA_METADATA
    data = load_json(metadata_path)
    if not data:
        return CheckResult("fail", "Could not load data-metadata.json")

    missing = []
    readable = 0

    for category in data.get("categories", []):
        for dataset in category.get("datasets", []):
            filename = dataset.get("filename", "")
            data_path = dataset.get("path", "data")
            dataset_id = dataset.get("id", "unknown")

            # Path is relative to data-and-figures/ (OUTPUT_ROOT)
            full_path = paths.OUTPUT_ROOT / data_path / filename

            if not full_path.exists():
                missing.append(f"{dataset_id}: {data_path}/{filename}")
            else:
                # Try to read first line to verify it's accessible
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        f.readline()
                    readable += 1
                except Exception as e:
                    missing.append(f"{dataset_id}: unreadable ({e})")

    if missing:
        return CheckResult("fail", f"{len(missing)} data files missing/unreadable", missing)
    return CheckResult("pass", f"All {readable} data files exist and readable")


def check_data_file_not_empty(report: ValidationReport) -> CheckResult:
    """Warn if data files have very few rows."""
    data_dir = paths.DATA_DIR
    low_row_files = []
    checked = 0

    for tsv_file in data_dir.rglob("*.tsv"):
        # Skip _metadata directory
        if "_metadata" in str(tsv_file):
            continue
        checked += 1
        try:
            with open(tsv_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # Subtract 1 for header
            data_rows = len(lines) - 1
            if data_rows < 2:
                rel_path = tsv_file.relative_to(data_dir)
                low_row_files.append(f"{rel_path}: {data_rows} data rows")
        except Exception:
            pass

    if low_row_files:
        return CheckResult(
            "warn",
            f"{len(low_row_files)} files with very few rows",
            low_row_files
        )
    return CheckResult("pass", f"All {checked} TSV files have sufficient data")


def check_source_data_files(report: ValidationReport) -> CheckResult:
    """Verify all source data files in paths.DATA_FILES exist."""
    missing = []
    found = 0

    for name, filepath in paths.DATA_FILES.items():
        if not filepath.exists():
            missing.append(f"{name}: {filepath.name}")
        else:
            found += 1

    if missing:
        return CheckResult("fail", f"{len(missing)} source data files missing", missing)
    return CheckResult("pass", f"All {found} source data files exist")


def check_data_metadata_files(report: ValidationReport) -> CheckResult:
    """Verify every TSV data file has a corresponding metadata JSON file."""
    data_dir = paths.DATA_DIR
    metadata_dir = paths.DATA_METADATA
    missing = []
    found = 0

    for tsv_file in data_dir.rglob("*.tsv"):
        # Skip _metadata directory
        if "_metadata" in str(tsv_file):
            continue

        # Get relative path from data dir
        relative = tsv_file.relative_to(data_dir)
        # Construct expected metadata path
        metadata_path = metadata_dir / relative.with_suffix(".json")

        if not metadata_path.exists():
            missing.append(f"{relative} -> missing {metadata_path.relative_to(data_dir)}")
        else:
            found += 1

    if missing:
        return CheckResult(
            "fail",
            f"{len(missing)} data files missing metadata",
            missing
        )
    return CheckResult("pass", f"All {found} data files have metadata")


def check_tsv_format(report: ValidationReport) -> CheckResult:
    """Validate TSV files have consistent column counts and valid format."""
    data_dir = paths.DATA_DIR
    issues = []
    checked = 0

    for tsv_file in data_dir.rglob("*.tsv"):
        if "_metadata" in str(tsv_file):
            continue
        checked += 1
        rel_path = tsv_file.relative_to(data_dir)

        try:
            with open(tsv_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                issues.append(f"{rel_path}: empty file")
                continue

            # Check for BOM
            if lines[0].startswith('\ufeff'):
                issues.append(f"{rel_path}: contains BOM character")

            # Check for rows with MORE columns than header (indicates data corruption)
            # Rows with fewer columns are allowed (sparse data with trailing empty fields)
            header_cols = len(lines[0].rstrip('\n\r').split('\t'))
            for i, line in enumerate(lines[1:], start=2):
                # Skip empty lines
                if not line.strip():
                    continue
                cols = len(line.rstrip('\n\r').split('\t'))
                if cols > header_cols:
                    issues.append(f"{rel_path}:{i}: {cols} cols (expected max {header_cols})")
                    break  # One error per file

            # Check trailing whitespace on lines
            for i, line in enumerate(lines, start=1):
                stripped = line.rstrip('\n\r')
                if stripped != stripped.rstrip(' \t'):
                    issues.append(f"{rel_path}:{i}: trailing whitespace")
                    break

        except Exception as e:
            issues.append(f"{rel_path}: read error: {e}")

    if issues:
        return CheckResult("warn", f"{len(issues)} TSV format issues", issues)
    return CheckResult("pass", f"All {checked} TSV files well-formed")


# =============================================================================
# TIER 3: Consistency Checks
# =============================================================================

def check_organism_taxonomy(report: ValidationReport) -> CheckResult:
    """Verify all organism tags are valid."""
    metadata_path = paths.OUTPUT_FIGURES_METADATA
    data = load_json(metadata_path)
    if not data:
        return CheckResult("fail", "Could not load figures-metadata.json")

    valid_organisms = {org["id"] for org in data.get("organisms", [])}
    invalid = []

    for fig in data.get("figures", []):
        fig_id = fig.get("id", "unknown")
        for org in fig.get("organism", []):
            if org not in valid_organisms:
                invalid.append(f"{fig_id}: invalid organism '{org}'")

    if invalid:
        return CheckResult("fail", f"{len(invalid)} invalid organism tags", invalid)
    return CheckResult("pass", f"All organism tags are valid (from {len(valid_organisms)} defined)")


def check_type_taxonomy(report: ValidationReport) -> CheckResult:
    """Verify all type tags are valid."""
    metadata_path = paths.OUTPUT_FIGURES_METADATA
    data = load_json(metadata_path)
    if not data:
        return CheckResult("fail", "Could not load figures-metadata.json")

    valid_types = {t["id"] for t in data.get("types", [])}
    invalid = []

    for fig in data.get("figures", []):
        fig_id = fig.get("id", "unknown")
        for t in fig.get("type", []):
            if t not in valid_types:
                invalid.append(f"{fig_id}: invalid type '{t}'")

    if invalid:
        return CheckResult("fail", f"{len(invalid)} invalid type tags", invalid)
    return CheckResult("pass", f"All type tags are valid (from {len(valid_types)} defined)")


def check_id_uniqueness(report: ValidationReport) -> CheckResult:
    """Verify no duplicate IDs across metadata files."""
    all_ids = []

    # Figures metadata
    figures_meta = load_json(paths.OUTPUT_FIGURES_METADATA)
    if figures_meta:
        all_ids.extend((f["id"], "figures") for f in figures_meta.get("figures", []))

    # Hand-drawn metadata
    hand_drawn_meta = load_json(paths.OUTPUT_HAND_DRAWN_METADATA)
    if hand_drawn_meta:
        all_ids.extend((f["id"], "hand-drawn") for f in hand_drawn_meta.get("figures", []))

    # Check for duplicates
    seen = {}
    duplicates = []
    for id_, source in all_ids:
        if id_ in seen:
            duplicates.append(f"'{id_}' in both {seen[id_]} and {source}")
        else:
            seen[id_] = source

    if duplicates:
        return CheckResult("fail", f"{len(duplicates)} duplicate IDs found", duplicates)
    return CheckResult("pass", f"All {len(all_ids)} IDs are unique")


def check_license_consistency(report: ValidationReport) -> CheckResult:
    """Verify all metadata files have license information."""
    files_to_check = [
        ("figures", paths.OUTPUT_FIGURES_METADATA),
        ("data", paths.OUTPUT_DATA_METADATA),
        ("hand-drawn", paths.OUTPUT_HAND_DRAWN_METADATA),
    ]

    missing_license = []

    for name, filepath in files_to_check:
        data = load_json(filepath)
        if data and "license" not in data:
            missing_license.append(name)

    if missing_license:
        return CheckResult("warn", f"{len(missing_license)} files missing license", missing_license)
    return CheckResult("pass", "All metadata files have license information")


def check_description_quality(report: ValidationReport) -> CheckResult:
    """Warn about empty or very short descriptions."""
    poor_descriptions = []

    # Check figures metadata
    figures_meta = load_json(paths.OUTPUT_FIGURES_METADATA)
    if figures_meta:
        for fig in figures_meta.get("figures", []):
            desc = fig.get("description", "")
            if len(desc) < 20:
                poor_descriptions.append(f"{fig['id']}: description too short ({len(desc)} chars)")

    if poor_descriptions:
        return CheckResult("warn", f"{len(poor_descriptions)} figures with poor descriptions", poor_descriptions)
    return CheckResult("pass", "All figures have adequate descriptions")


# =============================================================================
# TIER 4: Reporting Checks
# =============================================================================

def check_file_sizes(report: ValidationReport) -> CheckResult:
    """Report on file sizes for monitoring."""
    figures_dir = paths.OUTPUT_FIGURES

    total_png_size = 0
    total_svg_size = 0
    total_webp_size = 0
    total_avif_size = 0
    png_count = 0
    svg_count = 0
    webp_count = 0
    avif_count = 0

    for png in figures_dir.rglob("*.png"):
        total_png_size += png.stat().st_size
        png_count += 1

    for svg in figures_dir.rglob("*.svg"):
        total_svg_size += svg.stat().st_size
        svg_count += 1

    for webp in figures_dir.rglob("*.webp"):
        total_webp_size += webp.stat().st_size
        webp_count += 1

    for avif in figures_dir.rglob("*.avif"):
        total_avif_size += avif.stat().st_size
        avif_count += 1

    png_mb = total_png_size / (1024 * 1024)
    svg_mb = total_svg_size / (1024 * 1024)
    webp_mb = total_webp_size / (1024 * 1024)
    avif_mb = total_avif_size / (1024 * 1024)

    details = []
    if webp_count > 0:
        savings = (1 - webp_mb / png_mb) * 100 if png_mb > 0 else 0
        details.append(f"WebP: {webp_count} files ({webp_mb:.1f}MB, {savings:.0f}% smaller than PNG)")
    if avif_count > 0:
        savings = (1 - avif_mb / png_mb) * 100 if png_mb > 0 else 0
        details.append(f"AVIF: {avif_count} files ({avif_mb:.1f}MB, {savings:.0f}% smaller than PNG)")

    return CheckResult(
        "pass",
        f"{png_count} PNGs ({png_mb:.1f}MB), {svg_count} SVGs ({svg_mb:.1f}MB)",
        details
    )


def check_web_format_coverage(report: ValidationReport) -> CheckResult:
    """Check that generated figures have WebP and AVIF versions."""
    figures_dir = paths.OUTPUT_FIGURES

    # Get all PNG files (the baseline)
    png_files = list(figures_dir.rglob("*.png"))
    missing_webp = []
    missing_avif = []

    for png in png_files:
        webp_path = png.with_suffix(".webp")
        avif_path = png.with_suffix(".avif")

        rel_path = str(png.relative_to(figures_dir))

        if not webp_path.exists():
            missing_webp.append(rel_path)
        if not avif_path.exists():
            missing_avif.append(rel_path)

    total_missing = len(missing_webp) + len(missing_avif)

    if total_missing > 0:
        details = []
        if missing_webp:
            details.append(f"{len(missing_webp)} missing WebP files")
        if missing_avif:
            details.append(f"{len(missing_avif)} missing AVIF files")
        # Show first few missing files
        details.extend(missing_webp[:3] + missing_avif[:3])

        return CheckResult(
            "warn",
            f"{total_missing} web format files missing (run figure generation)",
            details
        )

    return CheckResult(
        "pass",
        f"All {len(png_files)} figures have WebP and AVIF versions"
    )


def check_hand_drawn_files(report: ValidationReport) -> CheckResult:
    """Check hand-drawn figures have both PNG and SVG."""
    metadata_path = paths.OUTPUT_HAND_DRAWN_METADATA
    data = load_json(metadata_path)
    if not data:
        return CheckResult("fail", "Could not load hand-drawn-metadata.json")

    hand_drawn_dir = paths.OUTPUT_FIGURES_HAND_DRAWN
    missing = []
    found = 0

    for fig in data.get("figures", []):
        if fig.get("id") == "_instructions":
            continue
        filename = fig.get("filename", "")
        fig_id = fig.get("id", "unknown")

        png_path = hand_drawn_dir / f"{filename}.png"
        svg_path = hand_drawn_dir / f"{filename}.svg"

        if not png_path.exists() and not svg_path.exists():
            missing.append(f"{fig_id}: no files found")
        elif not png_path.exists():
            missing.append(f"{fig_id}: missing PNG")
        elif not svg_path.exists():
            missing.append(f"{fig_id}: missing SVG")
        else:
            found += 1

    if missing:
        # This is expected since hand-drawn is a template
        return CheckResult(
            "warn",
            f"{len(missing)} hand-drawn entries without files (may be template)",
            missing[:5]  # Only show first 5
        )
    return CheckResult("pass", f"All {found} hand-drawn figures have PNG+SVG")


def check_orphan_hand_drawn_figures(report: ValidationReport) -> CheckResult:
    """Find hand-drawn figures not listed in metadata."""
    metadata_path = paths.OUTPUT_HAND_DRAWN_METADATA
    data = load_json(metadata_path)
    if not data:
        return CheckResult("fail", "Could not load hand-drawn-metadata.json")

    # Build set of expected filenames from metadata
    expected_files = set()
    for fig in data.get("figures", []):
        if fig.get("id", "").startswith("_"):
            continue  # Skip template entries
        filename = fig.get("filename", "")
        if filename:
            expected_files.add(f"{filename}.png")
            expected_files.add(f"{filename}.svg")

    # Find all actual files in hand-drawn directory
    hand_drawn_dir = paths.OUTPUT_FIGURES_HAND_DRAWN
    orphans = []

    # Skip non-figure files like _metadata.json
    skip_files = {"_metadata.json"}

    for f in hand_drawn_dir.iterdir():
        if f.name in skip_files:
            continue
        if f.suffix.lower() in [".png", ".svg"]:
            if f.name not in expected_files:
                orphans.append(f.name)

    if orphans:
        return CheckResult(
            "fail",
            f"{len(orphans)} hand-drawn figures not in metadata",
            orphans
        )
    return CheckResult("pass", "All hand-drawn figures are in metadata")


def check_stale_figures(report: ValidationReport) -> CheckResult:
    """Warn if source data is newer than generated figures."""
    from datetime import datetime

    # Key data files that affect figures
    source_files = [
        paths.DATA_FILES.get("neuron_simulations"),
        paths.DATA_FILES.get("neural_recordings"),
        paths.DATA_FILES.get("brain_scans"),
        paths.DATA_FILES.get("ai_compute"),
        paths.DATA_FILES.get("storage_costs"),
    ]

    figures_dir = paths.OUTPUT_FIGURES
    if not figures_dir.exists():
        return CheckResult("skip", "No generated figures directory")

    # Find newest source file
    newest_source = 0
    newest_source_name = ""
    for src in source_files:
        if src and src.exists():
            mtime = src.stat().st_mtime
            if mtime > newest_source:
                newest_source = mtime
                newest_source_name = src.name

    if newest_source == 0:
        return CheckResult("skip", "No source data files found")

    # Find oldest figure
    oldest_figure = float('inf')
    oldest_figure_name = ""
    figure_count = 0
    for fig in figures_dir.glob("*.svg"):
        figure_count += 1
        mtime = fig.stat().st_mtime
        if mtime < oldest_figure:
            oldest_figure = mtime
            oldest_figure_name = fig.name

    if figure_count == 0:
        return CheckResult("skip", "No figures found")

    # Compare timestamps
    if newest_source > oldest_figure:
        src_time = datetime.fromtimestamp(newest_source).strftime("%Y-%m-%d %H:%M")
        fig_time = datetime.fromtimestamp(oldest_figure).strftime("%Y-%m-%d %H:%M")
        return CheckResult(
            "warn",
            "Figures may be stale",
            [f"Source '{newest_source_name}' ({src_time}) newer than '{oldest_figure_name}' ({fig_time})"]
        )

    return CheckResult("pass", f"All {figure_count} figures up-to-date with source data")


# =============================================================================
# TIER 5: Bibliography & Reference Checks
# =============================================================================

def check_bibliography_exists(report: ValidationReport) -> CheckResult:
    """Verify bibliography.json exists and is valid JSON."""
    bib_path = paths.DATA_REFERENCES / "bibliography.json"

    if not bib_path.exists():
        return CheckResult("fail", "bibliography.json not found")

    data = load_json(bib_path)
    if not data:
        return CheckResult("fail", "bibliography.json is invalid JSON")

    refs = data.get("references", [])
    if not refs:
        return CheckResult("warn", "bibliography.json has no references")

    return CheckResult("pass", f"bibliography.json valid with {len(refs)} references")


def check_bibliography_schema(report: ValidationReport) -> CheckResult:
    """Verify bibliography entries have required CSL-JSON fields."""
    bib_path = paths.DATA_REFERENCES / "bibliography.json"
    data = load_json(bib_path)
    if not data:
        return CheckResult("skip", "Could not load bibliography.json")

    refs = data.get("references", [])
    issues = []

    required_fields = ["id", "type", "title"]

    for ref in refs:
        ref_id = ref.get("id", "unknown")

        # Check required fields
        for field in required_fields:
            if field not in ref or not ref[field]:
                issues.append(f"{ref_id}: missing required field '{field}'")

        # Check type is valid CSL type
        valid_types = {
            "article-journal", "article", "book", "chapter", "paper-conference",
            "report", "thesis", "webpage", "dataset", "software",
            "personal_communication", "post-weblog"
        }
        if ref.get("type") and ref["type"] not in valid_types:
            issues.append(f"{ref_id}: unknown type '{ref['type']}'")

        # Check DOI format if present
        doi = ref.get("DOI", "")
        if doi and not doi.startswith("10."):
            issues.append(f"{ref_id}: invalid DOI format '{doi[:30]}'")

    if issues:
        return CheckResult("warn", f"{len(issues)} bibliography schema issues", issues[:20])
    return CheckResult("pass", f"All {len(refs)} bibliography entries have valid schema")


def check_bibliography_duplicates(report: ValidationReport) -> CheckResult:
    """Check for duplicate DOIs or URLs in bibliography."""
    bib_path = paths.DATA_REFERENCES / "bibliography.json"
    data = load_json(bib_path)
    if not data:
        return CheckResult("skip", "Could not load bibliography.json")

    refs = data.get("references", [])
    doi_seen = {}
    url_seen = {}
    duplicates = []

    for ref in refs:
        ref_id = ref.get("id", "unknown")

        # Check DOI duplicates
        doi = ref.get("DOI", "")
        if doi:
            if doi in doi_seen:
                duplicates.append(f"Duplicate DOI '{doi}': {doi_seen[doi]} and {ref_id}")
            else:
                doi_seen[doi] = ref_id

        # Check URL duplicates (for non-DOI entries)
        if not doi:
            url = ref.get("URL", "")
            if url:
                if url in url_seen:
                    duplicates.append(f"Duplicate URL: {url_seen[url]} and {ref_id}")
                else:
                    url_seen[url] = ref_id

    if duplicates:
        return CheckResult("warn", f"{len(duplicates)} duplicate entries", duplicates[:10])
    return CheckResult("pass", f"No duplicate DOIs/URLs among {len(refs)} entries")


def check_ref_id_format(report: ValidationReport) -> CheckResult:
    """Check that ref_ids follow the author2024 naming convention."""
    bib_path = paths.DATA_REFERENCES / "bibliography.json"
    data = load_json(bib_path)
    if not data:
        return CheckResult("skip", "Could not load bibliography.json")

    refs = data.get("references", [])
    issues = []

    # Pattern: lowercase letters/underscores, ending with 4-digit year or 'nd'
    # Examples: stevenson2011, aws_pricing_2024, internal_estimate_2024
    valid_pattern = re.compile(r'^[a-z][a-z0-9_]*(\d{4}|nd)[a-z]?$')

    for ref in refs:
        ref_id = ref.get("id", "")
        if not valid_pattern.match(ref_id):
            # Allow some flexibility - just warn about obviously bad IDs
            if not re.match(r'^[a-z0-9_]+$', ref_id):
                issues.append(f"'{ref_id}' contains invalid characters")
            elif len(ref_id) < 5:
                issues.append(f"'{ref_id}' too short")

    if issues:
        return CheckResult("warn", f"{len(issues)} ref_id format issues", issues[:10])
    return CheckResult("pass", f"All {len(refs)} ref_ids follow naming convention")


def check_dist_bibliography_sync(report: ValidationReport) -> CheckResult:
    """Verify dist/references/bibliography.json exists and matches source."""
    source_path = paths.DATA_REFERENCES / "bibliography.json"
    dist_path = paths.OUTPUT_REFERENCES / "bibliography.json"

    if not source_path.exists():
        return CheckResult("skip", "Source bibliography.json not found")

    if not dist_path.exists():
        return CheckResult("fail", "dist/references/bibliography.json not found - run: cp data/references/bibliography.json dist/references/")

    # Compare file contents
    source_content = source_path.read_bytes()
    dist_content = dist_path.read_bytes()

    if source_content != dist_content:
        return CheckResult(
            "fail",
            "dist/references/bibliography.json out of sync with source",
            ["Run: cp data/references/bibliography.json dist/references/"]
        )

    return CheckResult("pass", "dist/references/bibliography.json in sync with source")


# Valid values for reference tracking columns
VALID_CONFIDENCE_VALUES = {"measured", "derived", "estimated", "assumed", "none", ""}
VALID_VALIDATED_BY_VALUES = {"human", "ai", "human+ai", "none", ""}

# TSV files with reference tracking columns
REFERENCE_TRACKING_FILES = [
    paths.DATA_DIR / "parameters" / "shared.tsv",
    paths.DATA_DIR / "formulas" / "costs.tsv",
    paths.DATA_DIR / "formulas" / "storage.tsv",
    paths.DATA_DIR / "formulas" / "connectomics.tsv",
]


def check_tsv_column_values(report: ValidationReport) -> CheckResult:
    """Validate that confidence and validated_by columns have valid values."""
    import csv

    issues = []

    for filepath in REFERENCE_TRACKING_FILES:
        if not filepath.exists():
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                filename = filepath.name

                for row_num, row in enumerate(reader, start=2):  # +2 for 1-indexed + header
                    # Check confidence column
                    if "confidence" in row:
                        val = (row["confidence"] or "").strip()
                        if val not in VALID_CONFIDENCE_VALUES:
                            issues.append(
                                f"{filename}:{row_num}: Invalid confidence value '{val}' "
                                f"(valid: {', '.join(sorted(VALID_CONFIDENCE_VALUES - {''}))})"
                            )

                    # Check validated_by column
                    if "validated_by" in row:
                        val = (row["validated_by"] or "").strip()
                        if val not in VALID_VALIDATED_BY_VALUES:
                            issues.append(
                                f"{filename}:{row_num}: Invalid validated_by value '{val}' "
                                f"(valid: {', '.join(sorted(VALID_VALIDATED_BY_VALUES - {''}))})"
                            )
        except Exception as e:
            issues.append(f"{filepath.name}: Could not read file - {e}")

    if issues:
        return CheckResult("fail", f"{len(issues)} invalid column values found", issues)

    return CheckResult("pass", "All confidence and validated_by values are valid")


# =============================================================================
# TIER 6: SEO & Accessibility Checks
# =============================================================================

# Required meta tags for SEO compliance
REQUIRED_META_TAGS = [
    ("description", "meta[name='description']"),
    ("og:title", "meta[property='og:title']"),
    ("og:description", "meta[property='og:description']"),
    ("og:image", "meta[property='og:image']"),
    ("twitter:card", "meta[name='twitter:card']"),
    ("robots", "meta[name='robots']"),
]

# Minimum acceptable title length for SEO
MIN_TITLE_LENGTH = 15

# SEO length limits for various fields
SEO_LENGTH_LIMITS = {
    "title": 60,              # Google SERP truncates after ~60 chars
    "description": 160,       # Google SERP truncates after ~160 chars
    "og:title": 90,           # Facebook/LinkedIn truncates after ~90 chars
    "og:description": 200,    # Facebook truncates after ~200 chars
    "twitter:title": 70,      # X/Twitter truncates after ~70 chars
    "twitter:description": 200,  # X/Twitter truncates after ~200 chars
    "alt": 125,               # Screen readers work best with ≤125 chars
}


def check_html_meta_tags(report: ValidationReport) -> CheckResult:
    """Verify HTML files have required SEO meta tags."""
    html_files = [
        paths.OUTPUT_ROOT / "figures.html",
        paths.OUTPUT_ROOT / "data.html",
    ]

    missing = []

    for html_file in html_files:
        if not html_file.exists():
            missing.append(f"{html_file.name}: file not found")
            continue

        content = html_file.read_text(encoding="utf-8")
        filename = html_file.name

        # Check for required meta tags
        for tag_name, _ in REQUIRED_META_TAGS:
            if tag_name.startswith("og:"):
                pattern = rf'<meta\s+property=["\']og:{tag_name[3:]}["\']'
            else:
                pattern = rf'<meta\s+name=["\']?{tag_name}["\']?'

            if not re.search(pattern, content, re.IGNORECASE):
                missing.append(f"{filename}: missing {tag_name}")

    if missing:
        return CheckResult("fail", f"{len(missing)} missing meta tags", missing)
    return CheckResult("pass", f"All {len(html_files)} HTML files have required SEO tags")


def check_html_lang_attribute(report: ValidationReport) -> CheckResult:
    """Verify HTML files have lang attribute."""
    html_files = [
        paths.OUTPUT_ROOT / "figures.html",
        paths.OUTPUT_ROOT / "data.html",
    ]

    missing = []

    for html_file in html_files:
        if not html_file.exists():
            continue

        content = html_file.read_text(encoding="utf-8")
        if not re.search(r'<html[^>]*\slang=["\'][a-z]{2}', content, re.IGNORECASE):
            missing.append(html_file.name)

    if missing:
        return CheckResult("fail", f"{len(missing)} HTML files missing lang attribute", missing)
    return CheckResult("pass", "All HTML files have lang attribute")


def check_heading_hierarchy(report: ValidationReport) -> CheckResult:
    """Verify proper heading hierarchy (H1 → H2 → H3, no skipping levels)."""
    html_files = [
        paths.OUTPUT_ROOT / "figures.html",
        paths.OUTPUT_ROOT / "data.html",
    ]

    issues = []

    for html_file in html_files:
        if not html_file.exists():
            continue

        content = html_file.read_text(encoding="utf-8")
        filename = html_file.name

        # Extract all heading tags in order (only static HTML, not JS)
        # Split by <script to get only the HTML part
        html_only = content.split("<script")[0]
        headings = re.findall(r"<h([1-6])[^>]*>", html_only, re.IGNORECASE)
        heading_levels = [int(h) for h in headings]

        # Check for exactly one H1
        h1_count = heading_levels.count(1)
        if h1_count != 1:
            issues.append(f"{filename}: {h1_count} H1 tags (should be 1)")

        # Check for skipped levels (e.g., H1 → H3 without H2)
        for i, level in enumerate(heading_levels[1:], 1):
            prev_level = heading_levels[i - 1]
            if level > prev_level + 1:
                issues.append(f"{filename}: H{level} after H{prev_level} (skipped level)")
                break  # Only report first issue per file

    if issues:
        return CheckResult("fail", f"{len(issues)} heading hierarchy issues", issues)
    return CheckResult("pass", "Heading hierarchy is correct in all HTML files")


def check_external_link_security(report: ValidationReport) -> CheckResult:
    """Verify external links have rel='noopener noreferrer'."""
    html_files = [
        paths.OUTPUT_ROOT / "figures.html",
        paths.OUTPUT_ROOT / "data.html",
    ]

    insecure = []

    for html_file in html_files:
        if not html_file.exists():
            continue

        content = html_file.read_text(encoding="utf-8")
        filename = html_file.name

        # Find all links with target="_blank"
        blank_links = re.findall(
            r'<a\s+[^>]*target=["\']_blank["\'][^>]*>',
            content,
            re.IGNORECASE | re.DOTALL
        )

        for link in blank_links:
            # Check if it has rel="noopener noreferrer" (or at least noopener)
            if 'rel="noopener noreferrer"' not in link and "rel='noopener noreferrer'" not in link:
                # Extract href for reporting
                href_match = re.search(r'href=["\']([^"\']+)["\']', link)
                href = href_match.group(1)[:40] + "..." if href_match else "unknown"
                insecure.append(f"{filename}: {href}")

    if insecure:
        return CheckResult("fail", f"{len(insecure)} insecure external links", insecure)
    return CheckResult("pass", "All external links have proper rel attributes")


def check_title_quality(report: ValidationReport) -> CheckResult:
    """Check figure titles are descriptive enough for SEO/alt text."""
    poor_titles = []

    # Check figures metadata
    figures_meta = load_json(paths.OUTPUT_FIGURES_METADATA)
    if figures_meta:
        for fig in figures_meta.get("figures", []):
            title = fig.get("title", "")
            fig_id = fig.get("id", "unknown")

            # Check minimum length
            if len(title) < MIN_TITLE_LENGTH:
                poor_titles.append(f"{fig_id}: title too short ({len(title)} chars)")

            # Check for vague single-word titles (unless it's a proper noun)
            words = title.split()
            if len(words) <= 2 and not any(w[0].isupper() for w in words[1:] if w):
                if title.lower() not in ["overview", "summary"]:
                    poor_titles.append(f"{fig_id}: title may be too vague ('{title}')")

    # Check hand-drawn metadata
    hand_drawn_meta = load_json(paths.OUTPUT_HAND_DRAWN_METADATA)
    if hand_drawn_meta:
        for fig in hand_drawn_meta.get("figures", []):
            if fig.get("id", "").startswith("_"):
                continue  # Skip template entries
            title = fig.get("title", "")
            fig_id = fig.get("id", "unknown")

            if len(title) < MIN_TITLE_LENGTH:
                poor_titles.append(f"{fig_id}: title too short ({len(title)} chars)")

    if poor_titles:
        return CheckResult("warn", f"{len(poor_titles)} figures with poor titles for SEO", poor_titles)
    return CheckResult("pass", f"All figure titles meet SEO requirements (min {MIN_TITLE_LENGTH} chars)")


def check_seo_length_limits(report: ValidationReport) -> CheckResult:
    """Check that SEO tags don't exceed platform-specific length limits."""
    html_files = [
        paths.OUTPUT_ROOT / "figures.html",
        paths.OUTPUT_ROOT / "data.html",
    ]

    issues = []

    for html_file in html_files:
        if not html_file.exists():
            continue

        content = html_file.read_text(encoding="utf-8")
        filename = html_file.name

        # Check <title> tag (max 60 chars)
        title_match = re.search(r"<title>([^<]+)</title>", content)
        if title_match:
            title = title_match.group(1)
            if len(title) > SEO_LENGTH_LIMITS["title"]:
                issues.append(f"{filename}: <title> too long ({len(title)}/{SEO_LENGTH_LIMITS['title']} chars)")

        # Check meta description (max 160 chars)
        desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if desc_match:
            desc = desc_match.group(1)
            if len(desc) > SEO_LENGTH_LIMITS["description"]:
                issues.append(f"{filename}: meta description too long ({len(desc)}/{SEO_LENGTH_LIMITS['description']} chars)")

        # Check og:title (max 90 chars)
        og_title_match = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if og_title_match:
            og_title = og_title_match.group(1)
            if len(og_title) > SEO_LENGTH_LIMITS["og:title"]:
                issues.append(f"{filename}: og:title too long ({len(og_title)}/{SEO_LENGTH_LIMITS['og:title']} chars)")

        # Check og:description (max 200 chars)
        og_desc_match = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if og_desc_match:
            og_desc = og_desc_match.group(1)
            if len(og_desc) > SEO_LENGTH_LIMITS["og:description"]:
                issues.append(f"{filename}: og:description too long ({len(og_desc)}/{SEO_LENGTH_LIMITS['og:description']} chars)")

        # Check twitter:title (max 70 chars)
        tw_title_match = re.search(r'<meta\s+name=["\']twitter:title["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if tw_title_match:
            tw_title = tw_title_match.group(1)
            if len(tw_title) > SEO_LENGTH_LIMITS["twitter:title"]:
                issues.append(f"{filename}: twitter:title too long ({len(tw_title)}/{SEO_LENGTH_LIMITS['twitter:title']} chars)")

        # Check twitter:description (max 200 chars)
        tw_desc_match = re.search(r'<meta\s+name=["\']twitter:description["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if tw_desc_match:
            tw_desc = tw_desc_match.group(1)
            if len(tw_desc) > SEO_LENGTH_LIMITS["twitter:description"]:
                issues.append(f"{filename}: twitter:description too long ({len(tw_desc)}/{SEO_LENGTH_LIMITS['twitter:description']} chars)")

        # Check alt text on images (max 125 chars)
        alt_matches = re.findall(r'<img[^>]+alt=["\']([^"\']+)["\']', content, re.IGNORECASE)
        for alt_text in alt_matches:
            if len(alt_text) > SEO_LENGTH_LIMITS["alt"]:
                truncated_alt = alt_text[:30] + "..."
                issues.append(f"{filename}: alt text too long ({len(alt_text)}/{SEO_LENGTH_LIMITS['alt']} chars): \"{truncated_alt}\"")

    if issues:
        return CheckResult("fail", f"{len(issues)} SEO length limit violations", issues)
    return CheckResult("pass", "All SEO tags within length limits")


# =============================================================================
# Main Execution
# =============================================================================

def run_all_checks(strict: bool = False, ci_mode: bool = False) -> int:
    """Run all validation checks and return exit code.

    Args:
        strict: If True, fail on warnings too
        ci_mode: If True, skip checks requiring generated content (figures, dist/data)
    """
    print("=" * 50)
    print(f"{Colors.BOLD}SOBE 2025 Data Repository - Quality Checks{Colors.RESET}")
    if ci_mode:
        print(f"{Colors.INFO}(CI mode: skipping checks for generated content){Colors.RESET}")
    print("=" * 50)

    report = ValidationReport()

    # Checks to skip in CI mode (require generated content)
    ci_skip_checks = {
        "Metadata-file sync",  # Requires generated figures
        "Orphan figures",      # Requires generated figures
        "Data files exist",    # Requires dist/data/ TSV files
    }

    def run_check(name: str, check_fn):
        if ci_mode and name in ci_skip_checks:
            result = CheckResult("skip", "Skipped in CI mode (requires generated content)")
        else:
            result = check_fn(report)
        report.add(name, result)
        report.print_result(name, result)

    # Tier 1: Critical
    report.print_tier_header("TIER 1", "Critical Checks")

    checks_tier1 = [
        ("SVG/PNG pairs", check_svg_png_pairs),
        ("Zero-size files", check_zero_size_files),
        ("Metadata-file sync", check_figures_metadata_sync),
        ("Orphan figures", check_orphan_figures),
    ]

    for name, check_fn in checks_tier1:
        run_check(name, check_fn)

    # Tier 2: Data Quality
    report.print_tier_header("TIER 2", "Data Quality Checks")

    checks_tier2 = [
        ("Data files exist", check_data_files_exist),
        ("Data file content", check_data_file_not_empty),
        ("Source data files", check_source_data_files),
        ("Data metadata files", check_data_metadata_files),
        ("TSV format", check_tsv_format),
    ]

    for name, check_fn in checks_tier2:
        run_check(name, check_fn)

    # Tier 3: Consistency
    report.print_tier_header("TIER 3", "Consistency Checks")

    checks_tier3 = [
        ("Organism taxonomy", check_organism_taxonomy),
        ("Type taxonomy", check_type_taxonomy),
        ("ID uniqueness", check_id_uniqueness),
        ("License consistency", check_license_consistency),
        ("Description quality", check_description_quality),
    ]

    for name, check_fn in checks_tier3:
        run_check(name, check_fn)

    # Tier 4: Reporting
    report.print_tier_header("TIER 4", "Reporting & Metrics")

    checks_tier4 = [
        ("File sizes", check_file_sizes),
        ("Web format coverage", check_web_format_coverage),
        ("Hand-drawn figures", check_hand_drawn_files),
        ("Orphan hand-drawn", check_orphan_hand_drawn_figures),
        ("Stale figures", check_stale_figures),
    ]

    for name, check_fn in checks_tier4:
        run_check(name, check_fn)

    # Tier 5: Bibliography & References
    report.print_tier_header("TIER 5", "Bibliography & Reference Checks")

    checks_tier5 = [
        ("Bibliography exists", check_bibliography_exists),
        ("Bibliography schema", check_bibliography_schema),
        ("Bibliography duplicates", check_bibliography_duplicates),
        ("Ref ID format", check_ref_id_format),
        ("Dist bibliography sync", check_dist_bibliography_sync),
        ("TSV column values", check_tsv_column_values),
    ]

    for name, check_fn in checks_tier5:
        run_check(name, check_fn)

    # Tier 6: SEO & Accessibility (metadata quality)
    report.print_tier_header("TIER 6", "SEO & Accessibility Checks")

    checks_tier6 = [
        ("Title quality (SEO)", check_title_quality),
    ]

    for name, check_fn in checks_tier6:
        run_check(name, check_fn)

    # Summary
    report.print_summary()

    # Return exit code
    fails, warns, _ = report.summary()
    if fails > 0:
        return 1
    if strict and warns > 0:
        return 1
    return 0


if __name__ == "__main__":
    strict_mode = "--strict" in sys.argv
    ci_mode = "--ci" in sys.argv
    exit_code = run_all_checks(strict=strict_mode, ci_mode=ci_mode)
    sys.exit(exit_code)
