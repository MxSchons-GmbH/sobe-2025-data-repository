#!/usr/bin/env python3
"""
Run all figure generation scripts for the Brain Emulation Report 2025.
This script executes the key visualizations from each notebook.

Usage:
    python run_all_figures.py          # Generate all figures
    python run_all_figures.py --list   # List available figures
    python run_all_figures.py fig1 fig2  # Generate specific figures
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for script execution

import logging
import sys
from functools import wraps

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import datetime as dt

from style import (
    apply_style, save_figure, add_attribution,
    COLORS, PRIMARY_COLORS, CATEGORICAL_COLORS,
    GOLD, TEAL, PURPLE,
    SPECIES_NEURONS, plot_species_hlines,
    EXTENDED_CATEGORICAL, HARDWARE_COLORS
)
from paths import (
    DATA_DIR, DATA_FILES, OUTPUT_FIGURES,
    OUTPUT_FIGURES_NEURO_SIM, OUTPUT_FIGURES_NEURO_REC,
    ensure_output_dirs
)

# =============================================================================
# Logging Configuration
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# =============================================================================
# Figure Registry
# =============================================================================
FIGURE_REGISTRY = {}


def figure(name, description=""):
    """Decorator to register a figure generation function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Generating: {name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"  Done: {name}")
                return result
            except FileNotFoundError as e:
                logger.error(f"  Data file not found for {name}: {e}")
            except pd.errors.ParserError as e:
                logger.error(f"  CSV parsing error for {name}: {e}")
            except Exception as e:
                logger.error(f"  Error generating {name}: {e}", exc_info=True)
            return None
        FIGURE_REGISTRY[name] = {
            'func': wrapper,
            'description': description
        }
        return wrapper
    return decorator


# =============================================================================
# Style Setup
# =============================================================================
apply_style()

# Seaborn configuration
sns.set_theme(style="whitegrid")
import matplotlib as mpl
mpl.rcParams.update({
    'axes.facecolor': COLORS['plot_bg'],
    'figure.facecolor': COLORS['figure_bg'],
    'axes.edgecolor': COLORS['border'],
    'grid.color': COLORS['grid'],
    'text.color': COLORS['text'],
    'axes.labelcolor': COLORS['text'],
    'xtick.color': COLORS['text'],
    'ytick.color': COLORS['text'],
})

# =============================================================================
# Figure 1: Number of Neurons in Simulations
# =============================================================================
@figure("num-neurons", "Neuron simulation counts over time")
def generate_num_neurons():
    neurons_df = pd.read_csv(DATA_FILES["neuron_simulations"])
    neurons_df['Year'] = neurons_df['Simulation/Initiative'].str.extract(r'(\d{4})').apply(pd.to_datetime)

    min_year = neurons_df['Year'].min() - dt.timedelta(days=365)
    max_year = neurons_df['Year'].max() + dt.timedelta(days=365)
    label_year = dt.datetime(year=1985, month=1, day=1)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        neurons_df,
        x='Year',
        y='# of Neurons',
        style='Category',
        hue='Organism (random)',
        palette=CATEGORICAL_COLORS,
        s=60,
        alpha=0.8,
        ax=ax
    )
    plot_species_hlines(ax, min_year, max_year, label_year)
    ax.legend(bbox_to_anchor=(1.03, 1.03), frameon=True)
    ax.set_yscale('log')
    ax.set_xlim(min_year, max_year)
    ax.set_ylabel('Number of Neurons')
    ax.set_xlabel(None)
    ax.set_title('Neuron Simulations Over Time')
    plt.tight_layout()
    save_figure(fig, 'num-neurons')
    plt.close()

# =============================================================================
# Figure 2: Imaging Speed
# =============================================================================
@figure("imaging-speed", "Neuroimaging technology progress")
def generate_imaging_speed():
    imaging_speed_df = pd.read_excel(
        DATA_FILES["imaging_speed"],
        skiprows=[1],
        parse_dates=['released_year'],
    )
    imaging_speed_df['imagingRate_perMachine'] = pd.to_numeric(
        imaging_speed_df['imagingRate_perMachine'], errors='coerce'
    )

    min_date = dt.date(year=1980, month=1, day=1)
    max_date = dt.date(year=2024, month=1, day=1)

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    palette = CATEGORICAL_COLORS

    # Subplot 1
    sns.scatterplot(
        data=imaging_speed_df, x='released_year', y='imagingRate_perMachine',
        hue='img_tech', palette=palette, s=60, alpha=0.8, ax=axes[0], legend=False,
    )
    axes[0].set_yscale('log')
    axes[0].set_title('Imaging Rate (mm³/day/machine)')
    axes[0].set_xlim(min_date, max_date)
    axes[0].set_xlabel(None)
    axes[0].set_ylabel(None)

    # Subplot 2
    sns.scatterplot(
        data=imaging_speed_df, x='released_year', y='fov_mm3',
        hue='img_tech', palette=palette, s=60, alpha=0.8, ax=axes[1], legend=False,
    )
    axes[1].set_yscale('log')
    axes[1].set_title('Volumes Imaged (mm³)')
    axes[1].set_xlim(min_date, max_date)
    axes[1].set_xlabel(None)
    axes[1].set_ylabel(None)

    # Subplot 3
    sns.scatterplot(
        data=imaging_speed_df, x='released_year', y='dsSize_TB',
        hue='img_tech', palette=palette, s=60, alpha=0.8, ax=axes[2], legend=True,
    )
    axes[2].set_yscale('log')
    axes[2].set_title('Dataset Size (TB)')
    sns.move_legend(axes[2], "upper left", bbox_to_anchor=(1, 1), frameon=True)
    axes[2].set_xlim(min_date, max_date)
    axes[2].set_xlabel(None)
    axes[2].set_ylabel(None)

    plt.tight_layout()
    save_figure(fig, 'imaging-speed')
    plt.close()

# =============================================================================
# Figure 3: Compute
# =============================================================================
@figure("compute", "AI training compute vs species requirements")
def generate_compute():
    compute_df = pd.read_csv(
        DATA_FILES["ai_compute"],
        parse_dates=['Day']
    )

    species_pf = {'Human': 2000.0, 'Mouse': 10.0, 'Fly': 0.195}

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=compute_df, x='Day', y='Training computation (petaFLOP)',
        hue='Domain', palette=CATEGORICAL_COLORS, s=60, alpha=0.7, ax=ax
    )

    min_year = dt.datetime(year=1945, month=1, day=1)
    max_year = dt.datetime(year=2030, month=1, day=1)
    label_year = dt.datetime(year=1955, month=1, day=1)

    for name, val in species_pf.items():
        ax.axhline(y=val, color=COLORS['caption'], ls=':', lw=1, alpha=0.7)
        ax.text(label_year, val, f'  {name}', va='bottom', fontsize=10, color=COLORS['caption'])

    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1), frameon=True)
    ax.set_yscale('log')
    ax.set_xlabel('Year')
    ax.set_ylabel('Training Computation (petaFLOP)')
    ax.set_xlim(min_year, max_year)
    ax.set_title('AI Training Compute vs Species Requirements')
    plt.tight_layout()
    save_figure(fig, 'compute')
    plt.close()

# =============================================================================
# Figure 4: Storage Costs
# =============================================================================
@figure("storage-costs", "Storage costs over time with species thresholds")
def generate_storage_costs():
    storage_df = pd.read_csv(
        DATA_FILES["storage_costs"],
        parse_dates=['Year']
    )
    storage_df.rename(columns={
        'Historical price of memory': 'Memory',
        'Historical price of flash memory': 'Flash',
        'Historical price of disk drives': 'Disk',
        'Historical price of solid-state drives': 'Solid state',
    }, inplace=True)

    storage_dfl = pd.melt(
        storage_df, ['Year'],
        value_vars=['Memory', 'Flash', 'Disk', 'Solid state'],
        value_name='Cost ($ / TB)', var_name='Storage type',
    )

    species_storage_tb = {'Human': 6e3, 'Mouse': 2, 'Fruitfly': 2.5e-4, 'C. elegans': 1e-3}
    species_cost = {k: 1e6 / v for k, v in species_storage_tb.items()}

    min_year = storage_dfl['Year'].min()
    max_year = storage_dfl['Year'].max()
    label_year = dt.datetime(year=1958, month=1, day=1)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=storage_dfl, x='Year', y='Cost ($ / TB)',
        hue='Storage type', palette=PRIMARY_COLORS, linewidth=2.5, ax=ax
    )

    for name, val in species_cost.items():
        ax.axhline(y=val, color=COLORS['caption'], ls=':', lw=1, alpha=0.7)
        ax.text(label_year, val, f'  {name}', va='bottom', fontsize=10, color=COLORS['caption'])

    ax.set_yscale('log')
    ax.set_xlim(min_year, max_year)
    ax.set_ylabel('Cost ($ / TB)')
    ax.set_xlabel(None)
    ax.set_title('Storage Costs Over Time (Species Thresholds at $1M Budget)')
    ax.legend(frameon=True)
    plt.tight_layout()
    save_figure(fig, 'storage-costs')
    plt.close()

# =============================================================================
# Figure 5: Neural Recordings
# =============================================================================
@figure("neuro-recordings", "Neural recording capacity over time")
def generate_neuro_recordings():
    import statsmodels.formula.api as smf

    neuro_df = pd.read_csv(DATA_FILES["neural_recordings"])

    # Fit models
    ephys_fit = smf.rlm('np.log(Neurons) ~ Year', data=neuro_df.query('Method == "Ephys"')).fit()
    imag_fit = smf.rlm('np.log(Neurons) ~ Year', data=neuro_df.query('Method == "Imaging"')).fit()

    min_year = neuro_df['Year'].min()
    max_year = neuro_df['Year'].max()
    x_lin = np.linspace(min_year, max_year, 2)
    y_lin_ephys = np.exp(ephys_fit.params['Intercept'] + ephys_fit.params['Year'] * x_lin)
    y_lin_imag = np.exp(imag_fit.params['Intercept'] + imag_fit.params['Year'] * x_lin)

    # Rename methods
    neuro_df.loc[neuro_df['Method'] == 'Ephys', 'Method'] = 'Electrophysiology'
    neuro_df.loc[neuro_df['Method'] == 'Imaging', 'Method'] = 'Fluorescence imaging'

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        neuro_df, x='Year', y='Neurons', hue='Method',
        palette=[TEAL, GOLD], s=60, alpha=0.8, ax=ax
    )

    # Regression lines
    ax.plot(x_lin, y_lin_ephys, color=COLORS['text'], ls=(0, (5, 7)), lw=2)
    ax.plot(x_lin, y_lin_imag, color=COLORS['text'], ls=(0, (5, 7)), lw=2)
    ax.plot(x_lin, y_lin_ephys, color=TEAL, ls=(6, (5, 7)), lw=2)
    ax.plot(x_lin, y_lin_imag, color=GOLD, ls=(6, (5, 7)), lw=2)

    ax.set_yscale('log')
    plot_species_hlines(ax, min_year, max_year, 1958)
    ax.set_ylabel('Simultaneously Recorded Neurons')
    ax.set_xlabel(None)
    ax.set_ylim(0.2, 1e12)
    ax.set_title('Neural Recording Capacity Over Time')
    ax.legend(frameon=True)
    plt.tight_layout()
    save_figure(fig, 'neuro-recordings')
    plt.close()

