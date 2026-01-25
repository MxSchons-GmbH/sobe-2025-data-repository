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
DATA_PARAMETERS = DATA_DIR / "parameters"
DATA_IMAGING = DATA_DIR / "imaging"
DATA_INITIATIVES = DATA_DIR / "initiatives"
DATA_METADATA = DATA_DIR / "_metadata"
DATA_REFERENCES = DATA_DIR / "references"

# Output directories (distribution-ready assets for website)
OUTPUT_ROOT = REPO_ROOT / "dist"
OUTPUT_FIGURES = OUTPUT_ROOT / "figures" / "generated"
OUTPUT_FIGURES_NEURO_SIM = OUTPUT_FIGURES / "neuro-sim"
OUTPUT_FIGURES_NEURO_REC = OUTPUT_FIGURES / "neuro-rec"
OUTPUT_FIGURES_HAND_DRAWN = OUTPUT_ROOT / "figures" / "hand-drawn"
OUTPUT_DATA = OUTPUT_ROOT / "data"
OUTPUT_DATA_METADATA = OUTPUT_DATA / "_metadata.json"
OUTPUT_FIGURES_METADATA = OUTPUT_FIGURES / "_metadata.json"
OUTPUT_HAND_DRAWN_METADATA = OUTPUT_FIGURES_HAND_DRAWN / "_metadata.json"
OUTPUT_DOWNLOADS = OUTPUT_ROOT / "downloads"
OUTPUT_CSS = OUTPUT_ROOT / "css"
OUTPUT_JS = OUTPUT_ROOT / "js"
OUTPUT_REFERENCES = OUTPUT_ROOT / "references"

# Calculator outputs
OUTPUT_CALCULATOR = OUTPUT_ROOT / "calculator"
OUTPUT_CALCULATOR_DATA = OUTPUT_CALCULATOR / "data.json"
OUTPUT_CALCULATOR_TYPES = OUTPUT_CALCULATOR / "types.ts"
OUTPUT_CALCULATOR_DOCS = OUTPUT_CALCULATOR / "docs"

# Specific data files (commonly used)
DATA_FILES = {
    # Simulations
    "neuron_simulations": DATA_SIMULATIONS / "neuron-simulations.tsv",
    "computational_models": DATA_SIMULATIONS / "computational-models.tsv",

    # Recordings
    "neural_recordings": DATA_RECORDINGS / "neural-recordings.tsv",
    "neural_dynamics": DATA_RECORDINGS / "neural-dynamics-references.tsv",
    "neurodynamics_papers": DATA_RECORDINGS / "neurodynamics-papers.tsv",
    "neurodynamics_organisms": DATA_RECORDINGS / "neurodynamics-organisms.tsv",
    "neural_information_rate": DATA_RECORDINGS / "neural-information-rate.tsv",
    "comparison_recordings": DATA_RECORDINGS / "comparison-recordings.tsv",
    "comparison_methods_volumes": DATA_RECORDINGS / "comparison-methods-volumes.tsv",
    "neuroscience_repositories": DATA_RECORDINGS / "neuroscience-repositories.tsv",

    # Connectomics
    "brain_scans": DATA_CONNECTOMICS / "brain-scans.tsv",
    "connectomics_2nm": DATA_CONNECTOMICS / "connectomics-2nm.tsv",
    "connectomics_10nm": DATA_CONNECTOMICS / "connectomics-10nm.tsv",
    "connectomics_25nm": DATA_CONNECTOMICS / "connectomics-25nm.tsv",
    "connectomics_50nm": DATA_CONNECTOMICS / "connectomics-50nm.tsv",
    "tracing_trends": DATA_CONNECTOMICS / "tracing-trends-references.tsv",

    # Compute
    "ai_compute": DATA_COMPUTE / "ai-training-computation.tsv",
    "computational_demands": DATA_COMPUTE / "computational-demands-organisms.tsv",
    "compute_hardware": DATA_COMPUTE / "hardware-characteristics.tsv",

    # Costs
    "storage_costs": DATA_COSTS / "storage-historical.tsv",
    "cost_estimates": DATA_COSTS / "neuron-reconstruction-estimates.tsv",
    "costs_neuro_megaprojects": DATA_COSTS / "neuroscience-megaprojects.tsv",
    "costs_non_neuro_megaprojects": DATA_COSTS / "non-neuroscience-megaprojects.tsv",

    # Organisms
    "organisms": DATA_ORGANISMS / "organisms.tsv",
    "organism_characteristics": DATA_ORGANISMS / "organism-characteristics.tsv",

    # Initiatives
    "initiatives_overview": DATA_INITIATIVES / "brain-initiatives-overview.tsv",
    "initiatives_costs": DATA_INITIATIVES / "digital-human-intelligence-costs.tsv",

    # Imaging
    "imaging_speed": DATA_IMAGING / "neuroimaging-speed.tsv",

    # Formulas (TSV files for calculator)
    "formulas_connectomics": DATA_FORMULAS / "connectomics.tsv",
    "formulas_costs": DATA_FORMULAS / "costs.tsv",
    "formulas_storage": DATA_FORMULAS / "storage.tsv",

    # Shared parameters
    "formulas_shared": DATA_PARAMETERS / "shared.tsv",

    # Imaging modalities
    "imaging_modalities": DATA_IMAGING / "imaging-modalities.tsv",

    # Recording parameters
    "neural_recording_params": DATA_RECORDINGS / "neural-recording.tsv",

    # Proofreading costs
    "proofreading": DATA_COSTS / "proofreading.tsv",

    # References/Bibliography
    "bibliography": DATA_REFERENCES / "bibliography.json",
}


def ensure_output_dirs():
    """Create all output directories if they don't exist."""
    for dir_path in [
        OUTPUT_FIGURES,
        OUTPUT_FIGURES_NEURO_SIM,
        OUTPUT_FIGURES_NEURO_REC,
        OUTPUT_FIGURES_HAND_DRAWN,
        OUTPUT_DATA,
        OUTPUT_DOWNLOADS,
        OUTPUT_CALCULATOR,
        OUTPUT_CALCULATOR_DOCS,
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)
