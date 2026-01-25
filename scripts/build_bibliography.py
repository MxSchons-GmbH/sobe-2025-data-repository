#!/usr/bin/env python3
"""
Build Bibliography - Extract sources from TSV files and create CSL-JSON bibliography.

This script programmatically extracts all source references from TSV files,
fetches metadata from CrossRef API for DOIs, and generates a standardized
bibliography in CSL-JSON format.

Features:
- Parse DOIs and fetch metadata from CrossRef API
- Generate ref_ids deterministically (author + year)
- Handle duplicates (same DOI referenced multiple times)
- Produce audit log of all extractions
- Optionally update TSV files with ref_id column

Usage:
    python build_bibliography.py              # Extract and build bibliography
    python build_bibliography.py --dry-run    # Preview without writing files
    python build_bibliography.py --update-tsv # Also update TSV files with ref_ids
"""

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import pandas as pd

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from paths import DATA_DIR, REPO_ROOT

# Output paths
REFERENCES_DIR = DATA_DIR / "references"
BIBLIOGRAPHY_FILE = REFERENCES_DIR / "bibliography.json"
AUDIT_LOG_FILE = REFERENCES_DIR / "extraction_audit.json"

# CrossRef API settings
CROSSREF_API_URL = "https://api.crossref.org/works/"
CROSSREF_MAILTO = "sobe25-data-repository@mxschons.com"  # Polite pool access
API_RATE_LIMIT_SECONDS = 0.1  # Be nice to CrossRef

# Source column names to look for (case-insensitive)
SOURCE_COLUMN_NAMES = ["source", "ref", "references", "reference", "doi", "link"]

# Files that have DOI column separately (keep both DOI and Source)
FILES_WITH_DOI_COLUMN = ["neural-recordings.tsv"]


@dataclass
class SourceExtraction:
    """Represents a single extracted source."""
    file: str
    row: int
    column: str
    original_value: str
    extracted_type: str  # "doi", "url", "text"
    extracted_value: str
    ref_id: Optional[str] = None
    method: str = ""  # "crossref_api", "url_parse", "text_hash"
    error: Optional[str] = None


@dataclass
class BibliographyEntry:
    """CSL-JSON compatible bibliography entry."""
    id: str
    type: str
    title: str
    URL: Optional[str] = None
    DOI: Optional[str] = None
    author: list = field(default_factory=list)
    issued: Optional[dict] = None
    accessed: Optional[dict] = None
    container_title: Optional[str] = None  # journal name
    volume: Optional[str] = None
    page: Optional[str] = None
    note: Optional[str] = None

    def to_csl_json(self) -> dict:
        """Convert to CSL-JSON format."""
        result = {"id": self.id, "type": self.type, "title": self.title}

        if self.URL:
            result["URL"] = self.URL
        if self.DOI:
            result["DOI"] = self.DOI
        if self.author:
            result["author"] = self.author
        if self.issued:
            result["issued"] = self.issued
        if self.accessed:
            result["accessed"] = self.accessed
        if self.container_title:
            result["container-title"] = self.container_title
        if self.volume:
            result["volume"] = self.volume
        if self.page:
            result["page"] = self.page
        if self.note:
            result["note"] = self.note

        return result