# =============================================================================
# Figure 6: Brain Scans
# =============================================================================
@figure("scanned-brain-tissue", "Brain scan resolution, volume, and dataset size")
def generate_scanned_brain_tissue():
    scans_df = pd.read_csv(
        DATA_FILES["brain_scans"],
        parse_dates=['Year'],
    )

    min_date = dt.date(year=1975, month=1, day=1)
    max_date = dt.date(year=2025, month=1, day=1)

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    palette = CATEGORICAL_COLORS

    for i, (y_col, title) in enumerate([
        ('Resolution (claude)', 'Resolution (nm)'),
        ('Volume (claude)', 'Volume Imaged (μm³)'),
        ('Dataset Size (Claude)', 'Dataset Size (TB)'),
    ]):
        sns.scatterplot(
            data=scans_df, x='Year', y=y_col,
            hue='Method (claude)', style='Organism (cleaned)',
            palette=palette, s=60, alpha=0.8, ax=axes[i],
            legend=(i == 2),
        )
        axes[i].set_yscale('log')
        axes[i].set_title(title)
        axes[i].set_xlim(min_date, max_date)
        axes[i].set_xlabel(None)
        axes[i].set_ylabel(None)
        axes[i].tick_params(axis='x', rotation=-30)

    sns.move_legend(axes[2], "upper left", bbox_to_anchor=(1, 1), frameon=True)
    plt.tight_layout()
    save_figure(fig, 'scanned-brain-tissue')
    plt.close()

# =============================================================================
# Figure 7: Recording Modalities Comparison
# =============================================================================
@figure("recording-modalities", "Brain tissue recording modalities comparison")
def generate_recording_modalities():
    categories = ["Resolution", "Speed", "Duration", "Volume"]
    x = np.arange(len(categories))

    methods = {
        "fUS": {"values": [3, 3, 4, 3], "color": GOLD, "ls": "-", "marker": "o"},
        "Calcium Imaging": {"values": [4, 2, 2, 2], "color": TEAL, "ls": "-", "marker": "o"},
        "Voltage Imaging": {"values": [4, 3.25, 1.5, 1.75], "color": PURPLE, "ls": "-", "marker": "o"},
        "MEA": {"values": [4, 4, 4, 1.5], "color": CATEGORICAL_COLORS[3], "ls": "-", "marker": "o"},
        "EEG": {"values": [1, 4, 3, 3.5], "color": CATEGORICAL_COLORS[4], "ls": "--", "marker": "o"},
        "fMRI": {"values": [2, 1, 3, 4], "color": PRIMARY_COLORS[0], "ls": "--", "marker": "s"},
    }

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(-0.2, len(categories) - 1 + 0.2)
    ax.set_ylim(0.8, 4.2)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=12, fontweight="500")
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    for xi in x:
        ax.vlines(xi, 1, 4, colors=COLORS['grid'], linewidth=1, zorder=0)
    for y in [1, 2, 3, 4]:
        ax.hlines(y, x[0], x[-1], colors=COLORS['grid'], linewidth=1, linestyles="--", zorder=0)

    axis_labels = {
        "Resolution": ["Millions", "10s of thousands", "Thousands", "Single Cell"],
        "Speed": ["1 Hz", "10 Hz", "100 Hz", "1000 Hz"],
        "Duration": ["Seconds", "Minutes", "Hours", "Days"],
        "Volume": ["1 µm³", "1 mm³", "1 cm³", "1 dm³"],
    }

    for i, cat in enumerate(categories):
        for y, label in zip([1, 2, 3, 4], axis_labels[cat]):
            ha = "left" if cat == "Volume" else "right"
            x_offset = 0.03 if cat == "Volume" else -0.03
            ax.text(i + x_offset, y, label, ha=ha, va="center", fontsize=9, color=COLORS['text'])

    for name, props in methods.items():
        ax.plot(x, props["values"], linestyle=props["ls"], marker=props["marker"],
                linewidth=2.5, markersize=6, color=props["color"],
                markeredgecolor='white', markeredgewidth=1.5, label=name)

    ax.set_title("Brain Tissue Recording Modalities Comparison", fontsize=14, pad=20)
    ax.legend(title="Method", loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=True)
    plt.tight_layout()
    save_figure(fig, 'recording-modalities')
    plt.close()

# =============================================================================
# Figure 8: Emulation Requirements
# =============================================================================
@figure("emulation-requirements", "Emulation compute and storage requirements")
def generate_emulation_requirements():
    categories_organisms = ['C. elegans', 'Fly', 'Mouse', 'Human']
    categories_full = categories_organisms + ['H100', 'xAI Colossus']
    x_pos_full = np.arange(len(categories_full))
    x_pos_org = np.arange(len(categories_organisms))

    # Time-based compute
    compute_mids = np.array([1.87e9, 3.76e12, 8.88e15, 1.12e19])
    compute_errs = np.array([8.25e8, 1.05e12, 2.13e15, 2.7e18])
    ref_compute = [np.nan, np.nan, np.nan, np.nan, 1E+15, 1E+20]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x_pos_org, compute_mids, yerr=compute_errs, alpha=0.85, color=GOLD,
           ecolor=COLORS['text'], capsize=5, label='Organisms', edgecolor='white')
    ax.bar(x_pos_full, ref_compute, alpha=0.7, color=COLORS['caption'],
           label='Reference', edgecolor='white')
    ax.set_yscale('log')
    ax.set_xticks(x_pos_full)
    ax.set_xticklabels(categories_full, rotation=30, ha='right')
    ax.set_ylabel('Compute (FLOP/s)')
    ax.set_title('Emulation Compute Requirements (Time-Based)')
    ax.legend(frameon=True)
    ax.set_ylim(1e8, 1e21)
    plt.tight_layout()
    save_figure(fig, 'emulation-compute-time-based')
    plt.close()

    # Storage
    storage_mids = np.array([2.6e5, 6.54e8, 1.63e12, 2.05e15])
    storage_errs = np.array([9.4e4, 2.21e8, 5.45e11, 6.85e14])
    ref_storage = [np.nan, np.nan, np.nan, np.nan, 8E+10, 1E+16]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x_pos_org, storage_mids, yerr=storage_errs, alpha=0.85, color=TEAL,
           ecolor=COLORS['text'], capsize=5, label='Organisms', edgecolor='white')
    ax.bar(x_pos_full, ref_storage, alpha=0.7, color=COLORS['caption'],
           label='Reference', edgecolor='white')
    ax.set_yscale('log')
    ax.set_xticks(x_pos_full)
    ax.set_xticklabels(categories_full, rotation=30, ha='right')
    ax.set_ylabel('Storage (Bytes)')
    ax.set_title('Emulation Storage Requirements')
    ax.legend(frameon=True)
    ax.set_ylim(1e5, 1e17)
    plt.tight_layout()
    save_figure(fig, 'emulation-storage-requirements')
    plt.close()

    # Event-driven compute
    event_mids = np.array([5.27e8, 2.61e11, 1.69e14, 6.04e16])
    event_errs = np.array([5.23e8, 2.5e11, 1.42e14, 2.64e16])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x_pos_org, event_mids, yerr=event_errs, alpha=0.85, color=PURPLE,
           ecolor=COLORS['text'], capsize=5, label='Organisms', edgecolor='white')
    ax.bar(x_pos_full, ref_compute, alpha=0.7, color=COLORS['caption'],
           label='Reference', edgecolor='white')
    ax.set_yscale('log')
    ax.set_xticks(x_pos_full)
    ax.set_xticklabels(categories_full, rotation=30, ha='right')
    ax.set_ylabel('Compute (FLOP/s)')
    ax.set_title('Emulation Compute Requirements (Event-Driven)')
    ax.legend(frameon=True)
    ax.set_ylim(1e6, 1e21)
    plt.tight_layout()
    save_figure(fig, 'emulation-compute-event-driven')
    plt.close()

