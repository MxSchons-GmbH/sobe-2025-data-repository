#!/usr/bin/env python3
"""
Generate a plot showing scaling of bandwidth requirements for multiplexed
imaging of whole human brain at different resolutions and color channels.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from style import (
    apply_style, save_figure, add_attribution,
    COLORS, EXTENDED_CATEGORICAL, FONT_SIZES
)

apply_style()

# Data extracted from original figure
# Resolution in nm vs bandwidth in bits/s for different numbers of multiplexed colors
data = {
    'resolution_nm': [10, 15, 25, 50, 100],
    '1-color': [5.5e14, 2.2e14, 3.8e13, 5.0e12, 5.0e11],
    '5-color': [3.2e15, 9.0e14, 2.0e14, 2.5e13, 3.0e12],
    '10-color': [5.8e15, 1.9e15, 3.8e14, 5.5e13, 6.0e12],
    '15-color': [8.5e15, 3.2e15, 5.2e14, 8.5e13, 9.0e12],
    '20-color': [1.15e16, 4.2e15, 7.2e14, 1.5e14, 1.2e13],
    '25-color': [1.45e16, 4.8e15, 1.05e15, 1.6e14, 1.5e13],
    '30-color': [2.0e16, 5.5e15, 1.25e15, 1.9e14, 1.8e13],
}

df = pd.DataFrame(data)

# Set up the figure
fig, ax = plt.subplots(figsize=(12, 9))

# Use extended categorical colors from style
colors = {
    '1-color': EXTENDED_CATEGORICAL[0],   # gold
    '5-color': EXTENDED_CATEGORICAL[1],   # teal
    '10-color': EXTENDED_CATEGORICAL[2],  # purple
    '15-color': EXTENDED_CATEGORICAL[3],  # brown
    '20-color': EXTENDED_CATEGORICAL[4],  # green
    '25-color': EXTENDED_CATEGORICAL[5],  # rust brown
    '30-color': EXTENDED_CATEGORICAL[6],  # pink
}

# Plot each color channel series
for col in df.columns[1:]:
    ax.plot(df['resolution_nm'], df[col], 'o-', label=col,
            color=colors[col], linewidth=2, markersize=10)

# Set log scale for both axes
ax.set_yscale('log')
ax.set_xscale('log')

# Customize x-axis
ax.set_xticks([10, 15, 25, 50, 100])
ax.set_xticklabels(['10 nm', '15 nm', '25 nm', '50 nm', '100 nm'], fontsize=FONT_SIZES['tick'])
ax.set_xlabel('Resolution (nm)', fontsize=FONT_SIZES['axis_title'])
ax.set_xlim(8, 130)

# Customize y-axis
ax.set_ylabel('Bandwidth (bits/s)', fontsize=FONT_SIZES['axis_title'])

# Set specific y-ticks with human-readable labels
yticks = [1e12, 1e13, 1e14, 1e15, 1e16]
yticklabels = ['1.00 terabits/s', '10.00 terabits/s', '100.00 terabits/s',
               '1.00 petabits/s', '10.00 petabits/s']
ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels, fontsize=FONT_SIZES['tick'])

# Extend y-axis range
ax.set_ylim(3e11, 3e16)

# Add title
ax.set_title('Scaling of Bandwidth Requirements for Multiplexed Imaging of Whole Human Brain',
             fontsize=FONT_SIZES['title'], color=COLORS['title'], pad=15)

# Add legend
ax.legend(title='Multiplexed Colors', loc='upper right', framealpha=0.95,
          fontsize=FONT_SIZES['legend'], title_fontsize=FONT_SIZES['legend'])

# Configure grid using style colors
ax.grid(True, which='major', linestyle='--', alpha=0.6, color=COLORS['grid'])
ax.grid(True, which='minor', linestyle='--', alpha=0.3, color=COLORS['grid'])
ax.set_axisbelow(True)

# Adjust layout
plt.tight_layout()

# Save the figure using the standard save_figure function
save_figure(fig, 'bandwidth-scaling')

print("Plot saved to figures/generated/bandwidth-scaling.svg and .png")
plt.close()
