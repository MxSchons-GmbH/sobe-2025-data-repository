# CLAUDE.md

This file provides guidance for Claude Code instances working with this repository.

## Project Overview

This is the **State of Brain Emulation Report 2025 Data Repository** - a Python-based data visualization pipeline that generates publication-quality interactive visualizations tracking progress in brain emulation research. The repository includes:

- 24+ datasets across neural simulations, recordings, connectomics, and computational requirements
- 38+ publication-quality figures in SVG and PNG formats
- Interactive web interface for data exploration
- Comprehensive styling system for consistent visualizations

## Quick Start

```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate all figures
cd scripts
python3 run_all_figures.py

# Generate specific figures
python3 run_all_figures.py fig1 fig2

# List available figures
python3 run_all_figures.py --list
```

## Repository Structure

```
sobe-2025-data-repository/
├── scripts/                    # Figure generation code
│   ├── style.py               # Style configuration (colors, fonts, chart specs)
│   ├── paths.py               # Centralized path configuration
│   ├── run_all_figures.py     # Main pipeline with figure registry
│   ├── validate.py            # Quality validation (run before commits!)
│   └── build_downloads.py     # ZIP archive builder
├── data/                       # Source datasets (TSV files)
│   ├── compute/               # AI training, hardware data
│   ├── connectomics/          # Brain scanning data
│   ├── costs/                 # Cost estimates, megaprojects
│   ├── formulas/              # Calculator formulas
│   ├── imaging/               # Imaging modalities
│   ├── initiatives/           # Brain research programs
│   ├── organisms/             # Organism reference data
│   ├── parameters/            # Shared calculation parameters
│   ├── recordings/            # Neural recording data
│   ├── simulations/           # Simulation history data
│   └── _metadata/             # Attribution metadata (mirrors data/ structure)
├── dist/                       # Distribution output for website
│   ├── calculator/            # Calculator outputs (data.json, types.ts, docs/)
│   ├── data/                  # TSV datasets (mirrors data/ structure)
│   │   └── _metadata.json     # Datasets catalog
│   ├── figures/
│   │   ├── generated/         # Output SVG, PNG, WebP, AVIF figures
│   │   │   └── _metadata.json # Generated figures catalog
│   │   └── hand-drawn/        # Hand-drawn illustrations
│   │       └── _metadata.json # Hand-drawn figures catalog
│   └── downloads/             # ZIP archives for bulk download
└── requirements.txt           # Python dependencies
```

## Key Scripts

### `scripts/run_all_figures.py`
Main figure generation pipeline. Uses a decorator-based figure registry:
```python
@figure("figure-name", "Description of the figure")
def generate_figure_name():
    # Figure generation code
```