# =============================================================================
# Figure 9: Cost per Neuron (two versions: with and without illustrations)
# =============================================================================
@figure("cost-per-neuron", "Cost per neuron over time")
def generate_cost_per_neuron():
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter
    import textwrap

    df = pd.read_csv(DATA_FILES["cost_estimates"])
    df['CostPerNeuron'] = df['Cost / Neuron'].replace('[\\$,]', '', regex=True).astype(float)

    # Define style by Type (Budget, Estimate, Illustration)
    type_styles = {
        'Budget': {'color': GOLD, 'marker': 'o', 'edgecolor': COLORS['text']},
        'Estimate': {'color': TEAL, 'marker': 's', 'edgecolor': COLORS['text']},
        'Illustration': {'color': '#2ECC71', 'marker': 'D', 'edgecolor': COLORS['text']},
    }

    def dollar_formatter(x, pos):
        if x >= 1000:
            return f'${x:,.0f}'
        elif x >= 1:
            return f'${x:.0f}'
        elif x >= 0.1:
            return f'${x:.1f}'
        else:
            return f'${x:.2f}'

    def create_cost_per_neuron_figure(data, filename, include_illustration=True):
        """Create cost per neuron figure with automatically positioned labels using adjustText."""
        from adjustText import adjust_text

        fig, ax = plt.subplots(figsize=(14, 8))

        # Collect points and texts for adjustText
        texts = []
        x_points = []
        y_points = []

        # Plot each point
        for idx, row in data.iterrows():
            type_cat = row['Type'] if pd.notna(row.get('Type')) else 'Budget'
            style = type_styles.get(type_cat, type_styles['Budget'])

            ax.scatter(
                row['Year'], row['CostPerNeuron'],
                s=120,
                c=style['color'],
                marker=style['marker'],
                edgecolor=style['edgecolor'],
                linewidth=1.5,
                zorder=3
            )

            x_points.append(row['Year'])
            y_points.append(row['CostPerNeuron'])

            # Create label text
            organism = row['Organism'].strip().replace('\n', ' ')
            if 'White et al' in organism:
                label = 'C. elegans (White et al 1986)'
            elif 'Fruitfly' in organism or 'Murthy' in organism:
                label = 'Fruitfly Zheng et al, 2018\n(Murthy, Seung, et al., 2024)'
            elif 'Zebrafish' in organism:
                label = 'Zebrafish (Svara et al., 2022)'
            elif 'BRAIN CONNECTS' in organism or 'NIH' in organism:
                label = 'Mouse (NIH, 2024)'
            elif 'Wellcome' in organism:
                label = 'Wellcome EM (10nm isotropic)\nwith proof-reading'
            elif '15nm isotropic with current' in organism:
                label = '15nm isotropic with current\nproofreading (EM)'
            elif '1000x less proofreading: EM 10nm' in organism:
                label = '1000x less proofreading:\nEM 10nm isotropic'
            elif '1000x less proofreading: EM 15nm' in organism:
                label = '1000x less proofreading:\nEM 15nm isotropic'
            elif '1000x less proofreading: ExM' in organism:
                label = '1000x less proofreading:\nExM 15nm isotropic'
            else:
                label = textwrap.fill(organism, 25)

            # Add text at the point location (adjustText will move it)
            texts.append(ax.text(row['Year'], row['CostPerNeuron'], label,
                                fontsize=9, color=COLORS['text']))

        # Reference lines with labels ABOVE the lines
        ax.axhline(10, linestyle='--', color=GOLD, lw=2, alpha=0.8)
        ax.text(1982, 13, 'Mouse connectome for $1B', ha='left', va='bottom',
                fontsize=10, fontweight='bold', color=COLORS['text'])

        ax.axhline(0.1, linestyle='--', color=GOLD, lw=2, alpha=0.8)
        ax.text(1982, 0.13, 'Human connectome for $10B', ha='left', va='bottom',
                fontsize=10, fontweight='bold', color=COLORS['text'])

        ax.axhline(0.01, linestyle='--', color=GOLD, lw=2, alpha=0.8)
        ax.text(1982, 0.013, 'Human connectome for $1B', ha='left', va='bottom',
                fontsize=10, fontweight='bold', color=COLORS['text'])

        ax.set_yscale('log')
        ax.set_xlim(1980, 2050)
        ax.set_ylim(0.005, 50000)

        # Use adjustText to automatically position labels without overlap
        adjust_text(texts, x=x_points, y=y_points, ax=ax,
                    arrowprops=dict(arrowstyle='-', color='gray', lw=0.5),
                    expand_points=(1.5, 1.5),
                    force_text=(0.5, 1.0),
                    force_points=(0.5, 0.5),
                    only_move={'points': 'y', 'text': 'xy'})

        ax.set_xlabel('Year')
        ax.set_ylabel('Cost per neuron (USD)')
        ax.set_title('Cost per neuron over time')

        ax.yaxis.set_major_formatter(FuncFormatter(dollar_formatter))

        # Create legend - position in upper right to avoid overlap with data
        if include_illustration:
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor=GOLD,
                       markeredgecolor=COLORS['text'], markersize=10, label='Budget'),
                Line2D([0], [0], marker='s', color='w', markerfacecolor=TEAL,
                       markeredgecolor=COLORS['text'], markersize=10, label='Estimate'),
                Line2D([0], [0], marker='D', color='w', markerfacecolor='#2ECC71',
                       markeredgecolor=COLORS['text'], markersize=10, label='Illustration'),
            ]
        else:
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor=GOLD,
                       markeredgecolor=COLORS['text'], markersize=10, label='Budget'),
                Line2D([0], [0], marker='s', color='w', markerfacecolor=TEAL,
                       markeredgecolor=COLORS['text'], markersize=10, label='Estimate'),
            ]

        ax.legend(handles=legend_elements, title='Type', loc='upper right',
                  frameon=True, fancybox=True, shadow=False)

        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        save_figure(fig, filename)
        plt.close()

    # Version 1: All data (Budget, Estimate, Illustration)
    create_cost_per_neuron_figure(df, 'cost-per-neuron', include_illustration=True)

    # Version 2: Only Budget and Estimate (no Illustration)
    df_no_illust = df[df['Type'] != 'Illustration'].copy()
    create_cost_per_neuron_figure(df_no_illust, 'cost-per-neuron-no-illust', include_illustration=False)

# =============================================================================
# Figure 10: Initiatives
# =============================================================================
@figure("initiatives", "Megaproject budgets and distributions")
def generate_initiatives():
    from matplotlib.patches import Patch

    brain_proj_df = pd.read_csv(
        DATA_FILES["initiatives_overview"],
        parse_dates=['Start Year (cleaned)', 'End Year (cleaned)']
    )
    brain_proj_df.dropna(subset=['Start Year (cleaned)', 'Budget (in million $) (cleaned)'], inplace=True)
    brain_proj_df['Category'] = 'Brain'
    brain_proj_df['End Year (cleaned)'] = brain_proj_df['End Year (cleaned)'].fillna(dt.datetime(2024, 12, 31))

    other_proj_df = pd.read_csv(
        DATA_FILES["initiatives_costs"],
        parse_dates=['StartYear', 'EndYear'],
        converters={'Adjusted2024_M': lambda s: 1e3 * float(s.replace('$', ''))}
    )

    all_proj_df = pd.concat([
        other_proj_df[['Name', 'Adjusted2024_M', 'Category', 'StartYear', 'EndYear']].rename(
            columns={'Adjusted2024_M': 'Budget_M'}),
        brain_proj_df[['Project name', 'Category', 'Budget (in million $) (cleaned)',
                       'Start Year (cleaned)', 'End Year (cleaned)']].rename(
            columns={'Project name': 'Name', 'Budget (in million $) (cleaned)': 'Budget_M',
                     'Start Year (cleaned)': 'StartYear', 'End Year (cleaned)': 'EndYear'}),
    ], ignore_index=True)

    # Scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(all_proj_df, x='StartYear', y='Budget_M', hue='Category',
                    palette=CATEGORICAL_COLORS + PRIMARY_COLORS[:4], s=80, alpha=0.8, ax=ax)
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1), frameon=True)
    ax.set_yscale('log')
    ax.set_ylabel('Budget (Million $)')
    ax.set_xlabel(None)
    ax.set_title('Megaproject Budgets by Start Year')
    plt.tight_layout()
    save_figure(fig, 'initiatives1')
    plt.close()

    # Compute project durations and midpoints for initiatives2, 4, 5
    proj_durations = all_proj_df['EndYear'] - all_proj_df['StartYear']
    proj_midpoints = all_proj_df['StartYear'] + proj_durations / 2

    proj_categories = all_proj_df['Category'].unique()
    all_colors = CATEGORICAL_COLORS + PRIMARY_COLORS
    category_colors = [all_colors[i % len(all_colors)] for i in range(len(proj_categories))]
    category_colormap = dict(zip(proj_categories, category_colors))
    proj_colors = [category_colormap[cat] for cat in all_proj_df['Category']]

    # initiatives2 - Megaproject Budgets and Durations
    fig, ax = plt.subplots(figsize=(10, 5))
    for i in range(len(all_proj_df)):
        ax.errorbar(
            [proj_midpoints[i]],
            [1e6 * all_proj_df.loc[i, 'Budget_M']],
            ls='none',
            xerr=[proj_durations[i] / 2],
            capsize=4,
            ecolor=proj_colors[i],
            alpha=0.8,
        )
    ax.set_yscale('log')
    ax.set_xlim(dt.datetime(year=1940, month=1, day=1), dt.datetime(year=2035, month=1, day=1))
    ax.set_ylabel('Budget ($)')
    ax.set_xlabel(None)
    legend_handles = [
        Patch(facecolor=color, edgecolor=COLORS['border'], label=category)
        for category, color in zip(proj_categories, category_colors)
    ]
    for i, proj in all_proj_df.head(6).iterrows():
        ax.text(proj_midpoints[i], 1e6 * proj['Budget_M'], proj['Name'],
                ha='center', va='bottom', fontsize=9, color=COLORS['text'])
    ax.legend(handles=legend_handles, title="Category", loc='upper left', bbox_to_anchor=(1, 1), frameon=True)
    ax.set_title('Megaproject Budgets and Durations')
    plt.tight_layout()
    save_figure(fig, 'initiatives2')
    plt.close()

    # initiatives3 - KDE plot
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.kdeplot(all_proj_df, x='Budget_M', label='All projects', fill=True, log_scale=True,
                color=COLORS['grid'], alpha=0.5, ax=ax)
    sns.kdeplot(all_proj_df.query('Category == "Brain"'), x='Budget_M', label='Brain projects',
                fill=True, log_scale=True, color=GOLD, alpha=0.7, ax=ax)
    ax.set_title('Brain Project Budgets vs All Megaprojects')
    ax.set_xlabel('Budget (Million $)')
    ax.legend(frameon=True)
    plt.tight_layout()
    save_figure(fig, 'initiatives3')
    plt.close()

    # initiatives4 - Budgets with KDE overlay
    fig, ax = plt.subplots(figsize=(10, 5))
    for i in range(len(all_proj_df)):
        ax.errorbar(
            [proj_midpoints[i]],
            [all_proj_df.loc[i, 'Budget_M']],
            ls='none',
            xerr=[proj_durations[i] / 2],
            capsize=4,
            ecolor=proj_colors[i],
            alpha=0.8,
        )
    ax.set_yscale('log')
    ax.set_xlim(dt.datetime(year=1940, month=1, day=1), dt.datetime(year=2035, month=1, day=1))
    ax.set_ylabel('Budget (Million $)')
    for i, proj in all_proj_df.head(6).iterrows():
        ax.text(proj_midpoints[i], proj['Budget_M'], proj['Name'],
                ha='center', va='bottom', fontsize=9, color=COLORS['text'])
    ax.legend(handles=legend_handles, title="Category", loc='upper left', bbox_to_anchor=(1, 1), frameon=True)
    ax.set_title('Megaproject Budgets')
    ax2 = ax.twiny()
    ax2.set_xticks([])
    ax2.set_xlim(0, 1.5)
    sns.kdeplot(all_proj_df.query('Category == "Brain"'), y='Budget_M', label='Brain', color=GOLD, fill=True, log_scale=True, ax=ax2, alpha=0.5)
    sns.kdeplot(all_proj_df.query('Category != "Brain"'), y='Budget_M', label='Other', color=COLORS['caption'], fill=True, log_scale=True, ax=ax2, alpha=0.3)
    ax2.legend(loc=(0.3, 0.3), title='Distributions', frameon=True)
    ax.set_ylim(1e0, 5e6)
    plt.tight_layout()
    save_figure(fig, 'initiatives4')
    plt.close()

    # initiatives5 - Budget Distributions by Category Over Time
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.kdeplot(
        all_proj_df,
        x='StartYear',
        y='Budget_M',
        hue='Category',
        palette=category_colormap,
        log_scale=(False, True),
        fill=True,
        alpha=0.4,
        warn_singular=False,
        ax=ax
    )
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1), frameon=True)
    ax.set_ylim(1e0, 5e6)
    ax.set_xlim(dt.datetime(year=1950, month=1, day=1), dt.datetime(year=2035, month=1, day=1))
    ax.set_ylabel('Budget (Million $)')
    ax.set_xlabel(None)
    ax.set_title('Budget Distributions by Category Over Time')
    plt.tight_layout()
    save_figure(fig, 'initiatives5')
    plt.close()

    # initiatives6 - Budget Distributions by Category
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.kdeplot(all_proj_df, x='Budget_M', label='All projects', log_scale=True, fill=True, color=COLORS['grid'], alpha=0.5, ax=ax)
    for i, category in enumerate(proj_categories):
        color = category_colors[i]
        sns.kdeplot(all_proj_df.query(f'Category == "{category}"'), x='Budget_M', label=category, fill=False, log_scale=True, color=color, ax=ax)
    ax.set_title('Budget Distributions by Category')
    ax.set_xlabel('Budget (Million $)')
    ax.legend(frameon=True, loc='upper right')
    plt.tight_layout()
    save_figure(fig, 'initiatives6')
    plt.close()

