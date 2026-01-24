"""
Brain Emulation Report 2025 - Shared Data Loader

Provides unified access to TSV parameter files for both Python figure
generation and cross-referencing with the TypeScript calculator.

All canonical data lives in data/ subdirectories and is read from TSV files.
"""

import csv
from pathlib import Path
from typing import Dict, Any, Optional

# Data directories (relative to repo root)
REPO_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = REPO_ROOT / "data"


def load_tsv(filepath: Path) -> list[dict]:
    """Load a TSV file and return list of row dicts."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        return list(reader)


def load_organisms() -> Dict[str, Dict[str, Any]]:
    """
    Load organisms from canonical TSV file.

    Returns dict keyed by organism ID with fields:
        - name: Display name
        - neurons: Neuron count (int)
        - volume_mm3: Brain volume in mm³ (float)
        - synapses: Synapse count (float)
        - source: Data source reference
    """
    filepath = DATA_DIR / "organisms" / "organisms.tsv"
    rows = load_tsv(filepath)

    organisms = {}
    for row in rows:
        organisms[row['id']] = {
            'name': row['name'],
            'neurons': int(float(row['neurons'])),
            'volume_mm3': float(row['volume_mm3']),
            'synapses': float(row['synapses']),
            'source': row.get('source', ''),
        }
    return organisms


def get_species_neurons() -> Dict[str, int]:
    """
    Get neuron counts formatted for figure annotations.

    Returns dict with display names as keys (matching style.py format).
    """
    organisms = load_organisms()

    # Map organism IDs to display names used in figures
    name_mapping = {
        'c_elegans': 'C. elegans',
        'drosophila': 'Drosophila',
        'zebrafish_larva': 'Zebrafish (larva)',
        'mouse': 'Mouse',
        'macaque': 'Macaque',
        'human': 'Human',
    }

    return {
        name_mapping[org_id]: data['neurons']
        for org_id, data in organisms.items()
        if org_id in name_mapping
    }


def get_compute_requirements() -> Dict[str, float]:
    """
    Get compute requirements in petaFLOPS by organism.

    Loaded from data/compute/compute-requirements.tsv.

    Returns dict with display names as keys.
    """
    filepath = DATA_DIR / "compute" / "compute-requirements.tsv"
    rows = load_tsv(filepath)

    return {
        row['name']: float(row['compute_pflops'])
        for row in rows
    }


def get_storage_requirements() -> Dict[str, float]:
    """
    Get storage requirements in TB by organism.

    Loaded from data/compute/storage-requirements.tsv.

    Returns dict with display names as keys.
    """
    filepath = DATA_DIR / "compute" / "storage-requirements.tsv"
    rows = load_tsv(filepath)

    return {
        row['name']: float(row['storage_tb'])
        for row in rows
    }


def load_imaging_modalities() -> Dict[str, Dict[str, Any]]:
    """
    Load imaging modality parameters from TSV.

    Returns dict keyed by modality ID.
    """
    filepath = DATA_DIR / "imaging" / "imaging-modalities.tsv"
    rows = load_tsv(filepath)

    modalities = {}
    for row in rows:
        modalities[row['id']] = {
            'name': row['name'],
            'definition': row.get('definition', ''),
            'unit': row.get('unit', ''),
            'value': row.get('value', ''),
        }
    return modalities


def load_formulas(formula_type: str) -> Dict[str, Dict[str, Any]]:
    """
    Load formulas from TSV file.

    Args:
        formula_type: One of 'connectomics', 'costs', 'storage'

    Returns dict keyed by formula ID.
    """
    filepath = DATA_DIR / "formulas" / f"{formula_type}.tsv"
    rows = load_tsv(filepath)

    formulas = {}
    for row in rows:
        formulas[row['id']] = {
            'name': row.get('name', ''),
            'definition': row.get('definition', ''),
            'formula': row.get('formula', ''),
            'unit': row.get('unit', ''),
        }
    return formulas


def load_shared_params() -> Dict[str, Dict[str, Any]]:
    """
    Load shared project parameters from TSV.

    Returns dict keyed by parameter ID.
    """
    filepath = DATA_DIR / "parameters" / "shared.tsv"
    rows = load_tsv(filepath)

    params = {}
    for row in rows:
        params[row['id']] = {
            'name': row['name'],
            'definition': row.get('definition', ''),
            'unit': row.get('unit', ''),
            'value': row.get('value', ''),
        }
    return params
