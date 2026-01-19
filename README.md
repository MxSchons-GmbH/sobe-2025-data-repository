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
sobe25-scripts/
├── scripts/                          # Figure generation code
│   ├── style.py                      # Centralized style configuration
│   ├── run_all_figures.py            # Main pipeline (generates all figures)
│   ├── build_downloads.py            # Creates ZIP archives
│   ├── build_standalone_html.py      # Inlines CSS/JS into HTML
│   └── *.ipynb                       # Analysis notebooks
├── data/                             # Source datasets (CSV, Excel)
└── data-and-figures/                 # All outputs (self-contained)
    ├── figures/
    │   ├── generated/                # Programmatic figures (SVG + PNG)
    │   │   ├── neuro-sim/            # Per-organism simulation figures
    │   │   ├── neuro-rec/            # Per-organism recording figures
    │   │   └── radar-charts/         # Comparative radar charts
    │   └── hand-drawn/               # Anatomical illustrations
    ├── data/                         # Dataset copies for web interface
    ├── metadata/                     # JSON metadata for web interface
    │   ├── figures-metadata.json
    │   ├── data-metadata.json
    │   └── hand-drawn-metadata.json
    ├── downloads/                    # ZIP archives
    ├── css/                          # Stylesheets
    ├── js/                           # JavaScript
    ├── figures.html                  # Interactive figure library
    └── data.html                     # Interactive data repository
```

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
| `build_standalone_html.py` | Makes HTML pages self-contained for iframe embedding |

### Jupyter Notebooks

| Notebook | Description |
|----------|-------------|
| `ConnectomicsDataviz.ipynb` | Main visualization work |
| `January.ipynb` | Extended analysis |
| `information_rate.ipynb` | Compute/storage parallel coordinate plots |
| `Computational demands across organisms.ipynb` | Organism comparison charts |
| `Estimated Requirements for Brain Emulation.ipynb` | Emulation cost analysis |
| `comparison_recording_modalities.ipynb` | Recording technique comparison |
| `Cost_estimates_Neurons.ipynb` | Cost per neuron trends |

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

## Interactive Web Interface

The `data-and-figures/` directory contains a complete, self-contained web interface:

### Figure Library (`figures.html`)

- Filter by **organism** (C. elegans, Zebrafish, Mouse, Human, etc.)
- Filter by **type** (Simulation, Recording, Emulation, etc.)
- Filter by **source** (Generated vs Hand-Drawn)
- Download individual figures as PNG or SVG
- Download all figures as ZIP archives

### Data Repository (`data.html`)

- 24 datasets organized into 8 categories
- Direct CSV download links
- Table and card view options

### Serving Locally

```bash
cd data-and-figures
python3 -m http.server 8000
# Open http://localhost:8000/figures.html
```

### Embedding

The HTML files are self-contained (CSS/JS inlined) for easy iframe embedding:

```html
<iframe src="figures.html" width="100%" height="800"></iframe>
```

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

1. Add PNG and SVG files to `data-and-figures/figures/hand-drawn/`
2. Update `data-and-figures/metadata/hand-drawn-metadata.json`:

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

## License

All figures are licensed under **CC BY 4.0** (Creative Commons Attribution 4.0 International).

**Attribution**: Zanichelli, Schons et al., State of Brain Emulation Report 2025