# =============================================================================
# Figure 11: Simulation Heatmap
# =============================================================================
@figure("sim-heatmap", "Computational models characteristics heatmap")
def generate_sim_heatmap():
    import textwrap
    from matplotlib.colors import ListedColormap, BoundaryNorm

    # Load simulation data
    neuro_sim_df = pd.read_csv(DATA_FILES["computational_models"])

    # Define organisms and data columns
    organisms = ['C. elegans', 'Drosophila', 'Zebrafish', 'Mouse', 'Human']
    # Map organism names
    organism_map = {
        'Mammalian': 'Mouse',
        'Silicon': None,  # Skip
    }
    neuro_sim_df = neuro_sim_df.copy()
    neuro_sim_df['Organism_mapped'] = neuro_sim_df['Organism'].replace(organism_map)
    neuro_sim_df = neuro_sim_df[neuro_sim_df['Organism_mapped'].isin(organisms)].copy()

    data_columns = [
        'Connectivity accuracy',
        'Percentage of neurons',
        'Neurontypes',
        'Plasticity',
        'Functional Accuracy',
        'Neuromodulation',
        'Temporal resolution',
        'Behavior',
        'Personality-defining Characteristics',
        'Learning',
    ]

    # Convert to numeric
    for col in data_columns:
        neuro_sim_df.loc[:, col] = pd.to_numeric(neuro_sim_df[col], errors='coerce')

    # Filter to rows that have at least half of the data columns filled
    min_valid_columns = len(data_columns) // 2
    valid_mask = neuro_sim_df[data_columns].notna().sum(axis=1) >= min_valid_columns
    neuro_sim_df = neuro_sim_df[valid_mask].copy()

    # Also require First Author and Year to be present
    neuro_sim_df = neuro_sim_df.dropna(subset=['First Author', 'Year']).copy()

    # Sort by organism to cluster entries
    organism_order = ['C. elegans', 'Drosophila', 'Zebrafish', 'Mouse', 'Human']
    neuro_sim_df['Organism_order'] = neuro_sim_df['Organism_mapped'].apply(
        lambda x: organism_order.index(x) if x in organism_order else 999
    )
    neuro_sim_df = neuro_sim_df.sort_values(['Organism_order', 'Year']).copy()
    neuro_sim_df = neuro_sim_df.reset_index(drop=True)

    logger.info(f"  Found {len(neuro_sim_df)} valid entries for heatmap")

    if len(neuro_sim_df) > 0:
        # Get the raw data with NaN preserved
        heatmap_data = neuro_sim_df[data_columns].astype(float)

        # Create figure with subplots: organism labels | heatmap
        fig_height = max(10, len(neuro_sim_df) * 0.4)
        fig = plt.figure(figsize=(16, fig_height))

        # Create grid: organism bar (narrow) | heatmap (wide)
        gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 10], wspace=0.02)
        org_ax = fig.add_subplot(gs[0])
        sim_ax = fig.add_subplot(gs[1])

        # Create a custom colormap with gray for NaN/unknown values
        # Use -1 as a placeholder for NaN, then create boundaries
        heatmap_filled = heatmap_data.fillna(-1)

        # Custom colormap: gray for -1, then Blues gradient for 0-3
        colors_list = ['#E0E0E0'] + list(plt.cm.Blues(np.linspace(0.2, 1.0, 4)))
        cmap = ListedColormap(colors_list)
        bounds = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
        norm = BoundaryNorm(bounds, cmap.N)

        heatmap = sns.heatmap(
            heatmap_filled,
            ax=sim_ax,
            cbar=True,
            cmap=cmap,
            norm=norm,
            cbar_kws=dict(
                orientation="vertical",
                location="right",
                shrink=0.4,
                aspect=15,
                pad=0.15,
            ),
            linewidths=0.5,
            linecolor='white',
        )

        # Configure colorbar
        cbar = heatmap.collections[0].colorbar
        cbar.set_ticks([-1, 0, 1, 2, 3])
        cbar.set_ticklabels(['Unknown', '0', '1', '2', '3'])
        cbar.ax.tick_params(labelsize=9)

        sim_ax.set_xticks(
            np.arange(len(data_columns)) + 0.5,
            [textwrap.fill(col, width=15) for col in data_columns],
            rotation=45,
            ha='right',
            fontsize=9,
        )

        # Add author labels on right side of heatmap
        sim_ax.set_yticks(
            np.arange(len(neuro_sim_df)) + 0.5,
            labels=[
                f'{row["First Author"]} ({int(row["Year"])})'
                for _, row in neuro_sim_df.iterrows()
            ],
            rotation=0,
            fontsize=9,
        )
        sim_ax.yaxis.tick_right()

        # Create organism grouping brackets on the left axis
        org_ax.set_xlim(0, 1)
        org_ax.set_ylim(len(neuro_sim_df), 0)  # Inverted to match heatmap
        org_ax.axis('off')

        # Find organism group boundaries
        organism_groups = []
        current_organism = None
        group_start = 0
        for i, (_, row) in enumerate(neuro_sim_df.iterrows()):
            org = row['Organism_mapped']
            if org != current_organism:
                if current_organism is not None:
                    organism_groups.append((current_organism, group_start, i))
                current_organism = org
                group_start = i
        # Add last group
        if current_organism is not None:
            organism_groups.append((current_organism, group_start, len(neuro_sim_df)))

        # Draw organism brackets and labels (simple lines, no colors)
        for idx, (org_name, start, end) in enumerate(organism_groups):
            # Draw bracket: top line, vertical line, bottom line
            bracket_x = 0.85
            # Top horizontal line
            org_ax.plot([bracket_x, 1.0], [start, start], color=COLORS['text'], linewidth=1.5)
            # Bottom horizontal line
            org_ax.plot([bracket_x, 1.0], [end, end], color=COLORS['text'], linewidth=1.5)
            # Vertical line connecting them
            org_ax.plot([bracket_x, bracket_x], [start, end], color=COLORS['text'], linewidth=1.5)
            # Add organism label centered on the bracket
            mid_y = (start + end) / 2
            org_ax.text(0.4, mid_y, org_name, ha='center', va='center',
                       fontsize=10, fontweight='bold', rotation=90, color=COLORS['text'])

        sim_ax.tick_params(axis='both', which='both', length=0)
        for direction in ['bottom', 'right', 'top', 'left']:
            sim_ax.spines[direction].set_visible(True)
            sim_ax.spines[direction].set_color(COLORS['border'])

        sim_ax.set_title('Computational Models of the Brain - Characteristics', fontsize=12, pad=10)

        plt.tight_layout()
        save_figure(fig, 'sim-heatmap')
        plt.close()
    else:
        logger.info("  Skipped - no valid data")

