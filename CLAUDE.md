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
│   ├── build_downloads.py     # ZIP archive builder
│   └── build_standalone_html.py # HTML inliner for embedding
├── data/                       # Source datasets (CSV files)
│   ├── ai-compute/            # AI training compute data
│   ├── brain-scans/           # Connectomics scanning data
│   ├── initiatives/           # Research initiatives data
│   └── storage-costs/         # Storage cost trends
├── data-and-figures/          # Self-contained web interface
│   ├── figures/generated/     # Output SVG and PNG figures
│   ├── metadata/              # JSON metadata for web interface
│   └── *.html                 # Interactive web pages
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

## Code Conventions

1. **Figure Registration**: Use the `@figure()` decorator to register new figures
2. **Styling**: Always use `style.py` for colors, fonts, and chart settings
3. **Paths**: Use `paths.py` for all file paths
4. **Output Formats**: Generate both SVG and PNG (150 DPI) for each figure
5. **Attribution**: All figures include "Zanichelli, Schons et al, State of Brain Emulation Report 2025"

## Common Tasks

### Adding a New Figure

1. Add a function in `scripts/run_all_figures.py` with the `@figure()` decorator
2. Use styling from `style.py`
3. Save to `paths.GENERATED_FIGURES_DIR`
4. Update `data-and-figures/metadata/figures-metadata.json` if needed

### Viewing the Web Interface

```bash
cd data-and-figures
python3 -m http.server 8000
# Open http://localhost:8000/figures.html
```

### Building Standalone HTML

```bash
cd scripts
python3 build_standalone_html.py
```

## Data Categories

| Category | Location | Description |
|----------|----------|-------------|
| Neural Simulations | `data/*.csv` | Neuron/synapse counts, 1957-2025 |
| Neural Recordings | `data/*.csv` | Recording capabilities by organism |
| Connectomics | `data/brain-scans/` | Brain tissue scanning data |
| AI Compute | `data/ai-compute/` | AI training compute trends |
| Storage Costs | `data/storage-costs/` | Storage cost evolution |
| Initiatives | `data/initiatives/` | Global brain research programs |

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
| **3 - Consistency** | Organism taxonomy | Invalid organism tags |
| **3 - Consistency** | Type taxonomy | Invalid type tags |
| **3 - Consistency** | ID uniqueness | Duplicate IDs across metadata |
| **3 - Consistency** | License consistency | Missing license in metadata |
| **4 - Reporting** | File sizes | Size metrics for monitoring |
| **4 - Reporting** | Hand-drawn figures | PNG+SVG pairs for hand-drawn |
| **5 - SEO** | HTML meta tags | Missing description, OG, Twitter tags |
| **5 - SEO** | HTML lang attribute | Missing lang="en" on HTML elements |
| **5 - SEO** | Heading hierarchy | H1→H3 skips, multiple H1s |
| **5 - SEO** | External link security | Missing rel="noopener noreferrer" |
| **5 - SEO** | Title quality | Titles too short for alt text/SEO |
| **5 - SEO** | SEO length limits | Tags exceeding platform character limits |

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

Current known exceptions:
- `radar-charts/*.png` - Legacy figures without SVG source (from old codebase)

## Notes for Claude Instances

- **Run `validate.py` before every commit** to catch issues early
- No unit test suite exists - validation + visual inspection are the quality gates
- The web interface is self-contained and can be embedded via iframes
- All figures are licensed under CC BY 4.0
- When modifying figures, regenerate using `run_all_figures.py`
- JSON metadata files control the web interface display
- If validation fails, fix the issues before committing
