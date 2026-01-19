"""
Brain Emulation Report 2025 - Path Configuration

Centralized path definitions for all scripts.
All paths are absolute and derived from __file__ to work regardless of cwd.
"""

from pathlib import Path

# Repository root (one level up from scripts/)
REPO_ROOT = Path(__file__).parent.parent.resolve()

# Source data directories
DATA_DIR = REPO_ROOT / "data"
DATA_AI_COMPUTE = DATA_DIR / "ai-compute"
DATA_BRAIN_SCANS = DATA_DIR / "brain-scans"
DATA_INITIATIVES = DATA_DIR / "initiatives"
DATA_STORAGE_COSTS = DATA_DIR / "storage-costs"

# Output directories (the embeddable web interface)
OUTPUT_ROOT = REPO_ROOT / "data-and-figures"
OUTPUT_FIGURES = OUTPUT_ROOT / "figures" / "generated"
OUTPUT_FIGURES_NEURO_SIM = OUTPUT_FIGURES / "neuro-sim"
OUTPUT_FIGURES_NEURO_REC = OUTPUT_FIGURES / "neuro-rec"
OUTPUT_FIGURES_RADAR = OUTPUT_FIGURES / "radar-charts"
OUTPUT_FIGURES_HAND_DRAWN = OUTPUT_ROOT / "figures" / "hand-drawn"
OUTPUT_DATA = OUTPUT_ROOT / "data"
OUTPUT_METADATA = OUTPUT_ROOT / "metadata"
OUTPUT_DOWNLOADS = OUTPUT_ROOT / "downloads"
OUTPUT_CSS = OUTPUT_ROOT / "css"
OUTPUT_JS = OUTPUT_ROOT / "js"

# Specific data files (commonly used)
DATA_FILES = {
    "neuron_simulations": DATA_DIR / "Neuron Simulations - TASK 3 - Sheet1.csv",
    "imaging_speed": DATA_DIR / "cboschp-wtlandscape_mbc-ca8b379" / "0-data" / "maps_dates_230119.xlsx",
    "ai_compute": DATA_AI_COMPUTE / "artificial-intelligence-training-computation.csv",
    "storage_costs": DATA_STORAGE_COSTS / "historical-cost-of-computer-memory-and-storage.csv",
    "neural_recordings": DATA_DIR / "Neural recordings - Neurons_year.csv",
    "brain_scans": DATA_BRAIN_SCANS / "Copy of (best) Upwork_TASK 1 (2) - Sheet1.csv",
    "cost_estimates": DATA_DIR / "State of Brain Emulation Report 2025 Data Repository - Cost estimates Neuron Reconstruction.csv",
    "initiatives_overview": DATA_INITIATIVES / "Overview of Brain Initiatives T4 v2.xlsx - Sheet1.csv",
    "initiatives_costs": DATA_INITIATIVES / "Digital Human Intelligence Figures - Costs of different projects.csv",
    "computational_models": DATA_DIR / "State of Brain Emulation Report 2025 Data Repository - Computational Models of the Brain.csv",
    "neural_dynamics": DATA_DIR / "State of Brain Emulation Report 2025 Data Repository - Neural Dynamics References.csv",
    "neurodynamics_papers": DATA_DIR / "Neurodynamics recording papers - Papers.csv",
    "neurodynamics_organisms": DATA_DIR / "Neurodynamics recording papers - Organisms.csv",
    "costs_neuro_megaprojects": DATA_DIR / "State of Brain Emulation Report 2025 Data Repository - Costs Neuroscience Megaprojects.csv",
    "costs_non_neuro_megaprojects": DATA_DIR / "State of Brain Emulation Report 2025 Data Repository - Costs Non-Neuroscience Megaprojects.csv",
    "computational_demands": DATA_DIR / "State of Brain Emulation Report 2025 Data Repository - Computational Demands Organisms.csv",
}


def ensure_output_dirs():
    """Create all output directories if they don't exist."""
    for dir_path in [
        OUTPUT_FIGURES,
        OUTPUT_FIGURES_NEURO_SIM,
        OUTPUT_FIGURES_NEURO_REC,
        OUTPUT_FIGURES_RADAR,
        OUTPUT_FIGURES_HAND_DRAWN,
        OUTPUT_DATA,
        OUTPUT_METADATA,
        OUTPUT_DOWNLOADS,
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)