# =============================================================================
# Figure 12: Recording Heatmap
# =============================================================================
@figure("rec-heatmap", "Neural dynamics recording data coverage heatmap")
def generate_rec_heatmap():
    import textwrap
    from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

    # Load recording data
    neuro_rec_df = pd.read_csv(DATA_FILES["neural_dynamics"])

    # Rename columns to match expected format
    neuro_rec_df = neuro_rec_df.copy()
    neuro_rec_df = neuro_rec_df.rename(columns={
        'First author': 'First Author',
        'Temporal resolution: Hz': 'Temporal resolution',
        'Duration single session min per Individual': 'Duration',
        'Resolution in µm isotropic': 'Resolution',
        'Number of neurons': 'Neurons',
    })

    rec_data_columns = [
        'Temporal resolution',
        'Duration',
        'Resolution',
        'Neurons',
    ]

    # Convert to numeric
    for col in rec_data_columns:
        if col in neuro_rec_df.columns:
            neuro_rec_df.loc[:, col] = pd.to_numeric(neuro_rec_df[col], errors='coerce')

    # Filter to rows that have at least 1 data column filled (relaxed from requiring all)
    valid_mask = neuro_rec_df[rec_data_columns].notna().sum(axis=1) >= 1
    neuro_rec_df = neuro_rec_df[valid_mask].copy()

    # Also require First Author and Year
    neuro_rec_df = neuro_rec_df.dropna(subset=['First Author', 'Year']).copy()

    # Sort by organism to cluster entries
    organism_order = ['C. elegans', 'Drosophila', 'Zebrafish', 'Mouse', 'Human']
    neuro_rec_df['Organism_order'] = neuro_rec_df['Organism'].apply(
        lambda x: organism_order.index(x) if x in organism_order else 999
    )
    neuro_rec_df = neuro_rec_df.sort_values(['Organism_order', 'Year']).copy()
    neuro_rec_df = neuro_rec_df.reset_index(drop=True)

    logger.info(f"  Found {len(neuro_rec_df)} valid entries for recording heatmap")

    if len(neuro_rec_df) > 0:
        # Log-scale the data for visualization, keeping NaN as NaN
        rec_df_log = neuro_rec_df[rec_data_columns].apply(lambda x: np.log10(x.replace(0, np.nan)))

        # Get min/max for color scaling (excluding NaN)
        all_values = rec_df_log.values.flatten()
        valid_values = all_values[~np.isnan(all_values)]
        vmin, vmax = valid_values.min(), valid_values.max()

        # Use a special value for NaN that's below vmin
        nan_placeholder = vmin - 1
        rec_df_filled = rec_df_log.fillna(nan_placeholder)

        # Create figure with subplots: organism labels | heatmap
        fig_height = max(8, len(neuro_rec_df) * 0.35)
        fig = plt.figure(figsize=(14, fig_height))

        # Create grid: organism bar (narrow) | heatmap (wide)
        gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 10], wspace=0.02)
        org_ax = fig.add_subplot(gs[0])
        rec_ax = fig.add_subplot(gs[1])

        # Create custom colormap with gray for unknown
        # OrRd colormap for data, gray at the bottom for unknown
        orrd_colors = plt.cm.OrRd(np.linspace(0.2, 1.0, 256))
        gray_color = np.array([[0.88, 0.88, 0.88, 1.0]])  # Light gray
        combined_colors = np.vstack([gray_color, orrd_colors])
        cmap = LinearSegmentedColormap.from_list('OrRd_with_gray', combined_colors, N=257)

        # Set vmin to include the nan_placeholder
        heatmap = sns.heatmap(
            rec_df_filled,
            ax=rec_ax,
            cbar=True,
            cmap=cmap,
            vmin=nan_placeholder,
            vmax=vmax,
            cbar_kws=dict(
                orientation="vertical",
                location="right",
                shrink=0.4,
                aspect=15,
                pad=0.25,
            ),
            linewidths=0.5,
            linecolor='white',
        )

        # Configure colorbar
        cbar = heatmap.collections[0].colorbar
        # Add "Unknown" label at the bottom
        cbar_ticks = [nan_placeholder, vmin, (vmin+vmax)/2, vmax]
        cbar_labels = ['Unknown', f'{vmin:.1f}', f'{(vmin+vmax)/2:.1f}', f'{vmax:.1f}']
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels(cbar_labels)
        cbar.ax.tick_params(labelsize=9)
        cbar.set_label('log10 scale', fontsize=10)

        rec_ax.set_xticks(
            np.arange(len(rec_data_columns)) + 0.5,
            [textwrap.fill(col, width=12) for col in rec_data_columns],
            fontsize=10,
        )

        # Add author labels on right side of heatmap
        rec_ax.set_yticks(
            np.arange(len(neuro_rec_df)) + 0.5,
            labels=[
                f'{row["First Author"]} ({int(row["Year"])})'
                for _, row in neuro_rec_df.iterrows()
            ],
            rotation=0,
            fontsize=9,
        )
        rec_ax.yaxis.tick_right()

        # Create organism grouping brackets on the left axis
        org_ax.set_xlim(0, 1)
        org_ax.set_ylim(len(neuro_rec_df), 0)  # Inverted to match heatmap
        org_ax.axis('off')

        # Find organism group boundaries
        organism_groups = []
        current_organism = None
        group_start = 0
        for i, (_, row) in enumerate(neuro_rec_df.iterrows()):
            org = row['Organism']
            if org != current_organism:
                if current_organism is not None:
                    organism_groups.append((current_organism, group_start, i))
                current_organism = org
                group_start = i
        # Add last group
        if current_organism is not None:
            organism_groups.append((current_organism, group_start, len(neuro_rec_df)))

        # Draw organism brackets and labels (simple lines, no colors)
        for idx, (org_name, start, end) in enumerate(organism_groups):
            # Draw bracket: top line, vertical line, bottom line
            bracket_x = 0.85
            # Top horizontal line
            org_ax.plot([bracket_x, 1.0], [start, start], color=COLORS['text'], linewidth=1.5)
            # Bottom horizontal line
            org_ax.plot([bracket_x, 1.0], [end, end], color=COLORS['text'], linewidth=1.5)
            # Vertical line connecting them
            org_ax.plot([bracket_x, bracket_x], [start, end], color=COLORS['text'], linewidth=1.5)
            # Add organism label centered on the bracket
            mid_y = (start + end) / 2
            org_ax.text(0.4, mid_y, org_name, ha='center', va='center',
                       fontsize=10, fontweight='bold', rotation=90, color=COLORS['text'])

        rec_ax.tick_params(axis='both', which='both', length=0)
        for direction in ['bottom', 'right', 'top', 'left']:
            rec_ax.spines[direction].set_visible(True)
            rec_ax.spines[direction].set_color(COLORS['border'])

        rec_ax.set_title('Neural Dynamics Recording - Data Coverage', fontsize=12, pad=10)

        plt.tight_layout()
        save_figure(fig, 'rec-heatmap')
        plt.close()
    else:
        logger.info("  Skipped - no valid data")

# =============================================================================
# Figure 13: Neuro-sim radar charts (individual organisms) - WITH TICKS AND INFO BOXES
# =============================================================================
@figure("neuro-sim", "Simulation characteristics radar charts per organism")
def generate_neuro_sim_radar():
    import textwrap

    # Create output directory if it doesn't exist
    OUTPUT_FIGURES_NEURO_SIM.mkdir(parents=True, exist_ok=True)

    # Load simulation data
    neuro_sim_df = pd.read_csv(DATA_FILES["computational_models"])

    organisms = ['C. elegans', 'Drosophila', 'Zebrafish', 'Mouse', 'Human']
    organism_map = {
        'Mammalian': 'Mouse',
        'Silicon': None,
    }
    neuro_sim_df['Organism_mapped'] = neuro_sim_df['Organism'].replace(organism_map)

    data_columns = [
        'Connectivity accuracy',
        'Percentage of neurons',
        'Neurontypes',
        'Plasticity',
        'Functional Accuracy',
        'Neuromodulation',
        'Temporal resolution',
        'Behavior',
        'Personality-defining Characteristics',
        'Learning',
    ]

    # Short labels for axes
    column_labels = [
        'Connectivity\nAccuracy',
        '% of\nNeurons',
        'Neuron\nTypes',
        'Plasticity',
        'Functional\nAccuracy',
        'Neuro-\nmodulation',
        'Temporal\nResolution',
        'Behavior',
        'Personality',
        'Learning',
    ]

    # Convert to numeric
    for col in data_columns:
        neuro_sim_df[col] = pd.to_numeric(neuro_sim_df[col], errors='coerce')

    for organism in organisms:
        organism_df = neuro_sim_df[neuro_sim_df['Organism_mapped'] == organism]
        organism_df = organism_df.dropna(subset=data_columns)

        if organism_df.empty:
            logger.info(f"  No data for {organism}, skipping.")
            continue

        N = len(data_columns)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
        width = 2 * np.pi / N

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

        # Set radial limits (0-3 scale for simulation data)
        ax.set_ylim(0, 3.5)

        # Draw concentric circles for tick marks
        tick_values = [0, 1, 2, 3]
        tick_labels = ['0', '1', '2', '3']
        for tick_val in tick_values:
            theta = np.linspace(0, 2*np.pi, 100)
            ax.plot(theta, [tick_val]*100, color=COLORS['grid'], lw=0.5, alpha=0.7)

        # Draw radial dividers
        for i in range(N):
            theta_div = 2*np.pi * (i-1/2) / N
            ax.plot([theta_div, theta_div], [0, 3.5], color=COLORS['grid'], lw=0.5, alpha=0.7)

        # Add tick labels in the middle (at angle 0)
        for tick_val, tick_label in zip(tick_values[1:], tick_labels[1:]):
            ax.text(0, tick_val, tick_label, ha='center', va='center',
                    fontsize=9, color=COLORS['caption'],
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.8))

        num_simulations = len(organism_df)
        base_alpha = 0.7
        normalized_alpha = 1 - (1 - base_alpha)**(1/max(num_simulations, 1))

        # Compute max values per column for info boxes
        max_values = organism_df[data_columns].max()

        for _, row in organism_df.iterrows():
            try:
                values = row[data_columns].astype(float).values
            except ValueError:
                continue

            ax.bar(
                x=angles,
                height=values,
                width=width,
                bottom=0.0,
                alpha=normalized_alpha,
                color=TEAL,
                edgecolor='none'
            )

        # Add axis labels
        ax.set_xticks(angles)
        ax.set_xticklabels(column_labels, fontsize=10, color=COLORS['text'])
        ax.tick_params(axis='x', pad=15)

        # Add info boxes at outside showing max values
        for i, (col, label) in enumerate(zip(data_columns, column_labels)):
            angle = angles[i]
            max_val = max_values[col]
            if pd.notna(max_val):
                # Position outside the chart
                r_pos = 3.8
                x_pos = r_pos * np.cos(np.pi/2 - angle)
                y_pos = r_pos * np.sin(np.pi/2 - angle)

                # Format the value
                if max_val >= 1:
                    val_str = f"{max_val:.1f}"
                else:
                    val_str = f"{max_val:.2f}"

                # Add info box
                ax.annotate(
                    f"Max: {val_str}",
                    xy=(angle, 3.2),
                    xytext=(angle, 4.0),
                    fontsize=8,
                    ha='center',
                    va='center',
                    color=COLORS['text'],
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['grid'], edgecolor=COLORS['border'], alpha=0.9),
                )

        ax.set_yticks([])
        ax.grid(False)
        ax.spines['polar'].set_visible(False)

        # Add title
        ax.set_title(f'{organism} - Simulation Characteristics', fontsize=14, pad=60, color=COLORS['title'])

        plt.tight_layout()
        add_attribution(fig)
        fig.savefig(OUTPUT_FIGURES_NEURO_SIM / f'{organism}.svg', format='svg', bbox_inches='tight', pad_inches=0.2)
        fig.savefig(OUTPUT_FIGURES_NEURO_SIM / f'{organism}.png', format='png', dpi=150, bbox_inches='tight', pad_inches=0.2)
        plt.close()

