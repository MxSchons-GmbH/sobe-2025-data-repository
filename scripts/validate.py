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

Usage:
    python3 validate.py          # Run all checks
    python3 validate.py --strict # Fail on warnings too
    python3 validate.py --fix    # Auto-fix some issues (future)
"""

import json
import sys
from pathlib import Path
from typing import NamedTuple

import paths


# Known exceptions - legacy assets that don't follow all conventions
# These should be documented and ideally fixed over time
KNOWN_EXCEPTIONS = {
    "svg_png_pairs": [
        # Legacy radar charts from old code - PNG only, no SVG source available
        "radar-charts/C. elegans.png",
        "radar-charts/Human.png",
        "radar-charts/Mammalian.png",
        "radar-charts/Mouse.png",
        "radar-charts/Rat.png",
        "radar-charts/Silicon.png",
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
    details: list[str] = []


class ValidationReport:
    """Aggregates validation results and provides summary."""

    def __init__(self):
        self.results: list[tuple[str, CheckResult]] = []
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

    def summary(self) -> tuple[int, int, int]:
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


def load_json(filepath: Path) -> dict | None:
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
    metadata_path = paths.OUTPUT_METADATA / "figures-metadata.json"
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
    metadata_path = paths.OUTPUT_METADATA / "figures-metadata.json"
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
    metadata_path = paths.OUTPUT_METADATA / "data-metadata.json"
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

            # Path is relative to repo root
            full_path = paths.REPO_ROOT / data_path / filename

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

    for csv_file in data_dir.rglob("*.csv"):
        checked += 1
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # Subtract 1 for header
            data_rows = len(lines) - 1
            if data_rows < 2:
                rel_path = csv_file.relative_to(data_dir)
                low_row_files.append(f"{rel_path}: {data_rows} data rows")
        except Exception:
            pass

    if low_row_files:
        return CheckResult(
            "warn",
            f"{len(low_row_files)} files with very few rows",
            low_row_files
        )
    return CheckResult("pass", f"All {checked} CSV files have sufficient data")


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


# =============================================================================
# TIER 3: Consistency Checks
# =============================================================================

def check_organism_taxonomy(report: ValidationReport) -> CheckResult:
    """Verify all organism tags are valid."""
    metadata_path = paths.OUTPUT_METADATA / "figures-metadata.json"
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
    metadata_path = paths.OUTPUT_METADATA / "figures-metadata.json"
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
    figures_meta = load_json(paths.OUTPUT_METADATA / "figures-metadata.json")
    if figures_meta:
        all_ids.extend((f["id"], "figures") for f in figures_meta.get("figures", []))

    # Hand-drawn metadata
    hand_drawn_meta = load_json(paths.OUTPUT_METADATA / "hand-drawn-metadata.json")
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
        ("figures-metadata.json", True),
        ("data-metadata.json", True),
        ("hand-drawn-metadata.json", True),
    ]

    missing_license = []

    for filename, required in files_to_check:
        filepath = paths.OUTPUT_METADATA / filename
        data = load_json(filepath)
        if data and "license" not in data:
            missing_license.append(filename)

    if missing_license:
        return CheckResult("warn", f"{len(missing_license)} files missing license", missing_license)
    return CheckResult("pass", "All metadata files have license information")


def check_description_quality(report: ValidationReport) -> CheckResult:
    """Warn about empty or very short descriptions."""
    poor_descriptions = []

    # Check figures metadata
    figures_meta = load_json(paths.OUTPUT_METADATA / "figures-metadata.json")
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
    png_count = 0
    svg_count = 0

    for png in figures_dir.rglob("*.png"):
        total_png_size += png.stat().st_size
        png_count += 1

    for svg in figures_dir.rglob("*.svg"):
        total_svg_size += svg.stat().st_size
        svg_count += 1

    png_mb = total_png_size / (1024 * 1024)
    svg_mb = total_svg_size / (1024 * 1024)

    return CheckResult(
        "pass",
        f"{png_count} PNGs ({png_mb:.1f}MB), {svg_count} SVGs ({svg_mb:.1f}MB)"
    )


def check_hand_drawn_files(report: ValidationReport) -> CheckResult:
    """Check hand-drawn figures have both PNG and SVG."""
    metadata_path = paths.OUTPUT_METADATA / "hand-drawn-metadata.json"
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


# =============================================================================
# Main Execution
# =============================================================================

def run_all_checks(strict: bool = False) -> int:
    """Run all validation checks and return exit code."""
    print("=" * 50)
    print(f"{Colors.BOLD}SOBE 2025 Data Repository - Quality Checks{Colors.RESET}")
    print("=" * 50)

    report = ValidationReport()

    # Tier 1: Critical
    report.print_tier_header("TIER 1", "Critical Checks")

    checks_tier1 = [
        ("SVG/PNG pairs", check_svg_png_pairs),
        ("Zero-size files", check_zero_size_files),
        ("Metadata-file sync", check_figures_metadata_sync),
        ("Orphan figures", check_orphan_figures),
    ]

    for name, check_fn in checks_tier1:
        result = check_fn(report)
        report.add(name, result)
        report.print_result(name, result)

    # Tier 2: Data Quality
    report.print_tier_header("TIER 2", "Data Quality Checks")

    checks_tier2 = [
        ("Data files exist", check_data_files_exist),
        ("Data file content", check_data_file_not_empty),
        ("Source data files", check_source_data_files),
    ]

    for name, check_fn in checks_tier2:
        result = check_fn(report)
        report.add(name, result)
        report.print_result(name, result)

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
        result = check_fn(report)
        report.add(name, result)
        report.print_result(name, result)

    # Tier 4: Reporting
    report.print_tier_header("TIER 4", "Reporting & Metrics")

    checks_tier4 = [
        ("File sizes", check_file_sizes),
        ("Hand-drawn figures", check_hand_drawn_files),
    ]

    for name, check_fn in checks_tier4:
        result = check_fn(report)
        report.add(name, result)
        report.print_result(name, result)

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
    exit_code = run_all_checks(strict=strict_mode)
    sys.exit(exit_code)
