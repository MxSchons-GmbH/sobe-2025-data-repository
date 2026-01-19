"""
Brain Emulation Report 2025 - Figure Style Configuration

Centralized styling for all visualization notebooks.
Import this module and call apply_style() before creating figures.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from cycler import cycler

from paths import OUTPUT_FIGURES

# =============================================================================
# COLOR SYSTEM
# =============================================================================

# Primary palette (use for main data series)
PRIMARY_COLORS = ['#6B6080', '#8B7A9E', '#A99BBD', '#C7BDDC']

# Categorical palette (use for distinct categories)
CATEGORICAL_COLORS = ['#D4A84B', '#4A90A4', '#6B6080', '#8B7355', '#5C8B6B']

# Sequential/heatmap gradient
SEQUENTIAL_COLORS = ['#F7F5F2', '#E5DFD8', '#C7BDDC', '#8B7A9E', '#5C5470']

# Heatmap gradient
HEATMAP_GRADIENT = {'low': '#F7F5F2', 'mid': '#D4A84B', 'high': '#8B5A2B'}

# UI Colors
COLORS = {
    'background': '#F7F5F2',      # warm off-white
    'figure_bg': '#FFFFFF',       # figure background
    'plot_bg': '#FAFAF8',         # plot area background
    'text': '#4A4A5A',            # body text, axis labels
    'title': '#3A3A48',           # figure titles
    'headers': '#6B6080',         # figure labels
    'grid': '#E8E5E1',            # grid lines
    'border': '#D8D4CF',          # borders, spines
    'caption': '#787470',         # caption text
    'highlight': '#D4A84B',       # gold accent
    'link': '#4A90A4',            # teal accent
}

# Named colors for convenience
GOLD = '#D4A84B'
PURPLE = '#6B6080'
TEAL = '#4A90A4'

# Extended palette for charts with many categories
EXTENDED_CATEGORICAL = [
    '#D4A84B',  # gold
    '#4A90A4',  # teal
    '#6B6080',  # purple
    '#8B7355',  # brown
    '#5C8B6B',  # green
    '#8c564b',  # rust brown
    '#e377c2',  # pink
    '#7f7f7f',  # gray
    '#bcbd22',  # olive
    '#17becf',  # cyan
]

# Hardware/technical chart colors
HARDWARE_COLORS = {
    'flops': '#4A4A4A',       # dark gray - compute performance
    'dram': '#2E8B57',        # sea green - memory bandwidth
    'interconnect': '#9370DB', # medium purple - interconnect bandwidth
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================

FONTS = {
    'title': ['Playfair Display', 'Georgia', 'serif'],
    'body': ['Inter', 'Helvetica Neue', 'Arial', 'sans-serif'],
    'mono': ['JetBrains Mono', 'Consolas', 'monospace'],
}

# Font sizes (in points)
FONT_SIZES = {
    'title': 16,
    'axis_title': 12,
    'tick': 11,
    'legend': 11,
    'annotation': 11,
    'data_label': 10,
}

# =============================================================================
# CHART SPECIFICATIONS
# =============================================================================

LINE_CHART = {
    'linewidth': 2,
    'markersize': 6,
    'markeredgewidth': 1.5,
    'markeredgecolor': '#FFFFFF',
}

BAR_CHART = {
    'width': 0.7,
    'edgecolor': '#FFFFFF',
    'linewidth': 1,
}

SCATTER = {
    'size': 48,
    'alpha': 0.7,
    'edgecolor': '#FFFFFF',
    'linewidth': 0.5,
}

RADAR_CHART = {
    'grid_color': '#E8E5E1',
    'grid_width': 1,
    'fill_color': '#D4A84B',
    'fill_alpha': 0.2,
    'stroke_color': '#D4A84B',
    'stroke_width': 2,
    'point_size': 4,
}

# =============================================================================
# EXPORT SETTINGS
# =============================================================================

EXPORT = {
    'dpi': 150,
    'dpi_print': 300,
    'format': 'png',
    'transparent': False,
    'bbox_inches': 'tight',
    'pad_inches': 0.1,
}

# =============================================================================
# ATTRIBUTION
# =============================================================================

ATTRIBUTION = "Zanichelli, Schons et al, State of Brain Emulation Report 2025"


def add_attribution(fig=None):
    """Add attribution text to bottom right of figure."""
    if fig is None:
        fig = plt.gcf()
    fig.text(
        0.99, 0.01, ATTRIBUTION,
        ha='right', va='bottom',
        fontsize=7, color=COLORS['caption'],
        style='italic',
        transform=fig.transFigure
    )


# =============================================================================
# STYLE APPLICATION
# =============================================================================

def apply_style():
    """Apply Brain Emulation Report 2025 figure style globally."""

    plt.rcParams.update({
        # Figure
        'figure.facecolor': COLORS['figure_bg'],
        'figure.edgecolor': COLORS['grid'],
        'figure.dpi': EXPORT['dpi'],
        'figure.figsize': [10, 6],

        # Axes
        'axes.facecolor': COLORS['plot_bg'],
        'axes.edgecolor': COLORS['border'],
        'axes.linewidth': 1,
        'axes.grid': True,
        'axes.axisbelow': True,
        'axes.labelsize': FONT_SIZES['axis_title'],
        'axes.labelweight': 500,
        'axes.labelcolor': COLORS['text'],
        'axes.titlesize': FONT_SIZES['title'],
        'axes.titleweight': 600,
        'axes.titlecolor': COLORS['title'],
        'axes.titlepad': 12,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.prop_cycle': cycler(color=PRIMARY_COLORS + [GOLD]),

        # Grid
        'grid.color': COLORS['grid'],
        'grid.linewidth': 1,
        'grid.alpha': 1.0,

        # Ticks
        'xtick.labelsize': FONT_SIZES['tick'],
        'ytick.labelsize': FONT_SIZES['tick'],
        'xtick.color': COLORS['text'],
        'ytick.color': COLORS['text'],
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 4,
        'ytick.major.size': 4,
        'xtick.major.width': 1,
        'ytick.major.width': 1,
        'xtick.minor.size': 2,
        'ytick.minor.size': 2,

        # Legend
        'legend.fontsize': FONT_SIZES['legend'],
        'legend.frameon': True,
        'legend.facecolor': COLORS['figure_bg'],
        'legend.edgecolor': COLORS['grid'],
        'legend.framealpha': 0.9,
        'legend.borderpad': 0.5,
        'legend.labelspacing': 0.4,

        # Font
        'font.family': 'sans-serif',
        'font.sans-serif': FONTS['body'],
        'font.size': FONT_SIZES['tick'],

        # Text
        'text.color': COLORS['text'],

        # Lines
        'lines.linewidth': LINE_CHART['linewidth'],
        'lines.markersize': LINE_CHART['markersize'],
        'lines.markeredgewidth': LINE_CHART['markeredgewidth'],
        'lines.markeredgecolor': LINE_CHART['markeredgecolor'],

        # Patches (bars, etc)
        'patch.edgecolor': BAR_CHART['edgecolor'],
        'patch.linewidth': BAR_CHART['linewidth'],

        # Scatter
        'scatter.edgecolors': SCATTER['edgecolor'],

        # Savefig
        'savefig.dpi': EXPORT['dpi'],
        'savefig.facecolor': COLORS['figure_bg'],
        'savefig.edgecolor': 'none',
        'savefig.bbox': 'tight',
        'savefig.pad_inches': EXPORT['pad_inches'],
    })


def get_categorical_palette(n=None):
    """Get categorical color palette, optionally limited to n colors."""
    if n is None:
        return CATEGORICAL_COLORS
    return CATEGORICAL_COLORS[:n]


def get_primary_palette(n=None):
    """Get primary color palette, optionally limited to n colors."""
    if n is None:
        return PRIMARY_COLORS
    return PRIMARY_COLORS[:n]


def get_sequential_cmap():
    """Get sequential colormap for heatmaps."""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list('report_sequential', SEQUENTIAL_COLORS)


def get_heatmap_cmap():
    """Get heatmap colormap (low -> mid -> high)."""
    from matplotlib.colors import LinearSegmentedColormap
    colors = [HEATMAP_GRADIENT['low'], HEATMAP_GRADIENT['mid'], HEATMAP_GRADIENT['high']]
    return LinearSegmentedColormap.from_list('report_heatmap', colors)


def style_legend(ax, loc='best', **kwargs):
    """Style legend with report defaults."""
    legend = ax.legend(
        loc=loc,
        frameon=True,
        facecolor=COLORS['figure_bg'],
        edgecolor=COLORS['grid'],
        framealpha=0.9,
        fontsize=FONT_SIZES['legend'],
        **kwargs
    )
    return legend


def annotate_point(ax, text, xy, xytext, **kwargs):
    """Add styled annotation to a point."""
    default_kwargs = {
        'fontsize': FONT_SIZES['annotation'],
        'color': COLORS['text'],
        'arrowprops': dict(
            arrowstyle='->',
            color=COLORS['caption'],
            lw=1,
        ),
        'bbox': dict(
            boxstyle='round,pad=0.3',
            facecolor=COLORS['grid'],
            edgecolor='none',
            alpha=0.9,
        ),
    }
    default_kwargs.update(kwargs)
    return ax.annotate(text, xy=xy, xytext=xytext, **default_kwargs)


def save_figure(fig, name, output_dir=None):
    """Save figure in both SVG and PNG formats with attribution."""
    from pathlib import Path
    if output_dir is None:
        output_dir = OUTPUT_FIGURES
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    add_attribution(fig)
    fig.savefig(output_dir / f'{name}.svg', format='svg', **{
        'bbox_inches': EXPORT['bbox_inches'],
        'pad_inches': EXPORT['pad_inches'],
    })
    fig.savefig(output_dir / f'{name}.png', format='png', dpi=EXPORT['dpi'], **{
        'bbox_inches': EXPORT['bbox_inches'],
        'pad_inches': EXPORT['pad_inches'],
    })


# Species reference data for neuron count lines
SPECIES_NEURONS = {
    'C. elegans': 302,
    'Zebrafish (larva)': 100_000,
    'Mouse': 67_873_741,
    'Macaque': 6_376_160_000,
    'Human': 86_060_000_000,
}


def plot_species_hlines(ax, xmin, xmax, label_x=None, species=None):
    """Plot horizontal reference lines for species neuron counts."""
    if species is None:
        species = SPECIES_NEURONS
    if label_x is None:
        label_x = xmin

    for name, neurons in species.items():
        ax.axhline(y=neurons, color=COLORS['caption'], ls=':', lw=1, alpha=0.7)
        ax.text(
            label_x, neurons, f'  {name}',
            va='bottom', fontsize=FONT_SIZES['annotation'] - 1,
            color=COLORS['caption']
        )


# Initialize style on import
apply_style()