# =============================================================================
# Figure 14: Neuro-rec radar charts - PER ORGANISM with ticks and info boxes
# =============================================================================
@figure("neuro-rec", "Recording characteristics radar charts per organism")
def generate_neuro_rec_radar():
    import textwrap

    # Create output directory if it doesn't exist
    OUTPUT_FIGURES_NEURO_REC.mkdir(parents=True, exist_ok=True)

    # Load recording data from the original data files
    neuro_rec_df = pd.read_csv(DATA_FILES["neurodynamics_papers"])
    organism_neuro_df = pd.read_csv(DATA_FILES["neurodynamics_organisms"])

    # Standardize organism names in organism_neuro_df
    organism_neuro_df.replace('Zebrafish Larvae', 'Zebrafish', inplace=True)
    organism_neuro_df.replace('C. Elegans', 'C. elegans', inplace=True)
    organism_neuro_df.index = organism_neuro_df.loc[:, 'Organism']
    organism_neuro_df.drop(columns=['Organism'], inplace=True)

    # Standardize organism names in recording data
    neuro_rec_df['Organism'] = neuro_rec_df['Organism'].replace({
        'C. Elegans': 'C. elegans',
        'Zebrafish Larvae': 'Zebrafish',
    })

    organisms = ['C. elegans', 'Drosophila', 'Zebrafish', 'Mouse', 'Human']

    # Define the 5 data columns (matching the old code)
    neuro_rec_data_columns = [
        'Number of neurons',
        'Temporal resolution: Hz',
        'Duration single session min',
        'Duration total repeated sessions min',
        'Resolution in µm isotropic',
    ]

    neuro_rec_column_labels = [
        'Temporal\nresolution: Hz',
        'Number of\nneurons',
        'Resolution in\nµm isotropic',
        'Duration total\nrepeated\nsessions min',
        'Duration single\nsession min',
    ]

    # Properties for max value info boxes
    neuro_rec_max_props = {
        'Number of neurons': {
            'col': 'Total Neuron Count',
            'short': 'Total Neurons',
        },
        'Temporal resolution: Hz': {
            'col': 'Maximum Neuron Firing Rate (Hz)',
            'short': 'Max. Neuron\nFiring Rate',
            'units': 'Hz',
        },
        'Duration single session min': {
            'col': 'Average Liftime in Minutes',
            'short': 'Avg. Lifetime',
            'units': 'min',
        },
        'Duration total repeated sessions min': {
            'col': 'Average Liftime in Minutes',
            'short': 'Avg. Lifetime',
            'units': 'min',
        },
        'Resolution in µm isotropic': {
            'col': 'Isotropic resolution Single Neuron recording in µm',
            'short': 'Single Neuron\nResolution',
            'units': 'µm³',
        },
    }

    # Reverse these axes because lower is better
    neuro_rec_rev_axes = ['Resolution in µm isotropic']

    # Convert columns to numeric
    for col in neuro_rec_data_columns:
        if col in neuro_rec_df.columns:
            neuro_rec_df[col] = pd.to_numeric(neuro_rec_df[col], errors='coerce')

    # Filter out rows with missing data
    neuro_rec_df = neuro_rec_df.dropna(subset=neuro_rec_data_columns + ['Organism'], how='all')

    # Define order-of-magnitude transformation function
    def oom_transform(x, oom_range):
        min_oom, max_oom = oom_range
        if abs(max_oom - min_oom) != 5:
            raise ValueError("Must span 5 orders of magnitude")
        # Reverse axis direction if range is given backwards
        if min_oom < max_oom:
            return max(np.log10(x) - min_oom, 0)
        else:
            max_oom, min_oom = oom_range
            return max(max_oom - np.log10(x), 0)

    def get_ooms(oom_range):
        return np.linspace(*oom_range, num=6, endpoint=True).astype(int)[1:]

    def format_exp_float(x, bold=False):
        expnt = int(np.floor(np.log10(x)))
        base = x / 10**expnt
        inner = rf"{base:.1f} \times 10^{{{expnt}}}"
        if bold:
            return rf"$\mathbf{{{inner}}}$"
        else:
            return f"${inner}$"

    # Calculate organism-specific axis ranges
    neuro_rec_ax_max_oom = {}
    for organism in organisms:
        if organism not in organism_neuro_df.index:
            continue
        neuro_rec_ax_max_oom[organism] = {}
        for col in neuro_rec_data_columns:
            if col not in neuro_rec_max_props:
                continue
            try:
                max_val = organism_neuro_df.loc[organism, neuro_rec_max_props[col]['col']]
                if col in neuro_rec_rev_axes:
                    neuro_rec_ax_max_oom[organism][col] = np.ceil(np.log10(max_val))
                else:
                    neuro_rec_ax_max_oom[organism][col] = np.floor(np.log10(max_val))
            except:
                pass

    neuro_rec_ax_oom_ranges = {}
    for organism in organisms:
        if organism not in neuro_rec_ax_max_oom:
            continue
        neuro_rec_ax_oom_ranges[organism] = {}
        for col in neuro_rec_data_columns:
            if col not in neuro_rec_ax_max_oom[organism]:
                continue
            if col in neuro_rec_rev_axes:
                neuro_rec_ax_oom_ranges[organism][col] = [
                    neuro_rec_ax_max_oom[organism][col] + 5,
                    neuro_rec_ax_max_oom[organism][col],
                ]
            else:
                neuro_rec_ax_oom_ranges[organism][col] = [
                    neuro_rec_ax_max_oom[organism][col] - 5,
                    neuro_rec_ax_max_oom[organism][col],
                ]

    # Updated rec_fig function with new color scheme
    def rec_fig(ax, sub_df, organism, individual_studies=None):
        N = 5

        # Angles: equally spaced around the circle
        angles = np.linspace(0, 2 * np.pi, N+1)
        unique_angles = angles[:-1]

        # Each wedge gets the same width
        width = 2 * np.pi / N

        # Plot circle indicating maximum value
        theta = np.linspace(0, 2*np.pi, 100)
        ax.plot(
            theta,
            [5]*100,
            color=COLORS['border'],
            lw=2,
        )

        tick_offsets = [
            [3, 3],
            [-22, 8],
            [-25,-10],
            [-10,-20],
            [5,-10],
        ]

        # Add tick labels for each section
        for i, col_name in enumerate(neuro_rec_data_columns):
            theta_pos = 2*np.pi * i / N
            if organism not in neuro_rec_ax_oom_ranges or col_name not in neuro_rec_ax_oom_ranges[organism]:
                continue
            oom_range = neuro_rec_ax_oom_ranges[organism][col_name]
            ooms = get_ooms(oom_range)
            for j, expnt in enumerate(ooms):
                label = f'$10^{{{expnt}}}$'
                r = j + 1
                ax.annotate(
                    label,
                    (theta_pos, r),
                    xytext=tick_offsets[i],
                    textcoords='offset points',
                    color=COLORS['text']
                )

        # Draw radial axes
        for i, theta_ax in enumerate(unique_angles):
            col_name = neuro_rec_data_columns[i]
            if organism not in organism_neuro_df.index or col_name not in neuro_rec_max_props:
                continue
            try:
                max_val = organism_neuro_df.loc[
                    organism,
                    neuro_rec_max_props[col_name]['col']
                ]
            except:
                continue
            if organism not in neuro_rec_ax_oom_ranges or col_name not in neuro_rec_ax_oom_ranges[organism]:
                continue
            oom_range = neuro_rec_ax_oom_ranges[organism][col_name]
            oom_val = oom_transform(max_val, oom_range)
            ax.plot(
                [theta_ax, theta_ax],
                [0, oom_val],
                color=COLORS['text'],
                lw=1,
                clip_on=None,
                transform=ax.transData,
            )

            axis_label_offsets = [
                [30, 0],
                [-20,20],
                [-50,5],
                [-20,-35],
                [35,-15],
            ]

            # axis labels
            ax.annotate(
                neuro_rec_column_labels[i],
                (theta_ax+0.2, 5),
                xytext=axis_label_offsets[i],
                fontsize=12,
                textcoords='offset points',
                color=COLORS['text'],
                ha='center',
                va='center',
            )

            # Label max val (dot)
            ax.plot(
                [theta_ax],
                [oom_val],
                'o',
                color=TEAL,
                clip_on=None,
                mec=COLORS['text'],
                transform=ax.transData,
            )

            max_val_str = format_exp_float(max_val, bold=True)

            max_val_offsets = [
                [50,-5],
                [35,35],
                [-45,20],
                [-55,-15],
                [-20,-35],
            ]

            max_desc = textwrap.fill(
                neuro_rec_max_props[col_name]['short'],
                15,
                break_long_words = False,
            )
            max_units = (
                rf" $\mathbf{{{neuro_rec_max_props[col_name]['units']}}}$"
                if 'units' in neuro_rec_max_props[col_name]
                else ''
            )
            max_label = f"{max_desc}:\n{max_val_str}{max_units}"
            ax.annotate(
                max_label,
                (theta_ax-0.15, 5),
                xytext=max_val_offsets[i],
                textcoords='offset points',
                clip_on=False,
                bbox=dict(
                    facecolor=TEAL,
                    alpha=0.8,
                    edgecolor=COLORS['text'],
                    boxstyle='round,pad=0.5'
                ),
                ha='center',
                va='center',
                color=COLORS['text'],
            )

        # Draw section dividers
        for i in range(N):
            theta_div = 2*np.pi * (i-1/2) / N
            ax.plot(
                [theta_div, theta_div],
                [0, 5],
                color=COLORS['border'],
                lw=1,
            )

        base_alpha = 0.7
        num_recs = len(sub_df)
        if num_recs > 0:
            normalized_alpha = 1 - (1 - base_alpha)**(1/num_recs)
        else:
            normalized_alpha = base_alpha

        for k, (j, row) in enumerate(sub_df.iterrows()):
            values = []
            valid_row = True
            for col_name in neuro_rec_data_columns:
                if organism not in neuro_rec_ax_oom_ranges or col_name not in neuro_rec_ax_oom_ranges[organism]:
                    valid_row = False
                    break
                col_val = row.get(col_name, np.nan)
                if pd.isna(col_val) or col_val <= 0:
                    values.append(0)
                else:
                    oom_range = neuro_rec_ax_oom_ranges[organism][col_name]
                    oom_val = oom_transform(col_val, oom_range)
                    values.append(oom_val)

            if not valid_row:
                continue

            # Plot bars on polar axis
            ax.bar(
                x=unique_angles,
                height=values,
                width=width,
                bottom=0.0,
                alpha=normalized_alpha,
                color=GOLD,
                edgecolor='none',
                clip_on = None,
            )

        ax.set_xticks([])
        ax.tick_params(axis='x', pad=35)
        ax.set_yticks(range(5), labels=[])
        ax.grid(axis='x', visible=False)
        ax.grid(
            axis='y',
            color=COLORS['grid'],
            alpha=0.3,
        )
        ax.spines['polar'].set_visible(False)
        ax.set_ylim(0, 5)

    # Generate per-organism radar charts
    for organism in organisms:
        organism_df = neuro_rec_df[neuro_rec_df['Organism'] == organism]

        for fixmov in ['fixated', 'moving']:
            sub_df = organism_df[organism_df['Fixated / moving'] == fixmov]

            if sub_df.empty:
                logger.info(f"  No data for {organism}/{fixmov}, skipping.")
                continue

            logger.info(f"  {organism}/{fixmov}")

            # Set up polar bar chart
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            rec_fig(ax, sub_df, organism, individual_studies=None)

            # Add title
            ax.set_title(f'{organism} - Recording Characteristics', fontsize=14, pad=20, color=COLORS['title'])

            plt.tight_layout()
            add_attribution(fig)
            fig.savefig(OUTPUT_FIGURES_NEURO_REC / f'{organism}-{fixmov}.svg', format='svg', bbox_inches='tight', pad_inches=0.2)
            fig.savefig(OUTPUT_FIGURES_NEURO_REC / f'{organism}-{fixmov}.png', format='png', dpi=150, bbox_inches='tight', pad_inches=0.2)
            plt.close()

