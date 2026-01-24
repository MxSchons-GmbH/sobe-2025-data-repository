"""
Brain Emulation Report 2025 - Figure Style Configuration

Centralized styling for all visualization notebooks.
Import this module and call apply_style() before creating figures.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import matplotlib as mpl
from cycler import cycler

from paths import OUTPUT_FIGURES
from data_loader import get_species_neurons

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

# =============================================================================
# COLORBLIND-FRIENDLY PALETTES (Okabe-Ito)
# =============================================================================
# These colors are distinguishable by people with all types of color vision
# Reference: https://jfly.uni-koeln.de/color/

COLORBLIND_CATEGORICAL = [
    '#E69F00',  # orange
    '#56B4E9',  # sky blue
    '#009E73',  # bluish green
    '#F0E442',  # yellow
    '#0072B2',  # blue
    '#D55E00',  # vermillion
    '#CC79A7',  # reddish purple
    '#000000',  # black
]

# Colorblind-safe sequential (luminance-based)
COLORBLIND_SEQUENTIAL = ['#FFFFFF', '#D9D9D9', '#969696', '#525252', '#000000']

# Colorblind-safe diverging
COLORBLIND_DIVERGING = ['#D55E00', '#F0E442', '#FFFFFF', '#56B4E9', '#0072B2']

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
GREEN = '#2ECC71'  # illustration/highlight green

# Extended palette for charts with many categories
EXTENDED_CATEGORICAL = [
    '#D4A84B',  # gold
    '#4A90A4',  # teal
    '#6B6080',  # purple
    '#8B7355',  # brown
    '#5C8B6B',  # green
    '#2ECC71',  # bright green (illustration)
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
# HATCHING PATTERNS (for colorblind accessibility)
# =============================================================================
# Use these with color to provide redundant encoding

HATCHING_PATTERNS = [
    '',       # solid (no hatch)
    '///',    # diagonal lines
    '\\\\\\', # reverse diagonal
    '|||',    # vertical lines
    '---',    # horizontal lines
    'xxx',    # crossed diagonals
    '+++',    # crossed lines
    'ooo',    # circles
]

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
    'markeredgecolor': '#4A4A5A',  # COLORS['text'] - visible on gray backgrounds
}

BAR_CHART = {
    'width': 0.7,
    'edgecolor': '#4A4A5A',  # COLORS['text'] - visible on gray backgrounds
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

ATTRIBUTION = "Zanichelli & Schons et al., State of Brain Emulation Report 2025"


def add_attribution(fig=None, position='figure'):
    """
    Add attribution text to bottom right of figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure, optional
        The figure to add attribution to (defaults to current figure)
    position : str
        'figure' - position relative to full figure (default)
        'axes' - position relative to the last axes (better for multi-panel figures)
    """
    if fig is None:
        fig = plt.gcf()

    if position == 'axes' and fig.axes:
        # Position relative to the rightmost axis to avoid extending figure bounds
        # Find the rightmost axis
        rightmost_ax = max(fig.axes, key=lambda ax: ax.get_position().x1)
        ax_pos = rightmost_ax.get_position()
        # Place below the rightmost axes with padding
        fig.text(
            ax_pos.x1, -0.02, ATTRIBUTION,
            ha='right', va='top',
            fontsize=7, color=COLORS['caption'],
            style='italic',
            transform=fig.transFigure
        )
    else:
        # Default: position relative to figure, below the content
        fig.text(
            0.99, -0.02, ATTRIBUTION,
            ha='right', va='top',
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


def get_sequential_cmap(colorblind_safe=False):
    """
    Get sequential colormap for heatmaps.

    Parameters
    ----------
    colorblind_safe : bool
        If True, use a luminance-based grayscale colormap
    """
    from matplotlib.colors import LinearSegmentedColormap
    if colorblind_safe:
        return LinearSegmentedColormap.from_list('report_sequential_cb', COLORBLIND_SEQUENTIAL)
    return LinearSegmentedColormap.from_list('report_sequential', SEQUENTIAL_COLORS)


def get_heatmap_cmap(colorblind_safe=False):
    """
    Get heatmap colormap (low -> mid -> high).

    Parameters
    ----------
    colorblind_safe : bool
        If True, use viridis (perceptually uniform, colorblind-friendly)
    """
    from matplotlib.colors import LinearSegmentedColormap
    if colorblind_safe:
        # Use matplotlib's built-in viridis which is colorblind-safe
        return plt.cm.viridis
    colors = [HEATMAP_GRADIENT['low'], HEATMAP_GRADIENT['mid'], HEATMAP_GRADIENT['high']]
    return LinearSegmentedColormap.from_list('report_heatmap', colors)


def get_categorical_palette(n=None, colorblind_safe=False):
    """
    Get categorical color palette.

    Parameters
    ----------
    n : int, optional
        Limit to n colors
    colorblind_safe : bool
        If True, use Okabe-Ito colorblind-friendly palette
    """
    palette = COLORBLIND_CATEGORICAL if colorblind_safe else CATEGORICAL_COLORS
    if n is None:
        return palette
    return palette[:n]


def get_primary_palette(n=None, colorblind_safe=False):
    """
    Get primary color palette.

    Parameters
    ----------
    n : int, optional
        Limit to n colors
    colorblind_safe : bool
        If True, use Okabe-Ito colorblind-friendly palette
    """
    if colorblind_safe:
        # Use subset of Okabe-Ito that works well for sequential data
        palette = ['#56B4E9', '#0072B2', '#009E73', '#000000']
    else:
        palette = PRIMARY_COLORS
    if n is None:
        return palette
    return palette[:n]


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


def place_legend(ax, fig=None, position='auto', **kwargs):
    """
    Intelligently place legend based on figure size and data density.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to add the legend to
    fig : matplotlib.figure.Figure, optional
        The figure (used for sizing calculations)
    position : str
        'auto' - automatically determine best placement
        'outside_right' - place outside to the right
        'outside_top' - place outside at top
        'inside_best' - place inside at best location
        'upper_left', 'upper_right', etc. - standard matplotlib locations
    **kwargs : dict
        Additional arguments passed to ax.legend()

    Returns
    -------
    matplotlib.legend.Legend
        The created legend
    """
    if fig is None:
        fig = plt.gcf()

    figwidth = fig.get_figwidth()

    default_kwargs = {
        'frameon': True,
        'facecolor': COLORS['figure_bg'],
        'edgecolor': COLORS['grid'],
        'framealpha': 0.9,
        'fontsize': FONT_SIZES['legend'],
    }
    default_kwargs.update(kwargs)

    if position == 'auto':
        # Use outside placement for wider figures, inside for narrow ones
        if figwidth >= 10:
            position = 'outside_right'
        else:
            position = 'inside_best'

    if position == 'outside_right':
        default_kwargs['bbox_to_anchor'] = (1.02, 1)
        default_kwargs['loc'] = 'upper left'
    elif position == 'outside_top':
        default_kwargs['bbox_to_anchor'] = (0.5, 1.02)
        default_kwargs['loc'] = 'lower center'
        default_kwargs['ncol'] = default_kwargs.get('ncol', 3)
    elif position == 'inside_best':
        default_kwargs['loc'] = 'best'
    else:
        # Use position as matplotlib loc string
        default_kwargs['loc'] = position

    return ax.legend(**default_kwargs)


def scale_fontsize(base_size, figsize=None, num_elements=None, min_size=6, max_size=14):
    """
    Scale font size based on figure dimensions and data density.

    Parameters
    ----------
    base_size : int
        The base font size (from FONT_SIZES)
    figsize : tuple, optional
        (width, height) of the figure in inches
    num_elements : int, optional
        Number of data elements (e.g., rows in heatmap)
    min_size : int
        Minimum font size to return
    max_size : int
        Maximum font size to return

    Returns
    -------
    int
        Scaled font size
    """
    scale = 1.0

    # Scale based on figure size
    if figsize is not None:
        width, height = figsize
        # Larger figures can use larger fonts
        area_scale = (width * height) / (10 * 6)  # Relative to default 10x6
        scale *= min(1.3, max(0.8, area_scale ** 0.3))

    # Scale down for high data density
    if num_elements is not None:
        if num_elements > 50:
            scale *= 0.7
        elif num_elements > 30:
            scale *= 0.8
        elif num_elements > 20:
            scale *= 0.9

    scaled = int(base_size * scale)
    return max(min_size, min(max_size, scaled))


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


def save_figure(fig, name, output_dir=None, print_quality=False, web_formats=True, attribution_position='figure'):
    """
    Save figure in multiple formats with attribution.

    Generates SVG (vector), PNG (raster), and optionally WebP/AVIF for web optimization.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to save
    name : str
        Base name for the output files (without extension)
    output_dir : Path or str, optional
        Output directory (defaults to OUTPUT_FIGURES)
    print_quality : bool
        If True, also save a high-DPI (300) PNG for print
    web_formats : bool
        If True, also save WebP and AVIF versions for modern browsers
    attribution_position : str
        'figure' - position attribution relative to full figure (default)
        'axes' - position attribution relative to the rightmost axes
                 (better for figures where bbox_inches='tight' would extend bounds)
    """
    from pathlib import Path
    from PIL import Image

    if output_dir is None:
        output_dir = OUTPUT_FIGURES
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    add_attribution(fig, position=attribution_position)

    save_kwargs = {
        'bbox_inches': EXPORT['bbox_inches'],
        'pad_inches': EXPORT['pad_inches'],
    }

    # Always save SVG (vector, resolution-independent)
    fig.savefig(output_dir / f'{name}.svg', format='svg', **save_kwargs)

    # Save standard PNG for web/screen
    png_path = output_dir / f'{name}.png'
    fig.savefig(png_path, format='png', dpi=EXPORT['dpi'], **save_kwargs)

    # Generate WebP and AVIF from the PNG for better web performance
    if web_formats:
        try:
            with Image.open(png_path) as img:
                # Convert to RGB if necessary (AVIF/WebP don't always handle RGBA well)
                if img.mode == 'RGBA':
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                    img_rgb = background
                else:
                    img_rgb = img.convert('RGB') if img.mode != 'RGB' else img

                # Save WebP (lossy, good quality, ~30-50% smaller than PNG)
                img_rgb.save(
                    output_dir / f'{name}.webp',
                    'WEBP',
                    quality=90,
                    method=6  # Slower but better compression
                )

                # Save AVIF (lossy, excellent quality, ~50-70% smaller than PNG)
                img_rgb.save(
                    output_dir / f'{name}.avif',
                    'AVIF',
                    quality=85,
                    speed=4  # Balance between speed and compression
                )
        except Exception as e:
            # Don't fail figure generation if web formats fail
            import logging
            logging.getLogger(__name__).warning(f"Could not generate web formats for {name}: {e}")

    # Optionally save high-DPI PNG for print
    if print_quality:
        fig.savefig(
            output_dir / f'{name}-print.png',
            format='png',
            dpi=EXPORT['dpi_print'],
            **save_kwargs
        )


# Species reference data for neuron count lines
# Loaded from canonical organisms.tsv file via data_loader
SPECIES_NEURONS = get_species_neurons()


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
