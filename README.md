# State of Brain Emulation Report 2025

**📱 Phone Display Test - January 19, 2026 at 13:08 UTC**

Data visualization pipeline and interactive figure library for the State of Brain Emulation Report 2025.

## Overview

This repository generates publication-quality figures tracking progress in brain emulation research, covering:

- **Neural Simulations** - From C. elegans (302 neurons) to human-scale models (86 billion neurons)
- **Neural Recordings** - Advances in recording technology across organisms
- **Connectomics** - Brain tissue scanning and connectome reconstruction
- **Computational Requirements** - Hardware and storage needs for brain emulation
- **Funding & Initiatives** - Global brain research programs and their budgets

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd sobe25-scripts
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate all figures
cd scripts
python3 run_all_figures.py

# Build downloadable archives
python3 build_downloads.py
```

## Repository Structure

```
sobe-2025-data-repository/
├── scripts/                          # Figure generation code
│   ├── style.py                      # Centralized style configuration
│   ├── run_all_figures.py            # Main pipeline (generates all figures)
│   ├── build_downloads.py            # Creates ZIP archives
│   └── validate.py                   # Quality validation checks
├── data/                             # Source datasets (TSV format)
│   ├── compute/                      # AI training, hardware data
│   ├── connectomics/                 # Brain scanning data
│   ├── costs/                        # Cost estimates, megaprojects
│   ├── formulas/                     # Calculator formulas
│   ├── imaging/                      # Imaging modalities
│   ├── initiatives/                  # Brain research programs
│   ├── organisms/                    # Organism reference data
│   ├── parameters/                   # Shared calculation parameters
│   ├── recordings/                   # Neural recording data
│   ├── simulations/                  # Simulation history data
│   └── _metadata/                    # Attribution metadata (mirrors data/ structure)
└── dist/                 # Data assets for website
    ├── figures/
    │   ├── generated/                # Programmatic figures (SVG, PNG, WebP, AVIF)
    │   │   ├── _metadata.json        # Generated figures catalog
    │   │   ├── neuro-sim/            # Per-organism simulation figures
    │   │   └── neuro-rec/            # Per-organism recording figures
    │   └── hand-drawn/               # Anatomical illustrations
    │       └── _metadata.json        # Hand-drawn figures catalog
    ├── data/                         # TSV datasets (mirrors data/ structure)
    │   └── _metadata.json            # Datasets catalog
    └── downloads/                    # ZIP archives for bulk download
```

> **Note**: The web interface (HTML/CSS/JS) has been moved to the main website repository.
> This repo now provides only raw data, figures, and metadata JSON catalogs that the website consumes.

## Style System

All figures use a consistent visual language defined in `scripts/style.py`:

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Purple | `#6B6080` | Primary accent |
| Gold | `#D4A84B` | Highlight, first category |
| Teal | `#4A90A4` | Links, second category |

### Typography

- **Titles**: Playfair Display (serif)
- **Body**: Inter (sans-serif)
- **Code**: JetBrains Mono (monospace)

### Usage

```python
from style import apply_style, save_figure, GOLD, TEAL, PURPLE

apply_style()

fig, ax = plt.subplots()
# ... create your visualization ...
save_figure(fig, 'my-figure')  # Saves both .svg and .png
```

## Scripts

### Main Pipeline

| Script | Description |
|--------|-------------|
| `run_all_figures.py` | Generates all 25+ figures from source data |
| `build_downloads.py` | Creates ZIP archives with CC BY 4.0 license |
| `validate.py` | Runs quality checks on figures and metadata |

## Generated Figures

The pipeline produces 38+ figures across categories:

**Overview Figures**
- `all-sim-rec` - Neural simulations & recordings combined
- `num-neurons` - Neuron count comparisons over time
- `imaging-speed` - Neuroimaging technology progress

**Computational**
- `compute` - Hardware trends
- `storage-costs` - Data storage costs
- `emulation-compute-*` - Compute requirements for emulation
- `emulation-storage-requirements` - Storage needs

**Organism-Specific** (in subdirectories)
- `neuro-sim/` - Simulation progress by organism
- `neuro-rec/` - Recording capabilities by organism
- `radar-charts/` - Comparative capability charts