# =============================================================================
# Figure 15: All sim-rec combined grid
# =============================================================================
@figure("all-sim-rec", "Combined simulation and recording grid")
def generate_all_sim_rec():
    import textwrap

    # Load both datasets
    neuro_sim_df = pd.read_csv(DATA_FILES["computational_models"])
    neuro_rec_df = pd.read_csv(DATA_FILES["neural_dynamics"])

    organisms = ['C. elegans', 'Drosophila', 'Zebrafish', 'Mouse', 'Human']

    # Standardize organism names in sim data
    organism_map = {'Mammalian': 'Mouse', 'Silicon': None}
    neuro_sim_df['Organism_mapped'] = neuro_sim_df['Organism'].replace(organism_map)

    # Standardize organism names in rec data
    neuro_rec_df['Organism'] = neuro_rec_df['Organism'].replace({
        'C. Elegans': 'C. elegans',
        'Zebrafish Larvae': 'Zebrafish',
    })
    neuro_rec_df = neuro_rec_df.rename(columns={'Fixated / moving': 'FixMov'})

    sim_data_columns = [
        'Connectivity accuracy', 'Percentage of neurons', 'Neurontypes',
        'Plasticity', 'Functional Accuracy', 'Neuromodulation',
        'Temporal resolution', 'Behavior', 'Personality-defining Characteristics', 'Learning',
    ]
    sim_column_labels = [textwrap.fill(col, 15, break_long_words=False) for col in sim_data_columns]

    rec_data_columns = ['Temporal resolution: Hz', 'Duration single session min per Individual',
                        'Resolution in µm isotropic', 'Number of neurons']

    # Convert to numeric
    for col in sim_data_columns:
        neuro_sim_df[col] = pd.to_numeric(neuro_sim_df[col], errors='coerce')
    for col in rec_data_columns:
        if col in neuro_rec_df.columns:
            neuro_rec_df[col] = pd.to_numeric(neuro_rec_df[col], errors='coerce')

    fig, axs = plt.subplots(5, 3, figsize=(16, 24), subplot_kw=dict(polar=True))

    for i, organism in enumerate(organisms):
        # Simulations column
        organism_sim_df = neuro_sim_df[neuro_sim_df['Organism_mapped'] == organism]
        organism_sim_df = organism_sim_df.dropna(subset=sim_data_columns)

        N_sim = len(sim_data_columns)
        angles_sim = np.linspace(0, 2 * np.pi, N_sim, endpoint=False)
        width_sim = 2 * np.pi / N_sim

        ax = axs[i, 0]
        theta = np.linspace(0, 2*np.pi, 100)
        ax.plot(theta, [3]*100, color=COLORS['border'], lw=2)

        for j in range(N_sim):
            theta_div = 2*np.pi * (j-1/2) / N_sim
            ax.plot([theta_div, theta_div], [0, 3], color=COLORS['border'], lw=1)

        if not organism_sim_df.empty:
            num_sims = len(organism_sim_df)
            normalized_alpha = 1 - (1 - 0.7)**(1/max(num_sims, 1))
            for _, row in organism_sim_df.iterrows():
                try:
                    values = row[sim_data_columns].astype(float).values
                    ax.bar(x=angles_sim, height=values, width=width_sim, bottom=0.0,
                           alpha=normalized_alpha, color=TEAL, edgecolor='none')
                except:
                    pass

        ax.set_xticks(angles_sim)
        ax.set_xticklabels(sim_column_labels, fontsize=8, color=COLORS['text'])
        ax.set_yticks([])
        ax.grid(False)
        ax.spines['polar'].set_visible(False)
        ax.set_ylim(0, 3)

        # Recording columns (fixated and moving)
        organism_rec_df = neuro_rec_df[neuro_rec_df['Organism'] == organism]

        for j, fixmov in enumerate(['fixated', 'moving']):
            ax = axs[i, j+1]
            sub_df = organism_rec_df[organism_rec_df['FixMov'] == fixmov]
            sub_df = sub_df.dropna(subset=rec_data_columns)

            N_rec = len(rec_data_columns)
            angles_rec = np.linspace(0, 2 * np.pi, N_rec, endpoint=False)
            width_rec = 2 * np.pi / N_rec

            ax.plot(theta, [5]*100, color=COLORS['border'], lw=2)
            for k in range(N_rec):
                theta_div = 2*np.pi * (k-1/2) / N_rec
                ax.plot([theta_div, theta_div], [0, 5], color=COLORS['border'], lw=1)

            if not sub_df.empty:
                num_recs = len(sub_df)
                normalized_alpha = 1 - (1 - 0.7)**(1/max(num_recs, 1))
                for _, row in sub_df.iterrows():
                    values = []
                    for col in rec_data_columns:
                        val = row[col]
                        if pd.notna(val) and val > 0:
                            log_val = np.log10(val)
                            normalized = min(5, max(0, (log_val + 2) * 1.0))
                            values.append(normalized)
                        else:
                            values.append(0)
                    ax.bar(x=angles_rec, height=values, width=width_rec, bottom=0.0,
                           alpha=normalized_alpha, color=GOLD, edgecolor='none')

            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)
            ax.spines['polar'].set_visible(False)
            ax.set_ylim(0, 5)

    # Add row labels
    for i, label in enumerate(organisms):
        fig.text(-0.02, 1 - (i+0.5)/5, label, rotation=90, va='center', fontweight='bold', fontsize=14)

    # Add column labels
    col_labels = ['Simulations', 'Recordings (fixated)', 'Recordings (moving)']
    for j, label in enumerate(col_labels):
        fig.text(0.17 + j/3, 1.01, label, ha='center', va='top', fontweight='bold', fontsize=14)

    plt.tight_layout()
    add_attribution(fig)
    fig.savefig(OUTPUT_FIGURES / 'all-sim-rec.svg', format='svg', bbox_inches='tight', pad_inches=0.1)
    fig.savefig(OUTPUT_FIGURES / 'all-sim-rec.png', format='png', dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()

# =============================================================================
# Figure 16: Funding figure
# =============================================================================
@figure("funding", "Megaproject budgets comparison")
def generate_funding():
    # Load funding data from new data structure
    neuro_proj_df = pd.read_csv(
        DATA_FILES["costs_neuro_megaprojects"]
    )
    other_proj_df = pd.read_csv(
        DATA_FILES["costs_non_neuro_megaprojects"]
    )

    # Clean neuroscience projects data
    neuro_proj_df = neuro_proj_df.rename(columns={
        'project name': 'Name',
        'Neuroscience funding ($M)': 'Budget_M',
        'start year': 'StartYear',
        'end year': 'EndYear',
    })
    neuro_proj_df['Category'] = 'Neuroscience'
    neuro_proj_df['Budget_M'] = pd.to_numeric(neuro_proj_df['Budget_M'], errors='coerce')
    neuro_proj_df['StartYear'] = pd.to_numeric(neuro_proj_df['StartYear'], errors='coerce')

    # Clean other projects data
    other_proj_df = other_proj_df.rename(columns={
        'project': 'Name',
        'cost ($B, 2024 dollars)': 'Budget_B',
        'field': 'Category',
    })
    other_proj_df['Budget_M'] = pd.to_numeric(other_proj_df['Budget_B'], errors='coerce') * 1000

    # Combine datasets (using available columns)
    neuro_clean = neuro_proj_df[['Name', 'Budget_M', 'Category']].dropna(subset=['Budget_M'])
    other_clean = other_proj_df[['Name', 'Budget_M', 'Category']].dropna(subset=['Budget_M'])

    all_funding = pd.concat([neuro_clean, other_clean], ignore_index=True)

    if len(all_funding) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))

        # Sort by budget for better visualization
        all_funding_sorted = all_funding.sort_values('Budget_M', ascending=True).tail(20)

        colors = [GOLD if cat == 'Neuroscience' else COLORS['caption']
                  for cat in all_funding_sorted['Category']]

        bars = ax.barh(all_funding_sorted['Name'], all_funding_sorted['Budget_M'], color=colors, alpha=0.8)

        ax.set_xscale('log')
        ax.set_xlabel('Budget (Million $)')
        ax.set_title('Megaproject Budgets Comparison')

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=GOLD, label='Neuroscience'),
            Patch(facecolor=COLORS['caption'], label='Other')
        ]
        ax.legend(handles=legend_elements, loc='lower right', frameon=True)

        plt.tight_layout()
        save_figure(fig, 'funding')
        plt.close()
    else:
        logger.info("  Skipped - no valid data")

# =============================================================================
# Figure 17: Organism Compute Requirements
# =============================================================================
@figure("organism-compute", "Neuron and synapse counts by organism")
def generate_organism_compute():
    # Load computational demands data
    compute_df = pd.read_csv(
        DATA_FILES["computational_demands"]
    )

    # Parse the data - it's in a wide format with organisms as columns
    organisms_row = compute_df.iloc[0]  # neurons row
    synapses_row = compute_df.iloc[1]   # synapses row

    # Extract organism data (skip the first column which is label)
    organism_names = ['C. elegans', 'Fly', 'Mouse (cortex)', 'Mouse (brain)', 'Human (cortex)', 'Human (brain)']
    organism_cols = ['C. elegans (body)', 'fly (brain)', 'mouse (cortex)', 'mouse (brain)', 'human (cortex)', 'human (brain)']

    neurons = []
    synapses = []
    for col in organism_cols:
        if col in compute_df.columns:
            neurons.append(pd.to_numeric(organisms_row[col], errors='coerce'))
            synapses.append(pd.to_numeric(synapses_row[col], errors='coerce'))

    if len(neurons) > 0:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        x = np.arange(len(organism_names))
        width = 0.6

        # Plot neurons
        axes[0].bar(x, neurons, width, color=TEAL, alpha=0.8, edgecolor='white')
        axes[0].set_yscale('log')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(organism_names, rotation=30, ha='right')
        axes[0].set_ylabel('Count')
        axes[0].set_title('Neuron Count by Organism')

        # Plot synapses
        axes[1].bar(x, synapses, width, color=GOLD, alpha=0.8, edgecolor='white')
        axes[1].set_yscale('log')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(organism_names, rotation=30, ha='right')
        axes[1].set_ylabel('Count')
        axes[1].set_title('Synapse Count by Organism')

        plt.tight_layout()
        save_figure(fig, 'organism-compute')
        plt.close()
    else:
        logger.info("  Skipped - no valid data")