class BibliographyBuilder:
    """Main class for building the bibliography."""

    def __init__(self, dry_run: bool = False, verbose: bool = True):
        self.dry_run = dry_run
        self.verbose = verbose
        self.extractions: list[SourceExtraction] = []
        self.bibliography: dict[str, BibliographyEntry] = {}
        self.doi_cache: dict[str, dict] = {}
        self.ref_id_counter: dict[str, int] = {}  # For disambiguation
        # Deduplication maps: DOI/URL -> ref_id
        self.doi_to_ref_id: dict[str, str] = {}
        self.url_to_ref_id: dict[str, str] = {}

    def log(self, message: str):
        """Print if verbose mode."""
        if self.verbose:
            print(message)

    def find_source_columns(self, df: pd.DataFrame) -> list[str]:
        """Find columns that contain source information."""
        found = []
        for col in df.columns:
            if col.lower() in SOURCE_COLUMN_NAMES:
                found.append(col)
        return found

    def extract_doi_from_url(self, url: str) -> Optional[str]:
        """Extract DOI from a URL if present."""
        # DOIs can contain parentheses, brackets, and various characters
        # Pattern needs to match balanced parentheses in DOIs like 10.1016/0014-4886(69)90086-7
        # DOI spec: prefix/suffix where suffix can contain most printable chars

        # Match DOI patterns - allow parentheses with content inside
        patterns = [
            # doi.org URLs - capture everything after doi.org/ that looks like a DOI
            r'doi\.org/(10\.\d{4,}/[^\s,;\]]+)',
            # URL encoded
            r'doi\.org%2F(10\.\d{4,}%2F[^\s,;\]]+)',
            # Bare DOI (not in URL)
            r'^(10\.\d{4,}/[^\s,;\]]+)$',
        ]

        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                doi = match.group(1)
                # Clean up URL encoding if present
                doi = doi.replace('%2F', '/')
                # Remove trailing punctuation but preserve parentheses that are part of DOI
                # Only remove trailing punctuation that's clearly not part of DOI
                doi = re.sub(r'[.,;]+$', '', doi)
                # Remove trailing ) only if there's no matching ( in the DOI suffix
                # This handles cases like "...article)," where ) is not part of DOI
                suffix = doi.split('/', 1)[1] if '/' in doi else doi
                open_parens = suffix.count('(')
                close_parens = suffix.count(')')
                if close_parens > open_parens:
                    # Remove excess trailing )
                    for _ in range(close_parens - open_parens):
                        if doi.endswith(')'):
                            doi = doi[:-1]
                return doi
        return None

    def extract_urls_from_text(self, text: str) -> list[str]:
        """Extract all URLs from a text string."""
        # Match URLs (http, https)
        # Need to handle parentheses in DOIs like doi.org/10.1016/0014-4886(69)90086-7
        # Strategy: match until whitespace/comma/semicolon, then clean up

        # First, try to find URLs - be greedy with parentheses
        url_pattern = r'https?://[^\s,;]+?(?=\s|,|;|$)'
        urls = re.findall(url_pattern, text, re.IGNORECASE)

        # If no matches, try simpler pattern
        if not urls:
            url_pattern = r'https?://\S+'
            urls = re.findall(url_pattern, text, re.IGNORECASE)

        # Clean up URLs - handle balanced parentheses
        cleaned = []
        for url in urls:
            # Remove trailing punctuation that's clearly not part of URL
            url = re.sub(r'[.,;]+$', '', url)

            # Handle parentheses - keep them if they're balanced within the URL
            # This is important for DOIs like 10.1016/0014-4886(69)90086-7
            # But remove trailing ) if unbalanced (e.g., from "(see https://...)")
            open_count = url.count('(')
            close_count = url.count(')')
            while close_count > open_count and url.endswith(')'):
                url = url[:-1]
                close_count -= 1

            # Also remove trailing ] if unbalanced
            open_bracket = url.count('[')
            close_bracket = url.count(']')
            while close_bracket > open_bracket and url.endswith(']'):
                url = url[:-1]
                close_bracket -= 1

            cleaned.append(url)

        return cleaned

    def fetch_crossref_metadata(self, doi: str) -> Optional[dict]:
        """Fetch metadata from CrossRef API for a DOI."""
        if not HAS_REQUESTS:
            return None

        if doi in self.doi_cache:
            return self.doi_cache[doi]

        try:
            headers = {"User-Agent": f"SOBEReport/1.0 (mailto:{CROSSREF_MAILTO})"}
            url = f"{CROSSREF_API_URL}{doi}"

            response = requests.get(url, headers=headers, timeout=10)
            time.sleep(API_RATE_LIMIT_SECONDS)  # Rate limiting

            if response.status_code == 200:
                data = response.json()
                self.doi_cache[doi] = data.get("message", {})
                return self.doi_cache[doi]
            else:
                self.log(f"  CrossRef returned {response.status_code} for {doi}")
                return None

        except Exception as e:
            self.log(f"  CrossRef error for {doi}: {e}")
            return None

    def generate_ref_id_from_metadata(self, metadata: dict) -> str:
        """Generate ref_id from CrossRef metadata."""
        # Get first author
        authors = metadata.get("author", [])
        if authors:
            first_author = authors[0].get("family", "unknown").lower()
            # Clean up author name
            first_author = re.sub(r'[^a-z]', '', first_author)
        else:
            first_author = "unknown"

        # Get year
        issued = metadata.get("issued", {})
        date_parts = issued.get("date-parts", [[]])
        if date_parts and date_parts[0]:
            year = str(date_parts[0][0])
        else:
            year = "nd"  # no date

        base_id = f"{first_author}{year}"
        return self._disambiguate_ref_id(base_id)

    def generate_ref_id_from_url(self, url: str) -> str:
        """Generate ref_id from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").split(".")[0]
        # Replace hyphens with underscores in domain
        domain = domain.replace("-", "_")

        # Extract meaningful part from path
        path_parts = [p for p in parsed.path.split("/") if p]
        if path_parts:
            slug = path_parts[-1][:30]
            # Replace all non-alphanumeric with underscore
            slug = re.sub(r'[^a-z0-9]', '_', slug.lower())
        else:
            slug = "page"

        # Use current year for access date
        year = datetime.now().year

        base_id = f"{domain}_{slug}_{year}"
        # Clean up: collapse multiple underscores, strip leading/trailing
        base_id = re.sub(r'_+', '_', base_id)
        base_id = base_id.strip('_')

        return self._disambiguate_ref_id(base_id)

    def generate_ref_id_from_text(self, text: str) -> str:
        """Generate ref_id from plain text (fallback)."""
        # Create a short hash-based ID
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        base_id = f"text_{text_hash}"
        return self._disambiguate_ref_id(base_id)

    def _disambiguate_ref_id(self, base_id: str) -> str:
        """Add suffix if ref_id already exists."""
        if base_id not in self.ref_id_counter:
            self.ref_id_counter[base_id] = 0
            return base_id

        self.ref_id_counter[base_id] += 1
        count = self.ref_id_counter[base_id]

        # Use a, b, c... for disambiguation
        suffix = chr(ord('a') + count - 1) if count < 26 else str(count)
        return f"{base_id}{suffix}"

    def create_bibliography_entry_from_doi(self, doi: str, metadata: dict) -> BibliographyEntry:
        """Create bibliography entry from CrossRef metadata."""
        ref_id = self.generate_ref_id_from_metadata(metadata)

        # Extract authors in CSL format
        authors = []
        for author in metadata.get("author", []):
            author_entry = {}
            if "family" in author:
                author_entry["family"] = author["family"]
            if "given" in author:
                author_entry["given"] = author["given"]
            if author_entry:
                authors.append(author_entry)

        # Extract issued date
        issued = None
        issued_data = metadata.get("issued", {})
        date_parts = issued_data.get("date-parts", [[]])
        if date_parts and date_parts[0]:
            issued = {"date-parts": [date_parts[0]]}

        # Determine type
        csl_type = metadata.get("type", "article-journal")
        type_mapping = {
            "journal-article": "article-journal",
            "proceedings-article": "paper-conference",
            "book-chapter": "chapter",
            "posted-content": "article",  # preprints
        }
        csl_type = type_mapping.get(csl_type, csl_type)

        return BibliographyEntry(
            id=ref_id,
            type=csl_type,
            title=metadata.get("title", ["Unknown"])[0] if metadata.get("title") else "Unknown",
            DOI=doi,
            URL=f"https://doi.org/{doi}",
            author=authors,
            issued=issued,
            container_title=metadata.get("container-title", [None])[0] if metadata.get("container-title") else None,
            volume=metadata.get("volume"),
            page=metadata.get("page"),
        )

    def create_bibliography_entry_from_url(self, url: str, note: str = None) -> BibliographyEntry:
        """Create bibliography entry from URL."""
        ref_id = self.generate_ref_id_from_url(url)

        # Extract domain for title
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")

        # Try to extract title from path
        path_parts = [p for p in parsed.path.split("/") if p]
        if path_parts:
            title = path_parts[-1].replace("-", " ").replace("_", " ").title()
        else:
            title = domain

        return BibliographyEntry(
            id=ref_id,
            type="webpage",
            title=title,
            URL=url,
            author=[{"literal": domain}],
            accessed={"date-parts": [[datetime.now().year, datetime.now().month, datetime.now().day]]},
            note=note,
        )

    def create_bibliography_entry_from_text(self, text: str) -> BibliographyEntry:
        """Create bibliography entry from plain text."""
        ref_id = self.generate_ref_id_from_text(text)

        return BibliographyEntry(
            id=ref_id,
            type="personal_communication",
            title=text[:100] + ("..." if len(text) > 100 else ""),
            note=text if len(text) > 100 else None,
        )

    def process_source_value(self, value: str, file_name: str, row: int, column: str) -> list[SourceExtraction]:
        """Process a single source value and extract references."""
        if pd.isna(value) or not str(value).strip():
            return []

        value = str(value).strip()
        extractions = []

        # Extract all URLs first
        urls = self.extract_urls_from_text(value)

        if urls:
            for url in urls:
                # Check if URL contains a DOI
                doi = self.extract_doi_from_url(url)

                if doi:
                    extraction = SourceExtraction(
                        file=file_name,
                        row=row,
                        column=column,
                        original_value=value,
                        extracted_type="doi",
                        extracted_value=doi,
                    )

                    # Check if we've already processed this DOI
                    if doi in self.doi_to_ref_id:
                        extraction.ref_id = self.doi_to_ref_id[doi]
                        extraction.method = "cached_doi"
                    elif HAS_REQUESTS:
                        # Try to fetch metadata from CrossRef
                        metadata = self.fetch_crossref_metadata(doi)
                        if metadata:
                            entry = self.create_bibliography_entry_from_doi(doi, metadata)
                            extraction.ref_id = entry.id
                            extraction.method = "crossref_api"

                            if entry.id not in self.bibliography:
                                self.bibliography[entry.id] = entry
                            self.doi_to_ref_id[doi] = entry.id
                        else:
                            # Fallback: create entry from URL
                            entry = self.create_bibliography_entry_from_url(url)
                            entry.DOI = doi
                            extraction.ref_id = entry.id
                            extraction.method = "url_parse_doi_failed"
                            extraction.error = "CrossRef lookup failed"

                            if entry.id not in self.bibliography:
                                self.bibliography[entry.id] = entry
                            self.doi_to_ref_id[doi] = entry.id
                    else:
                        extraction.method = "no_requests_library"
                        extraction.error = "requests library not available"

                    extractions.append(extraction)
                else:
                    # Regular URL
                    extraction = SourceExtraction(
                        file=file_name,
                        row=row,
                        column=column,
                        original_value=value,
                        extracted_type="url",
                        extracted_value=url,
                    )

                    # Check if we've already processed this URL
                    if url in self.url_to_ref_id:
                        extraction.ref_id = self.url_to_ref_id[url]
                        extraction.method = "cached_url"
                    else:
                        # Extract any annotation (text in parentheses after URL)
                        note = None
                        url_pos = value.find(url)
                        if url_pos >= 0:
                            after_url = value[url_pos + len(url):].strip()
                            paren_match = re.match(r'\(([^)]+)\)', after_url)
                            if paren_match:
                                note = paren_match.group(1)

                        entry = self.create_bibliography_entry_from_url(url, note)
                        extraction.ref_id = entry.id
                        extraction.method = "url_parse"

                        if entry.id not in self.bibliography:
                            self.bibliography[entry.id] = entry
                        self.url_to_ref_id[url] = entry.id

                    extractions.append(extraction)
        else:
            # Plain text (no URLs found)
            # Check if it looks like a short label we should preserve
            if len(value) < 50 and not any(c in value for c in [':', '/', '\n']):
                extraction = SourceExtraction(
                    file=file_name,
                    row=row,
                    column=column,
                    original_value=value,
                    extracted_type="text",
                    extracted_value=value,
                )

                entry = self.create_bibliography_entry_from_text(value)
                extraction.ref_id = entry.id
                extraction.method = "text_label"

                if entry.id not in self.bibliography:
                    self.bibliography[entry.id] = entry

                extractions.append(extraction)
            else:
                # Longer text, treat as note/description
                extraction = SourceExtraction(
                    file=file_name,
                    row=row,
                    column=column,
                    original_value=value,
                    extracted_type="text",
                    extracted_value=value[:100],
                )

                entry = self.create_bibliography_entry_from_text(value)
                extraction.ref_id = entry.id
                extraction.method = "text_hash"

                if entry.id not in self.bibliography:
                    self.bibliography[entry.id] = entry

                extractions.append(extraction)

        return extractions

    def process_tsv_file(self, filepath: Path) -> list[SourceExtraction]:
        """Process a single TSV file and extract sources."""
        self.log(f"\nProcessing: {filepath.name}")

        try:
            df = pd.read_csv(filepath, sep='\t', dtype=str)
        except Exception as e:
            self.log(f"  Error reading file: {e}")
            return []

        source_columns = self.find_source_columns(df)

        if not source_columns:
            self.log(f"  No source columns found")
            return []

        self.log(f"  Found source columns: {source_columns}")

        file_extractions = []

        for col in source_columns:
            for idx, value in df[col].items():
                extractions = self.process_source_value(
                    value,
                    filepath.name,
                    idx + 2,  # +2 for 1-indexed + header row
                    col
                )
                file_extractions.extend(extractions)

        self.log(f"  Extracted {len(file_extractions)} references")
        return file_extractions

    def process_all_tsv_files(self):
        """Process all TSV files in the data directory."""
        self.log("=" * 60)
        self.log("BIBLIOGRAPHY EXTRACTION")
        self.log("=" * 60)

        # Find all TSV files
        tsv_files = list(DATA_DIR.rglob("*.tsv"))
        # Exclude files in _metadata directory
        tsv_files = [f for f in tsv_files if "_metadata" not in str(f)]

        self.log(f"\nFound {len(tsv_files)} TSV files to process")

        for filepath in sorted(tsv_files):
            extractions = self.process_tsv_file(filepath)
            self.extractions.extend(extractions)

        self.log("\n" + "=" * 60)
        self.log("EXTRACTION SUMMARY")
        self.log("=" * 60)
        self.log(f"Total extractions: {len(self.extractions)}")
        self.log(f"Unique bibliography entries: {len(self.bibliography)}")

        # Count by type
        type_counts = {}
        for ext in self.extractions:
            type_counts[ext.extracted_type] = type_counts.get(ext.extracted_type, 0) + 1

        for ext_type, count in sorted(type_counts.items()):
            self.log(f"  {ext_type}: {count}")

        # Count errors
        errors = [e for e in self.extractions if e.error]
        if errors:
            self.log(f"\nWarnings/errors: {len(errors)}")

    def write_bibliography(self):
        """Write bibliography to JSON file."""
        if self.dry_run:
            self.log("\n[DRY RUN] Would write bibliography.json")
            return

        # Ensure directory exists
        REFERENCES_DIR.mkdir(parents=True, exist_ok=True)

        # Build CSL-JSON structure
        csl_data = {
            "$schema": "https://resource.citationstyles.org/schema/v1.0/input/json/csl-data.json",
            "_generated": datetime.now().isoformat(),
            "_generator": "build_bibliography.py",
            "references": [
                entry.to_csl_json()
                for entry in sorted(self.bibliography.values(), key=lambda e: e.id)
            ]
        }

        with open(BIBLIOGRAPHY_FILE, 'w', encoding='utf-8') as f:
            json.dump(csl_data, f, indent=2, ensure_ascii=False)

        self.log(f"\nWrote {len(self.bibliography)} entries to {BIBLIOGRAPHY_FILE}")

    def write_audit_log(self):
        """Write extraction audit log."""
        if self.dry_run:
            self.log("[DRY RUN] Would write extraction_audit.json")
            return

        audit_data = {
            "extraction_date": datetime.now().isoformat(),
            "files_processed": len(set(e.file for e in self.extractions)),
            "total_extractions": len(self.extractions),
            "unique_references": len(self.bibliography),
            "by_type": {},
            "by_method": {},
            "extractions": [],
            "errors": []
        }

        for ext in self.extractions:
            # Count by type
            audit_data["by_type"][ext.extracted_type] = audit_data["by_type"].get(ext.extracted_type, 0) + 1

            # Count by method
            audit_data["by_method"][ext.method] = audit_data["by_method"].get(ext.method, 0) + 1

            # Add to extractions list
            audit_data["extractions"].append({
                "file": ext.file,
                "row": ext.row,
                "column": ext.column,
                "original": ext.original_value[:200] if ext.original_value else None,
                "type": ext.extracted_type,
                "value": ext.extracted_value,
                "ref_id": ext.ref_id,
                "method": ext.method,
            })

            if ext.error:
                audit_data["errors"].append({
                    "file": ext.file,
                    "row": ext.row,
                    "error": ext.error,
                })

        with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)

        self.log(f"Wrote audit log to {AUDIT_LOG_FILE}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract sources from TSV files and build CSL-JSON bibliography"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview extraction without writing files"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Skip CrossRef API lookups (faster, less metadata)"
    )

    args = parser.parse_args()

    if args.no_api:
        global HAS_REQUESTS
        HAS_REQUESTS = False

    builder = BibliographyBuilder(
        dry_run=args.dry_run,
        verbose=not args.quiet
    )

    builder.process_all_tsv_files()
    builder.write_bibliography()
    builder.write_audit_log()

    if not args.dry_run:
        print("\nDone! Next steps:")
        print("1. Review data/references/bibliography.json")
        print("2. Review data/references/extraction_audit.json for any errors")
        print("3. Run: python validate.py to check the bibliography")


if __name__ == "__main__":
    main()