**Funding & Initiatives**
- `funding` - Research funding trends
- `initiatives*` - Brain research programs

All figures are saved in both **SVG** (vector) and **PNG** (150 DPI) formats.

## Data Assets

The `dist/` directory provides assets for the main website:

### What This Repo Provides

| Asset | Location | Format |
|-------|----------|--------|
| Generated figures | `figures/generated/` | SVG, PNG, WebP, AVIF |
| Figure metadata | `figures/generated/_metadata.json` | JSON |
| Hand-drawn figures | `figures/hand-drawn/` | SVG, PNG, WebP, AVIF |
| Hand-drawn metadata | `figures/hand-drawn/_metadata.json` | JSON |
| Datasets | `data/` | TSV |
| Dataset metadata | `data/_metadata.json` | JSON |
| Bulk downloads | `downloads/` | ZIP |

### How the Website Uses This Data

The main website repository reads the metadata JSON files and renders the UI natively.
When you add new figures or datasets:

1. Add the actual files (TSV, PNG, SVG)
2. Update the relevant metadata JSON
3. Regenerate ZIP archives if needed
4. The website will automatically display the new content

## Datasets

Source data is organized by topic:

| Category | Files | Description |
|----------|-------|-------------|
| Neural Simulations | 2 | Simulation neuron counts, 1957-2025 |
| Neural Recordings | 3 | Recording capabilities by organism |
| Connectomics | 5 | Brain tissue scanning at various resolutions |
| Computational Models | 2 | Model complexity and requirements |
| Costs | 4 | Neuron reconstruction costs, project budgets |
| Initiatives | 1 | Global brain research programs |
| Hardware | 2 | Compute characteristics, storage costs |
| AI/Compute | 1 | AI training compute trends |

## Adding Hand-Drawn Figures

1. Add PNG and SVG files to `dist/figures/hand-drawn/`
2. Update `dist/metadata/hand-drawn-metadata.json`:

```json
{
  "figures": [
    {
      "id": "my-figure",
      "title": "My Figure Title",
      "description": "Description of the figure.",
      "filename": "my-figure",
      "organism": ["all"],
      "type": ["hand-drawn", "anatomy"]
    }
  ]
}
```

3. Rebuild ZIP archives: `python3 scripts/build_downloads.py`

## Dependencies

```
matplotlib      # Plotting
seaborn         # Statistical visualization
pandas          # Data manipulation
numpy           # Numerical computing
statsmodels     # Statistical modeling
openpyxl        # Excel file support
nbconvert       # Notebook processing
ipykernel       # Jupyter kernel
```

## Data Attribution Guidelines

### Structure

All data files in `data/` have a corresponding metadata file in `data/_metadata/`, mirroring the folder structure:

```
data/
├── compute/
│   └── ai-training-computation.tsv
├── connectomics/
│   └── brain-scans.tsv
└── _metadata/
    ├── compute/
    │   └── ai-training-computation.json
    └── connectomics/
        └── brain-scans.json
```

### Metadata Schema

Each `.json` metadata file contains:

```json
{
  "title": "Human-readable dataset name",
  "source": "State of Brain Emulation Report 2025",
  "originalAuthor": "Original creator(s)",
  "contributors": ["Name (year)", "Name (year)"],
  "license": "CC BY 4.0",
  "url": "Source URL (external data only)",
  "dateAccessed": "YYYY-MM-DD (external data only)",
  "description": "Brief description of what this data contains"
}
```

### For Contributors

- **Adding a new dataset**: Create both the data file and corresponding metadata file
- **Modifying an existing dataset**: Add yourself to the `contributors` array with the year
- **External data**: Always include `url` and `dateAccessed`

### External Data Sources

| Dataset | Original Author | License |
|---------|-----------------|---------|
| `ai-training-computation.tsv` | Epoch via Our World in Data | CC BY 4.0 |
| `storage-historical.tsv` | John C. McCallum via Our World in Data | CC BY 4.0 |
| `neuroimaging-speed.tsv` | Carles Bosch | MIT |

## License

All figures are licensed under **CC BY 4.0** (Creative Commons Attribution 4.0 International).

**Attribution**: Zanichelli, Schons et al., State of Brain Emulation Report 2025
