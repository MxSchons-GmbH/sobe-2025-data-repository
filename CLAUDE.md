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

## Notes for Claude Instances

- No test suite exists - focus on visual inspection of generated figures
- The web interface is self-contained and can be embedded via iframes
- All figures are licensed under CC BY 4.0
- When modifying figures, regenerate using `run_all_figures.py`
- JSON metadata files control the web interface display