# =============================================================================
# Figure 18: Bandwidth Scaling for Multiplexed Imaging
# =============================================================================
@figure("bandwidth-scaling", "Bandwidth requirements for multiplexed imaging")
def generate_bandwidth_scaling():
    # Data extracted from original figure
    # Resolution in nm vs bandwidth in bits/s for different numbers of multiplexed colors
    bandwidth_data = {
        'resolution_nm': [10, 15, 25, 50, 100],
        '1-color': [5.5e14, 2.2e14, 3.8e13, 5.0e12, 5.0e11],
        '5-color': [3.2e15, 9.0e14, 2.0e14, 2.5e13, 3.0e12],
        '10-color': [5.8e15, 1.9e15, 3.8e14, 5.5e13, 6.0e12],
        '15-color': [8.5e15, 3.2e15, 5.2e14, 8.5e13, 9.0e12],
        '20-color': [1.15e16, 4.2e15, 7.2e14, 1.5e14, 1.2e13],
        '25-color': [1.45e16, 4.8e15, 1.05e15, 1.6e14, 1.5e13],
        '30-color': [2.0e16, 5.5e15, 1.25e15, 1.9e14, 1.8e13],
    }

    bandwidth_df = pd.DataFrame(bandwidth_data)

    fig, ax = plt.subplots(figsize=(12, 9))

    # Use extended categorical colors
    bw_colors = {
        '1-color': EXTENDED_CATEGORICAL[0],
        '5-color': EXTENDED_CATEGORICAL[1],
        '10-color': EXTENDED_CATEGORICAL[2],
        '15-color': EXTENDED_CATEGORICAL[3],
        '20-color': EXTENDED_CATEGORICAL[4],
        '25-color': EXTENDED_CATEGORICAL[5],
        '30-color': EXTENDED_CATEGORICAL[6],
    }

    for col in bandwidth_df.columns[1:]:
        ax.plot(bandwidth_df['resolution_nm'], bandwidth_df[col], 'o-', label=col,
                color=bw_colors[col], linewidth=2, markersize=10)

    ax.set_yscale('log')
    ax.set_xscale('log')

    ax.set_xticks([10, 15, 25, 50, 100])
    ax.set_xticklabels(['10 nm', '15 nm', '25 nm', '50 nm', '100 nm'])
    ax.set_xlabel('Resolution (nm)')
    ax.set_xlim(8, 130)

    ax.set_ylabel('Bandwidth (bits/s)')

    yticks = [1e12, 1e13, 1e14, 1e15, 1e16]
    yticklabels = ['1.00 terabits/s', '10.00 terabits/s', '100.00 terabits/s',
                   '1.00 petabits/s', '10.00 petabits/s']
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    ax.set_ylim(3e11, 3e16)

    ax.set_title('Scaling of Bandwidth Requirements for Multiplexed Imaging of Whole Human Brain')

    ax.legend(title='Multiplexed Colors', loc='upper right', framealpha=0.95)

    ax.grid(True, which='major', linestyle='--', alpha=0.6, color=COLORS['grid'])
    ax.grid(True, which='minor', linestyle='--', alpha=0.3, color=COLORS['grid'])
    ax.set_axisbelow(True)

    plt.tight_layout()
    save_figure(fig, 'bandwidth-scaling')
    plt.close()

# =============================================================================
# Figure 19: Hardware Scaling (FLOPS, DRAM BW, Interconnect BW)
# =============================================================================
@figure("hardware-scaling", "Hardware FLOPS and bandwidth scaling over time")
def generate_hardware_scaling():
    from scipy import stats

    # Data for hardware scaling
    hw_flops = {
        'name': ['Pentium 4', 'GTX 580', 'K40', 'KNL', 'TPUv3', 'A100', 'H100', 'Gaudi 2', 'B200'],
        'year': [2005, 2010, 2014, 2016, 2018, 2020, 2022, 2022, 2024],
        'value': [90, 6000, 15000, 22000, 420000, 1250000, 2000000, 1100000, 4500000]
    }
    dram_bw = {
        'name': ['GDDR4', 'GDDR5', 'HBM', 'HBM 2', 'HBM 3', 'HBM3E'],
        'year': [2007, 2010, 2015, 2018, 2021, 2024],
        'value': [1.8, 10, 30, 70, 120, 250]
    }
    interconnect_bw = {
        'name': ['PCIe 2.0', 'PCIe 3.0', 'NVLink 1.0', 'PCIe 5.0', 'NVLink 4.0'],
        'year': [2007, 2011, 2016, 2019, 2024],
        'value': [1.2, 2, 3, 8, 50]
    }

    color_flops = HARDWARE_COLORS['flops']
    color_dram = HARDWARE_COLORS['dram']
    color_interconnect = HARDWARE_COLORS['interconnect']

    fig, ax = plt.subplots(figsize=(12, 9))

    # Plot data points with labels
    ax.scatter(hw_flops['year'], hw_flops['value'], color=color_flops, s=80, zorder=5)
    for i, name in enumerate(hw_flops['name']):
        y_offset = 1.3 if name not in ['Gaudi 2'] else 0.7
        ha = 'left' if name == 'Gaudi 2' else 'center'
        ax.annotate(name, (hw_flops['year'][i], hw_flops['value'][i] * y_offset),
                    ha=ha, va='bottom', fontsize=9, color=color_flops)

    ax.scatter(dram_bw['year'], dram_bw['value'], color=color_dram, s=80, zorder=5)
    for i, name in enumerate(dram_bw['name']):
        ax.annotate(name, (dram_bw['year'][i], dram_bw['value'][i] * 1.3),
                    ha='center', va='bottom', fontsize=9, color=color_dram)

    ax.scatter(interconnect_bw['year'], interconnect_bw['value'], color=color_interconnect, s=80, zorder=5)
    for i, name in enumerate(interconnect_bw['name']):
        ax.annotate(name, (interconnect_bw['year'][i], interconnect_bw['value'][i] * 1.3),
                    ha='center', va='bottom', fontsize=9, color=color_interconnect)

    # Fit and plot trend lines
    def fit_trend(years, values):
        log_values = np.log10(values)
        slope, intercept, *_ = stats.linregress(years, log_values)
        return slope, intercept

    x_trend = np.linspace(2005, 2026, 100)

    slope_flops, intercept_flops = fit_trend(hw_flops['year'], hw_flops['value'])
    y_trend_flops = 10 ** (intercept_flops + slope_flops * x_trend)
    ax.plot(x_trend, y_trend_flops, color=color_flops, linewidth=3, alpha=0.7, zorder=1)

    slope_dram, intercept_dram = fit_trend(dram_bw['year'], dram_bw['value'])
    y_trend_dram = 10 ** (intercept_dram + slope_dram * x_trend)
    ax.plot(x_trend, y_trend_dram, color=color_dram, linewidth=3, alpha=0.5, zorder=1)
    ax.fill_between(x_trend, y_trend_dram * 0.5, y_trend_dram * 2, color=color_dram, alpha=0.15, zorder=0)

    slope_inter, intercept_inter = fit_trend(interconnect_bw['year'], interconnect_bw['value'])
    y_trend_inter = 10 ** (intercept_inter + slope_inter * x_trend)
    ax.plot(x_trend, y_trend_inter, color=color_interconnect, linewidth=3, alpha=0.5, zorder=1)
    ax.fill_between(x_trend, y_trend_inter * 0.5, y_trend_inter * 2, color=color_interconnect, alpha=0.15, zorder=0)

    # Calculate scaling factors
    flops_20yr = 10 ** (slope_flops * 20)
    dram_20yr = 10 ** (slope_dram * 20)
    inter_20yr = 10 ** (slope_inter * 20)
    flops_2yr = 10 ** (slope_flops * 2)
    dram_2yr = 10 ** (slope_dram * 2)
    inter_2yr = 10 ** (slope_inter * 2)

    # Add legend text
    ax.text(0.02, 0.98, 'HW FLOPS:', transform=ax.transAxes, fontsize=12, fontweight='bold',
            va='top', ha='left', color=color_flops)
    ax.text(0.18, 0.98, f'{flops_20yr:.0f}x / 20 yrs ({flops_2yr:.1f}x/2yrs)', transform=ax.transAxes,
            fontsize=12, va='top', ha='left', color=color_flops)
    ax.text(0.02, 0.93, 'DRAM BW:', transform=ax.transAxes, fontsize=12, fontweight='bold',
            va='top', ha='left', color=color_dram)
    ax.text(0.18, 0.93, f'{dram_20yr:.0f}x / 20 yrs ({dram_2yr:.1f}x/2yrs)', transform=ax.transAxes,
            fontsize=12, va='top', ha='left', color=color_dram)
    ax.text(0.02, 0.88, 'Interconnect BW:', transform=ax.transAxes, fontsize=12, fontweight='bold',
            va='top', ha='left', color=color_interconnect)
    ax.text(0.18, 0.88, f'{inter_20yr:.0f}x / 20 yrs ({inter_2yr:.1f}x/2yrs)', transform=ax.transAxes,
            fontsize=12, va='top', ha='left', color=color_interconnect)

    ax.set_yscale('log')
    ax.set_xlim(2004, 2026)
    ax.set_ylim(0.01, 10000000)
    ax.grid(True, which='major', axis='both', linestyle='-', alpha=0.3, color=COLORS['grid'])

    plt.tight_layout()
    save_figure(fig, 'hardware-scaling')
    plt.close()

# =============================================================================
# Main Entry Point
# =============================================================================
def list_figures():
    """List all available figures."""
    logger.info("Available figures:")
    logger.info("")
    for name, info in FIGURE_REGISTRY.items():
        desc = info.get('description', '')
        logger.info(f"  {name:30s} {desc}")
    logger.info("")
    logger.info(f"Total: {len(FIGURE_REGISTRY)} figures")


def generate_figures(figure_names=None):
    """Generate specified figures, or all if none specified."""
    ensure_output_dirs()

    if figure_names:
        # Generate specific figures
        for name in figure_names:
            if name in FIGURE_REGISTRY:
                FIGURE_REGISTRY[name]['func']()
            else:
                logger.warning(f"Unknown figure: {name}")
                logger.info(f"Use --list to see available figures")
    else:
        # Generate all figures
        logger.info("=" * 60)
        logger.info("Brain Emulation Report 2025 - Figure Generation")
        logger.info("=" * 60)

        for name, info in FIGURE_REGISTRY.items():
            info['func']()

        logger.info("")
        logger.info("=" * 60)
        logger.info("Figure generation complete!")
        logger.info("=" * 60)
        logger.info(f"Output files saved to: {OUTPUT_FIGURES}/")


def build_all():
    """Run full pipeline: figures + downloads + HTML."""
    generate_figures()

    # Build Download ZIPs
    logger.info("")
    logger.info("=" * 60)
    logger.info("Building downloadable ZIP files...")
    logger.info("=" * 60)

    try:
        from build_downloads import main as build_downloads
        build_downloads()
    except Exception as e:
        logger.error(f"Error building downloads: {e}")
        logger.info("You can run 'python build_downloads.py' separately to generate ZIPs.")

    # Build Standalone HTML Files
    logger.info("")
    logger.info("=" * 60)
    logger.info("Building standalone HTML files for iframe embedding...")
    logger.info("=" * 60)

    try:
        from build_standalone_html import main as build_standalone_html
        build_standalone_html()
    except Exception as e:
        logger.error(f"Error building standalone HTML: {e}")
        logger.info("You can run 'python build_standalone_html.py' separately.")


def main():
    """Main entry point with CLI argument parsing."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate figures for the Brain Emulation Report 2025',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_figures.py              # Generate all figures
  python run_all_figures.py --list       # List available figures
  python run_all_figures.py num-neurons  # Generate specific figure
  python run_all_figures.py --all        # Full pipeline (figures + downloads + HTML)
        """
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available figures'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run full pipeline: figures + downloads + HTML'
    )
    parser.add_argument(
        'figures',
        nargs='*',
        help='Specific figures to generate (by name)'
    )

    args = parser.parse_args()

    if args.list:
        list_figures()
    elif args.all:
        build_all()
    elif args.figures:
        generate_figures(args.figures)
    else:
        generate_figures()


if __name__ == "__main__":
    main()
