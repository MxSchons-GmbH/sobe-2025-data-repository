# State of Brain Emulation Report 2025

Data repository and visualization pipeline for the State of Brain Emulation Report 2025.

## Overview

This repository generates publication-quality figures tracking progress in brain emulation research, covering:

- **Neural Simulations** - From C. elegans (302 neurons) to human-scale models (86 billion neurons)
- **Neural Recordings** - Advances in recording technology across organisms
- **Connectomics** - Brain tissue scanning and connectome reconstruction
- **Computational Requirements** - Hardware and storage needs for brain emulation
- **Funding & Initiatives** - Global brain research programs and their budgets

## Citation

If you use this data or figures in your work, please cite:

> Zanichelli, N., Schons, M., Shiu, P., Freeman, I., & Arkhipov, A. (2026). State of Brain Emulation Report 2025 (Version 1). Zenodo. https://doi.org/10.5281/zenodo.18377594

**BibTeX:**

```bibtex
@software{zanichelli2026sobe,
  author       = {Zanichelli, Nicola and Schons, Maximilian and Shiu, Patrick and Freeman, Ian and Arkhipov, Anton},
  title        = {State of Brain Emulation Report 2025},
  year         = 2026,
  publisher    = {Zenodo},
  version      = {1},
  doi          = {10.5281/zenodo.18377594},
  url          = {https://doi.org/10.5281/zenodo.18377594}
}
```

## Data Quality Notice

This repository contains data that has been recently transferred and consolidated from multiple sources. Quality control and validation is ongoing, with completion expected in Q1 2026. If you notice any discrepancies or errors, please [open an issue](https://github.com/MxSchons-GmbH/sobe-2025-data-repository/issues).

## Quick Start

```bash
# Clone and setup
git clone https://github.com/MxSchons-GmbH/sobe-2025-data-repository.git
cd sobe-2025-data-repository
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
│   ├── references/                   # Centralized bibliography (CSL-JSON)
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
    ├── references/                   # Bibliography for web access
    │   └── bibliography.json         # CSL-JSON format (mirrors data/references/)
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
| `build_bibliography.py` | Extracts sources from TSVs, builds CSL-JSON bibliography |
| `validate.py` | Runs quality checks on figures and metadata |

## Generated Figures

The pipeline produces 38+ figures across categories:

**Overview Figures**
- `all-sim-rec` - Neural simulations & recordings combined
- `num-neurons` - Neuron count comparisons over time
- `imaging-speed` - Neuroimaging technology progress

**Computational**
- `compute` - Hardware trends
- `gpu-memory` - Single GPU memory vs brain emulation requirements
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

## Reference Management

The repository uses a centralized bibliography for tracking data sources.

### Bibliography

The bibliography is stored in CSL-JSON format at `data/references/bibliography.json` (1,130+ references). It is also distributed at `dist/references/bibliography.json` for web access.

### Building the Bibliography

```bash
cd scripts
python3 build_bibliography.py           # Extract sources and build bibliography
python3 build_bibliography.py --dry-run # Preview without writing
python3 build_bibliography.py --no-api  # Skip CrossRef API lookups (faster)
```

The script extracts DOIs and URLs from TSV source columns, fetches metadata from CrossRef, and generates ref_ids in `author2024` format.

### Reference Columns in TSV Files

Parameter and formula files include columns for source tracking:

| Column | Description |
|--------|-------------|
| `ref_id` | ID linking to bibliography.json entry |
| `supporting_refs` | Additional reference IDs (semicolon-separated) |
| `ref_note` | Specific location: "Table 2", "Section 4.2" |
| `confidence` | `measured`, `derived`, `estimated`, or `assumed` |
| `validated_by` | `human`, `ai`, `human+ai`, or `none` |

## License

All figures are licensed under **CC BY 4.0** (Creative Commons Attribution 4.0 International).

**Attribution**: Zanichelli, Schons et al., State of Brain Emulation Report 2025
