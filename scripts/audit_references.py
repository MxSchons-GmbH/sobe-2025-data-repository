#!/usr/bin/env python3
"""
Audit References - Analyze reference quality across all TSV files.

This script generates a comprehensive report of reference coverage,
identifying gaps, format issues, and areas needing attention.

Usage:
    python audit_references.py              # Generate audit report
    python audit_references.py --json       # Output as JSON only
    python audit_references.py --summary    # Brief summary only
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA_DIR, DATA_REFERENCES

# Output path
AUDIT_REPORT_FILE = DATA_REFERENCES / "audit_report.json"

# Reference column patterns
REF_COLUMNS = ["source", "ref", "references", "reference", "doi", "link", "doi/link"]
STRUCTURED_REF_COLUMNS = ["ref_id", "supporting_refs", "ref_note", "confidence", "validated_by"]

# DOI format patterns
DOI_PATTERNS = {
    "canonical": r"^https://doi\.org/10\.\d{4,}/\S+$",
    "dx_doi": r"^https?://dx\.doi\.org/10\.\d{4,}/\S+$",
    "bare": r"^10\.\d{4,}/\S+$",
    "doi_prefix": r"^doi:10\.\d{4,}/\S+$",
    "bracketed": r"^\[\d+\]$",
}


@dataclass
class FileAudit:
    """Audit results for a single TSV file."""
    file_path: str
    file_name: str
    category: str
    total_rows: int = 0
    ref_columns: list = field(default_factory=list)
    structured_columns: list = field(default_factory=list)

    # Coverage stats
    rows_with_refs: int = 0
    rows_without_refs: int = 0
    coverage_pct: float = 0.0

    # DOI format stats
    canonical_dois: int = 0
    non_canonical_dois: int = 0
    bracketed_refs: int = 0
    urls_only: int = 0
    text_only: int = 0

    # Structured column stats
    ref_id_filled: int = 0
    ref_id_empty: int = 0
    confidence_none: int = 0
    validated_none: int = 0

    # Issues found
    issues: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditReport:
    """Complete audit report."""
    generated_at: str = ""
    total_files: int = 0
    total_rows: int = 0

    # Overall coverage
    rows_with_refs: int = 0
    rows_without_refs: int = 0
    overall_coverage_pct: float = 0.0

    # DOI format summary
    canonical_dois: int = 0
    non_canonical_dois: int = 0
    bracketed_refs: int = 0

    # Structured columns summary
    files_with_structured_cols: int = 0
    ref_id_filled: int = 0
    ref_id_empty: int = 0

    # By category
    by_category: dict = field(default_factory=dict)

    # Individual file audits
    files: list = field(default_factory=list)

    # Priority issues
    priority_issues: list = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {
            "generated_at": self.generated_at,
            "summary": {
                "total_files": self.total_files,
                "total_rows": self.total_rows,
                "rows_with_refs": self.rows_with_refs,
                "rows_without_refs": self.rows_without_refs,
                "overall_coverage_pct": round(self.overall_coverage_pct, 1),
                "canonical_dois": self.canonical_dois,
                "non_canonical_dois": self.non_canonical_dois,
                "bracketed_refs": self.bracketed_refs,
                "files_with_structured_cols": self.files_with_structured_cols,
                "ref_id_filled": self.ref_id_filled,
                "ref_id_empty": self.ref_id_empty,
            },
            "by_category": self.by_category,
            "priority_issues": self.priority_issues,
            "files": [f.to_dict() for f in self.files],
        }
        return result


def find_ref_columns(df: pd.DataFrame) -> list[str]:
    """Find columns that contain reference information."""
    found = []
    for col in df.columns:
        if col.lower() in REF_COLUMNS:
            found.append(col)
    return found


def find_structured_columns(df: pd.DataFrame) -> list[str]:
    """Find structured reference columns (ref_id, confidence, etc.)."""
    found = []
    for col in df.columns:
        if col.lower() in STRUCTURED_REF_COLUMNS:
            found.append(col)
    return found


def classify_reference(value: str) -> str:
    """Classify a reference value by its format."""
    if pd.isna(value) or not str(value).strip():
        return "empty"

    value = str(value).strip()

    # Check for bracketed references like [10]
    if re.match(DOI_PATTERNS["bracketed"], value):
        return "bracketed"

    # Check for canonical DOI format
    if re.match(DOI_PATTERNS["canonical"], value):
        return "canonical_doi"

    # Check for other DOI formats
    if re.match(DOI_PATTERNS["dx_doi"], value, re.IGNORECASE):
        return "dx_doi"
    if re.match(DOI_PATTERNS["bare"], value):
        return "bare_doi"
    if re.match(DOI_PATTERNS["doi_prefix"], value, re.IGNORECASE):
        return "doi_prefix"

    # Check if contains doi.org anywhere
    if "doi.org" in value.lower():
        return "canonical_doi"
    if "dx.doi.org" in value.lower():
        return "dx_doi"

    # Check if URL
    if value.startswith("http://") or value.startswith("https://"):
        return "url"

    # Plain text
    return "text"


def audit_file(filepath: Path) -> FileAudit:
    """Audit a single TSV file."""
    # Determine category from path
    category = filepath.parent.name
    if category == "data":
        category = "root"

    audit = FileAudit(
        file_path=str(filepath.relative_to(DATA_DIR)),
        file_name=filepath.name,
        category=category,
    )

    try:
        df = pd.read_csv(filepath, sep='\t', dtype=str)
    except Exception as e:
        audit.issues.append(f"Error reading file: {e}")
        return audit

    audit.total_rows = len(df)
    audit.ref_columns = find_ref_columns(df)
    audit.structured_columns = find_structured_columns(df)

    # Analyze reference columns
    if audit.ref_columns:
        for idx, row in df.iterrows():
            has_ref = False
            for col in audit.ref_columns:
                value = row.get(col, "")
                ref_type = classify_reference(value)

                if ref_type != "empty":
                    has_ref = True

                    if ref_type == "canonical_doi":
                        audit.canonical_dois += 1
                    elif ref_type in ["dx_doi", "bare_doi", "doi_prefix"]:
                        audit.non_canonical_dois += 1
                    elif ref_type == "bracketed":
                        audit.bracketed_refs += 1
                    elif ref_type == "url":
                        audit.urls_only += 1
                    else:
                        audit.text_only += 1

            if has_ref:
                audit.rows_with_refs += 1
            else:
                audit.rows_without_refs += 1

        if audit.total_rows > 0:
            audit.coverage_pct = (audit.rows_with_refs / audit.total_rows) * 100
    else:
        audit.rows_without_refs = audit.total_rows

    # Analyze structured columns
    if audit.structured_columns:
        for col in audit.structured_columns:
            if col.lower() == "ref_id":
                for value in df[col]:
                    if pd.isna(value) or not str(value).strip():
                        audit.ref_id_empty += 1
                    else:
                        audit.ref_id_filled += 1
            elif col.lower() == "confidence":
                for value in df[col]:
                    if pd.isna(value) or str(value).strip().lower() == "none":
                        audit.confidence_none += 1
            elif col.lower() == "validated_by":
                for value in df[col]:
                    if pd.isna(value) or str(value).strip().lower() == "none":
                        audit.validated_none += 1

    # Identify issues
    if audit.bracketed_refs > 0:
        audit.issues.append(f"{audit.bracketed_refs} bracketed references need resolution")

    if audit.non_canonical_dois > 0:
        audit.issues.append(f"{audit.non_canonical_dois} DOIs in non-canonical format")

    if audit.structured_columns and audit.ref_id_empty > 0:
        audit.issues.append(f"{audit.ref_id_empty} rows with empty ref_id")

    if not audit.ref_columns and audit.total_rows > 0:
        audit.issues.append("No reference columns found")
    elif audit.coverage_pct < 50 and audit.total_rows > 5:
        audit.issues.append(f"Low coverage: {audit.coverage_pct:.1f}%")

    return audit


def generate_report(verbose: bool = True) -> AuditReport:
    """Generate complete audit report."""
    report = AuditReport()
    report.generated_at = datetime.now().isoformat()

    # Find all TSV files
    tsv_files = list(DATA_DIR.rglob("*.tsv"))
    tsv_files = [f for f in tsv_files if "_metadata" not in str(f)]

    if verbose:
        print(f"Auditing {len(tsv_files)} TSV files...\n")

    category_stats = defaultdict(lambda: {
        "files": 0,
        "rows": 0,
        "with_refs": 0,
        "without_refs": 0,
        "coverage_pct": 0,
    })

    for filepath in sorted(tsv_files):
        audit = audit_file(filepath)
        report.files.append(audit)
        report.total_files += 1
        report.total_rows += audit.total_rows
        report.rows_with_refs += audit.rows_with_refs
        report.rows_without_refs += audit.rows_without_refs
        report.canonical_dois += audit.canonical_dois
        report.non_canonical_dois += audit.non_canonical_dois
        report.bracketed_refs += audit.bracketed_refs

        if audit.structured_columns:
            report.files_with_structured_cols += 1
            report.ref_id_filled += audit.ref_id_filled
            report.ref_id_empty += audit.ref_id_empty

        # Update category stats
        cat = audit.category
        category_stats[cat]["files"] += 1
        category_stats[cat]["rows"] += audit.total_rows
        category_stats[cat]["with_refs"] += audit.rows_with_refs
        category_stats[cat]["without_refs"] += audit.rows_without_refs

        # Collect priority issues
        for issue in audit.issues:
            if "bracketed" in issue.lower() or "empty ref_id" in issue.lower():
                report.priority_issues.append({
                    "file": audit.file_name,
                    "category": audit.category,
                    "issue": issue,
                    "priority": "high"
                })
            elif "non-canonical" in issue.lower():
                report.priority_issues.append({
                    "file": audit.file_name,
                    "category": audit.category,
                    "issue": issue,
                    "priority": "medium"
                })

    # Calculate overall coverage
    if report.total_rows > 0:
        report.overall_coverage_pct = (report.rows_with_refs / report.total_rows) * 100

    # Calculate category coverage
    for cat, stats in category_stats.items():
        if stats["rows"] > 0:
            stats["coverage_pct"] = round((stats["with_refs"] / stats["rows"]) * 100, 1)
        report.by_category[cat] = stats

    return report


def print_report(report: AuditReport):
    """Print a formatted report to console."""
    print("=" * 70)
    print("REFERENCE QUALITY AUDIT REPORT")
    print("=" * 70)
    print(f"Generated: {report.generated_at}\n")

    print("OVERALL SUMMARY")
    print("-" * 40)
    print(f"Total files:        {report.total_files}")
    print(f"Total rows:         {report.total_rows}")
    print(f"Rows with refs:     {report.rows_with_refs}")
    print(f"Rows without refs:  {report.rows_without_refs}")
    print(f"Coverage:           {report.overall_coverage_pct:.1f}%")
    print()

    print("DOI FORMAT SUMMARY")
    print("-" * 40)
    print(f"Canonical DOIs:     {report.canonical_dois}")
    print(f"Non-canonical DOIs: {report.non_canonical_dois}")
    print(f"Bracketed refs:     {report.bracketed_refs}")
    print()

    print("STRUCTURED COLUMNS (ref_id, confidence, validated_by)")
    print("-" * 40)
    print(f"Files with columns: {report.files_with_structured_cols}")
    print(f"ref_id filled:      {report.ref_id_filled}")
    print(f"ref_id empty:       {report.ref_id_empty}")
    print()

    print("COVERAGE BY CATEGORY")
    print("-" * 40)
    print(f"{'Category':<15} {'Files':>6} {'Rows':>8} {'With Ref':>10} {'Coverage':>10}")
    print("-" * 40)
    for cat, stats in sorted(report.by_category.items()):
        print(f"{cat:<15} {stats['files']:>6} {stats['rows']:>8} {stats['with_refs']:>10} {stats['coverage_pct']:>9.1f}%")
    print()

    print("PRIORITY ISSUES")
    print("-" * 40)
    high_priority = [i for i in report.priority_issues if i["priority"] == "high"]
    medium_priority = [i for i in report.priority_issues if i["priority"] == "medium"]

    if high_priority:
        print("\nHIGH PRIORITY:")
        for issue in high_priority[:10]:  # Show top 10
            print(f"  [{issue['category']}] {issue['file']}: {issue['issue']}")

    if medium_priority:
        print("\nMEDIUM PRIORITY:")
        for issue in medium_priority[:10]:  # Show top 10
            print(f"  [{issue['category']}] {issue['file']}: {issue['issue']}")

    if not high_priority and not medium_priority:
        print("  No priority issues found!")

    print()
    print("FILES NEEDING ATTENTION")
    print("-" * 40)

    # Files with no refs at all
    no_refs = [f for f in report.files if f.coverage_pct == 0 and f.total_rows > 0]
    if no_refs:
        print("\nFiles with 0% coverage:")
        for f in no_refs[:10]:
            print(f"  {f.file_path} ({f.total_rows} rows)")

    # Files with low coverage
    low_coverage = [f for f in report.files if 0 < f.coverage_pct < 50 and f.total_rows > 5]
    if low_coverage:
        print("\nFiles with <50% coverage:")
        for f in sorted(low_coverage, key=lambda x: x.coverage_pct)[:10]:
            print(f"  {f.file_path}: {f.coverage_pct:.1f}% ({f.rows_with_refs}/{f.total_rows})")


def main():
    parser = argparse.ArgumentParser(
        description="Audit reference quality across TSV files"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON only (no console formatting)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show brief summary only"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: data/references/audit_report.json)"
    )

    args = parser.parse_args()

    # Generate report
    report = generate_report(verbose=not args.json)

    # Output
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    elif args.summary:
        print(f"Reference Coverage: {report.overall_coverage_pct:.1f}%")
        print(f"Files: {report.total_files} | Rows: {report.total_rows}")
        print(f"DOIs: {report.canonical_dois} canonical, {report.non_canonical_dois} non-canonical")
        print(f"Bracketed refs: {report.bracketed_refs}")
        print(f"Structured columns: {report.ref_id_filled} filled, {report.ref_id_empty} empty")
    else:
        print_report(report)

    # Write JSON report
    output_path = Path(args.output) if args.output else AUDIT_REPORT_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, indent=2)

    if not args.json:
        print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
