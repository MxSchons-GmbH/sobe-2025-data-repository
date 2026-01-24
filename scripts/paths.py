"""
Brain Emulation Report 2025 - Path Configuration

Centralized path definitions for all scripts.
All paths are absolute and derived from __file__ to work regardless of cwd.
"""

from pathlib import Path

# Repository root (one level up from scripts/)
REPO_ROOT = Path(__file__).parent.parent.resolve()

# Source data directories (organized by topic)
DATA_DIR = REPO_ROOT / "data"
DATA_SIMULATIONS = DATA_DIR / "simulations"
DATA_RECORDINGS = DATA_DIR / "recordings"
DATA_CONNECTOMICS = DATA_DIR / "connectomics"
DATA_COMPUTE = DATA_DIR / "compute"
DATA_COSTS = DATA_DIR / "costs"
DATA_ORGANISMS = DATA_DIR / "organisms"
DATA_FORMULAS = DATA_DIR / "formulas"
DATA_IMAGING = DATA_DIR / "imaging"
DATA_INITIATIVES = DATA_DIR / "initiatives"

# External data (third-party datasets)
DATA_EXTERNAL = DATA_DIR / "cboschp-wtlandscape_mbc-ca8b379"

# Output directories (the embeddable web interface)
OUTPUT_ROOT = REPO_ROOT / "data-and-figures"
OUTPUT_FIGURES = OUTPUT_ROOT / "figures" / "generated"
OUTPUT_FIGURES_NEURO_SIM = OUTPUT_FIGURES / "neuro-sim"
OUTPUT_FIGURES_NEURO_REC = OUTPUT_FIGURES / "neuro-rec"
OUTPUT_FIGURES_HAND_DRAWN = OUTPUT_ROOT / "figures" / "hand-drawn"
OUTPUT_DATA = OUTPUT_ROOT / "data"
OUTPUT_METADATA = OUTPUT_ROOT / "metadata"
OUTPUT_DOWNLOADS = OUTPUT_ROOT / "downloads"
OUTPUT_CSS = OUTPUT_ROOT / "css"
OUTPUT_JS = OUTPUT_ROOT / "js"

# Specific data files (commonly used)
DATA_FILES = {
    # Simulations
    "neuron_simulations": DATA_SIMULATIONS / "neuron-simulations.csv",
    "computational_models": DATA_SIMULATIONS / "computational-models.csv",

    # Recordings
    "neural_recordings": DATA_RECORDINGS / "neural-recordings.csv",
    "neural_dynamics": DATA_RECORDINGS / "neural-dynamics-references.csv",
    "neurodynamics_papers": DATA_RECORDINGS / "neurodynamics-papers.csv",
    "neurodynamics_organisms": DATA_RECORDINGS / "neurodynamics-organisms.csv",
    "neural_information_rate": DATA_RECORDINGS / "neural-information-rate.csv",
    "comparison_recordings": DATA_RECORDINGS / "comparison-recordings.csv",
    "comparison_methods_volumes": DATA_RECORDINGS / "comparison-methods-volumes.csv",
    "neuroscience_repositories": DATA_RECORDINGS / "neuroscience-repositories.csv",

    # Connectomics
    "brain_scans": DATA_CONNECTOMICS / "brain-scans.csv",
    "connectomics_2nm": DATA_CONNECTOMICS / "connectomics-2nm.csv",
    "connectomics_10nm": DATA_CONNECTOMICS / "connectomics-10nm.csv",
    "connectomics_25nm": DATA_CONNECTOMICS / "connectomics-25nm.csv",
    "connectomics_50nm": DATA_CONNECTOMICS / "connectomics-50nm.csv",
    "tracing_trends": DATA_CONNECTOMICS / "tracing-trends-references.csv",

    # Compute
    "ai_compute": DATA_COMPUTE / "ai-training-computation.csv",
    "computational_demands": DATA_COMPUTE / "computational-demands-organisms.csv",
    "compute_hardware": DATA_COMPUTE / "hardware-characteristics.csv",

    # Costs
    "storage_costs": DATA_COSTS / "storage-historical.csv",
    "cost_estimates": DATA_COSTS / "neuron-reconstruction-estimates.csv",
    "costs_neuro_megaprojects": DATA_COSTS / "neuroscience-megaprojects.csv",
    "costs_non_neuro_megaprojects": DATA_COSTS / "non-neuroscience-megaprojects.csv",

    # Organisms
    "organisms": DATA_ORGANISMS / "organisms.tsv",
    "organism_characteristics": DATA_ORGANISMS / "organism-characteristics.csv",

    # Initiatives
    "initiatives_overview": DATA_INITIATIVES / "brain-initiatives-overview.csv",
    "initiatives_costs": DATA_INITIATIVES / "digital-human-intelligence-costs.csv",

    # External data
    "imaging_speed": DATA_EXTERNAL / "0-data" / "maps_dates_230119.xlsx",

    # Formulas (TSV files for calculator)
    "formulas_connectomics": DATA_FORMULAS / "connectomics.tsv",
    "formulas_costs": DATA_FORMULAS / "costs.tsv",
    "formulas_storage": DATA_FORMULAS / "storage.tsv",
    "formulas_shared": DATA_FORMULAS / "shared.tsv",

    # Imaging modalities
    "imaging_modalities": DATA_IMAGING / "imaging-modalities.tsv",

    # Recording parameters
    "neural_recording_params": DATA_RECORDINGS / "neural-recording.tsv",

    # Proofreading costs
    "proofreading": DATA_COSTS / "proofreading.tsv",
}


def ensure_output_dirs():
    """Create all output directories if they don't exist."""
    for dir_path in [
        OUTPUT_FIGURES,
        OUTPUT_FIGURES_NEURO_SIM,
        OUTPUT_FIGURES_NEURO_REC,
        OUTPUT_FIGURES_HAND_DRAWN,
        OUTPUT_DATA,
        OUTPUT_METADATA,
        OUTPUT_DOWNLOADS,
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)