### `scripts/style.py`
Centralized styling with:
- Color palette: Purple (#6B6080), Gold (#D4A84B), Teal (#4A90A4)
- Typography: Playfair Display, Inter, JetBrains Mono
- Chart specifications and export settings
- Species neuron count reference data

### `scripts/paths.py`
Path configuration for all data and output directories. Always use these paths instead of hardcoding.

## Calculator Module

The TypeScript calculator at `scripts/calculator/` estimates brain emulation project costs and timelines based on organism size, imaging modality, and technology assumptions.

### Calculator Quick Start

```bash
cd scripts/calculator
npm install          # Also runs build:data via postinstall
npm test             # Run tests
```

### Calculator Structure

```
scripts/calculator/
├── build/             # Build scripts (validate, generate-types, bundle, generate-docs)
├── src/               # TypeScript source code
│   └── engine/        # Core calculator engine
├── tests/             # Unit tests and spreadsheet parity tests
├── data/              # Symlinks to root data/ TSV files
└── original/          # Reference Excel spreadsheets
```

### Calculator Outputs

Outputs are generated in `dist/calculator/` (distribution folder):

| File | Purpose |
|------|---------|
| `data.json` | Bundled parameters and formulas for web apps |
| `types.ts` | TypeScript interfaces for type-safe usage |
| `docs/parameters.md` | Human-readable parameter reference |
| `docs/formulas.md` | Human-readable formula reference |

### Calculator Workflow

1. Edit TSV files in `data/` (formulas, organisms, imaging, etc.)
2. Run `npm run build:data` to regenerate outputs
3. Run `npm test` to verify calculations
4. Commit both source TSV files and generated outputs

CI will fail if generated outputs are stale.

## Code Conventions

1. **Figure Registration**: Use the `@figure()` decorator to register new figures
2. **Styling**: Always use `style.py` for colors, fonts, and chart settings
3. **Paths**: Use `paths.py` for all file paths
4. **Output Formats**: Generate SVG, PNG, WebP, and AVIF for each figure (see below)
5. **Attribution**: All figures include "Zanichelli, Schons et al, State of Brain Emulation Report 2025"

### Output Formats

The `save_figure()` function generates multiple formats optimized for different use cases:

| Format | Purpose | Size | Notes |
|--------|---------|------|-------|
| **SVG** | Vector graphics | Varies | Resolution-independent, ideal for scaling |
| **PNG** | Raster fallback | Baseline | 150 DPI, universal browser support |
| **WebP** | Web optimization | ~50% smaller | Modern browsers, good quality at 90% |
| **AVIF** | Best compression | ~70% smaller | Newest browsers, excellent quality at 85% |

Use `<picture>` element in HTML to serve the best format:
```html
<picture>
  <source srcset="figure.avif" type="image/avif">
  <source srcset="figure.webp" type="image/webp">
  <img src="figure.png" alt="Description">
</picture>
```

## File Naming Conventions

All figure filenames follow SEO and data science best practices for discoverability and clarity.

### Rules

| Rule | Description | Example |
|------|-------------|---------|
| **Length** | 2-5 words per filename | `neural-simulation-mouse-brain` |
| **Separators** | Use hyphens (`-`), never underscores | `brain-emulation-overview` |
| **Case** | Always lowercase | `connectomics-cost-trends` |
| **Keywords first** | Lead with the most important term | `neural-recording-capabilities` |
| **Descriptive** | Describe what the image actually shows | `neuron-counts-organism-comparison` |
| **No abbreviations** | Write full words for SEO | `simulation` not `sim` |
| **No dates in filename** | Keep dates in metadata only | Avoids long-term SEO issues |
| **No keyword stuffing** | Don't repeat terms unnecessarily | Natural, readable names |

### Filename Structure

```
{primary-subject}-{specifics}-{context}.svg
```

**Examples:**
- General figures: `brain-emulation-compute-requirements.svg`
- Organism-specific: `neural-simulation-mouse-brain.svg`
- Comparisons: `neuron-counts-organism-comparison.svg`
- Technology: `neuroimaging-modalities-comparison.svg`

### Organism-Specific Figures

For figures focused on a single organism, include the organism name:
- `neural-simulation-celegans-brain.svg`
- `neural-recording-drosophila-brain.svg`
- `neural-recording-mouse-moving.svg`
- `connectomics-zebrafish-larval-brain.svg`

### Hand-Drawn Figures

Same conventions apply. Use descriptive names that explain the illustration:
- `brain-emulation-pipeline-overview.svg`
- `mouse-digital-twin-concept.svg`
- `celegans-connectome-original.svg`

## Common Tasks

### Adding a New Figure

1. Add a function in `scripts/run_all_figures.py` with the `@figure()` decorator
2. Use styling from `style.py`
3. Save to `paths.GENERATED_FIGURES_DIR`
4. Update `dist/figures/generated/_metadata.json` if needed

### Serving Data Locally

```bash
cd dist
python3 -m http.server 8000
# Access figures metadata at http://localhost:8000/figures/generated/_metadata.json
```

## Data Categories

| Category | Location | Description |
|----------|----------|-------------|
| Neural Simulations | `data/simulations/*.tsv` | Neuron/synapse counts, 1957-2025 |
| Neural Recordings | `data/recordings/*.tsv` | Recording capabilities by organism |
| Connectomics | `data/connectomics/*.tsv` | Brain tissue scanning data |
| AI Compute | `data/compute/*.tsv` | AI training compute trends |
| Storage Costs | `data/costs/*.tsv` | Storage cost evolution |
| Initiatives | `data/initiatives/*.tsv` | Global brain research programs |
| Formulas | `data/formulas/*.tsv` | Calculator formula definitions |
| Imaging | `data/imaging/*.tsv` | Imaging modality data |

## Data Attribution

All data files in `data/` have corresponding metadata in `data/_metadata/` (mirrored structure).
See README.md "Data Attribution Guidelines" for the metadata schema and contributor guidelines.

## Reference Management

The repository uses a centralized bibliography system for tracking sources and citations.

### Bibliography Location

```
data/references/
└── bibliography.json    # CSL-JSON format bibliography (auto-generated)
```

### Building the Bibliography

The bibliography is extracted programmatically from existing source columns in TSV files:

```bash
cd scripts
python3 build_bibliography.py           # Extract sources and build bibliography
python3 build_bibliography.py --dry-run # Preview without writing files
python3 build_bibliography.py --no-api  # Skip CrossRef API lookups (faster)
```

The script:
1. Scans all TSV files for source columns (`source`, `ref`, `References`, `DOI`, `Link`)
2. Extracts DOIs and fetches metadata from CrossRef API
3. Generates ref_ids in `author2024` format
4. Creates CSL-JSON bibliography entries
5. Produces an audit log at `data/references/extraction_audit.json`

### Reference ID Convention

| Source Type | Pattern | Examples |
|-------------|---------|----------|
| Paper (single author) | `author2024` | `stevenson2011`, `herculano2009` |
| Paper (multi-author) | `firstauthor2024` | `dorkenwald2024` |
| Same author, same year | `author2024a`, `author2024b` | `koch2024a`, `koch2024b` |
| Organization/Website | `org_name_2024` | `aws_pricing_2024`, `wikipedia_tat8_2024` |
| Internal estimate | `internal_estimate_2024` | For values without external source |

### Adding Sources to Parameters (Future)

When the parameter schema is extended, use these columns:

| Column | Required | Values |
|--------|----------|--------|
| `ref_id` | Yes | ID from bibliography.json |
| `supporting_refs` | No | Semicolon-separated additional ref_ids |
| `ref_note` | No | Specific location: "Table 2", "Section 4.2" |
| `confidence` | Yes | `measured`, `derived`, `estimated`, `assumed` |
| `validated_by` | Yes | `human`, `ai`, `human+ai`, `none` |

### Confidence Levels

| Value | Definition |
|-------|------------|
| `measured` | Direct measurement from source |
| `derived` | Calculated from source data |
| `estimated` | Informed estimate with methodology |
| `assumed` | Assumption without direct evidence |

### Validation Levels

| Value | Definition |
|-------|------------|
| `human` | Human verified the value |
| `ai` | AI extracted, not human-verified |
| `human+ai` | AI-assisted, human-confirmed |
| `none` | Not validated (legacy data) |

## Dependencies

Key Python packages (see `requirements.txt`):
- matplotlib, seaborn - Visualization
- pandas, numpy - Data manipulation
- statsmodels - Statistical modeling
- openpyxl - Excel file support

## Quality Checks (IMPORTANT)

**Always run validation before committing changes:**

```bash
cd scripts
python3 validate.py          # Run all checks
python3 validate.py --strict # Fail on warnings too
python3 validate.py --ci     # Skip checks requiring generated content
```

### Validation Modes

| Mode | Use Case |
|------|----------|
| Default | Full validation - requires figures to be generated first |
| `--strict` | Treats warnings as failures |
| `--ci` | Skips checks that require generated content (figures, dist/data/) |

**Important**: Full validation (without `--ci`) requires figures to be generated first:

```bash
cd scripts/figures
python3 run_all_figures.py   # Generate figures to dist/
cd ..
python3 validate.py          # Now run full validation
```

The CI pipeline uses `--ci` mode since figure generation is a separate step.

### Pre-commit Hooks

Install pre-commit hooks to automatically run validation before each commit:

```bash
pip install pre-commit
pre-commit install
```

Hooks run automatically on `git commit`. To run manually:

```bash
pre-commit run --all-files
```

The validation script checks:

| Tier | Check | What It Catches |
|------|-------|-----------------|
| **1 - Critical** | SVG/PNG pairs | Missing format pairs for figures |
| **1 - Critical** | Zero-size files | Corrupt or failed generation |
| **1 - Critical** | Metadata-file sync | Broken references in metadata |
| **1 - Critical** | Orphan figures | Undocumented figures |
| **2 - Data** | Data files exist | Missing CSV source files |
| **2 - Data** | Data file content | Empty or truncated datasets |
| **2 - Data** | Source data files | Missing files referenced in paths.py |
| **2 - Data** | TSV format | Column count mismatches, BOM, trailing whitespace |
| **3 - Consistency** | Organism taxonomy | Invalid organism tags |
| **3 - Consistency** | Type taxonomy | Invalid type tags |
| **3 - Consistency** | ID uniqueness | Duplicate IDs across metadata |
| **3 - Consistency** | License consistency | Missing license in metadata |
| **4 - Reporting** | File sizes | Size metrics for monitoring |
| **4 - Reporting** | Hand-drawn figures | PNG+SVG pairs for hand-drawn |
| **4 - Reporting** | Stale figures | Source data newer than generated figures |
| **5 - Bibliography** | Bibliography exists | Missing or invalid bibliography.json |
| **5 - Bibliography** | Bibliography schema | Missing required fields in entries |
| **5 - Bibliography** | Bibliography duplicates | Duplicate DOIs or URLs |
| **5 - Bibliography** | Ref ID format | Invalid ref_id naming convention |
| **5 - Bibliography** | TSV column values | Invalid confidence/validated_by values |
| **6 - SEO** | Title quality | Titles too short for alt text/SEO |

### SEO Length Limits

The validation script enforces platform-specific character limits:

| Field | Max Length | Platform |
|-------|------------|----------|
| `<title>` | 60 chars | Google SERP |
| meta description | 160 chars | Google SERP |
| og:title | 90 chars | Facebook/LinkedIn |
| og:description | 200 chars | Facebook |
| twitter:title | 70 chars | X/Twitter |
| twitter:description | 200 chars | X/Twitter |
| alt text | 125 chars | Screen readers |

### Known Exceptions

Some legacy assets don't follow all conventions. These are documented in `scripts/validate.py` under `KNOWN_EXCEPTIONS`. If you need to add new exceptions, document them there with a comment explaining why.

## Notes for Claude Instances

- **Run `validate.py` before every commit** to catch issues early
- **Regenerate figures before full validation**: Run `run_all_figures.py` before `validate.py` (without `--ci`)
- No unit test suite exists - validation + visual inspection are the quality gates
- The web interface is self-contained and can be embedded via iframes
- All figures are licensed under CC BY 4.0
- When modifying figures, regenerate using `run_all_figures.py`
- JSON metadata files control the web interface display
- If validation fails, fix the issues before committing
- Use `validate.py --ci` if you only changed source data/code (not figures)
