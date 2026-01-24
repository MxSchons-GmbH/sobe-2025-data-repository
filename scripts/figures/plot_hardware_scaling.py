#!/usr/bin/env python3
"""
Generate a plot showing hardware FLOPS, DRAM bandwidth, and interconnect
bandwidth scaling over time (2005-2025).
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from style import (
    apply_style, save_figure, add_attribution,
    COLORS, FONT_SIZES, HARDWARE_COLORS
)

apply_style()

# Data extracted from original figure
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

# Colors from centralized style
color_flops = HARDWARE_COLORS['flops']
color_dram = HARDWARE_COLORS['dram']
color_interconnect = HARDWARE_COLORS['interconnect']

# Set up the figure
fig, ax = plt.subplots(figsize=(12, 9))

# Plot HW FLOPS data points
ax.scatter(hw_flops['year'], hw_flops['value'], color=color_flops, s=80, zorder=5)
for i, name in enumerate(hw_flops['name']):
    # Position labels above points, with some adjustments for crowded areas
    y_offset = 1.3 if name not in ['Gaudi 2'] else 0.7
    ha = 'center'
    if name == 'Gaudi 2':
        ha = 'left'
    ax.annotate(name, (hw_flops['year'][i], hw_flops['value'][i] * y_offset),
                ha=ha, va='bottom', fontsize=9, color=color_flops)

# Plot DRAM BW data points
ax.scatter(dram_bw['year'], dram_bw['value'], color=color_dram, s=80, zorder=5)
for i, name in enumerate(dram_bw['name']):
    y_offset = 1.3
    ax.annotate(name, (dram_bw['year'][i], dram_bw['value'][i] * y_offset),
                ha='center', va='bottom', fontsize=9, color=color_dram)

# Plot Interconnect BW data points
ax.scatter(interconnect_bw['year'], interconnect_bw['value'], color=color_interconnect, s=80, zorder=5)
for i, name in enumerate(interconnect_bw['name']):
    y_offset = 1.3
    ax.annotate(name, (interconnect_bw['year'][i], interconnect_bw['value'][i] * y_offset),
                ha='center', va='bottom', fontsize=9, color=color_interconnect)

# Fit and plot trend lines
def fit_trend(years, values):
    """Fit exponential trend line to data."""
    log_values = np.log10(values)
    slope, intercept, *_ = stats.linregress(years, log_values)
    return slope, intercept

# Trend line for HW FLOPS
slope_flops, intercept_flops = fit_trend(hw_flops['year'], hw_flops['value'])
x_trend = np.linspace(2005, 2026, 100)
y_trend_flops = 10 ** (intercept_flops + slope_flops * x_trend)
ax.plot(x_trend, y_trend_flops, color=color_flops, linewidth=3, alpha=0.7, zorder=1)

# Trend line for DRAM BW
slope_dram, intercept_dram = fit_trend(dram_bw['year'], dram_bw['value'])
y_trend_dram = 10 ** (intercept_dram + slope_dram * x_trend)
ax.plot(x_trend, y_trend_dram, color=color_dram, linewidth=3, alpha=0.5, zorder=1)
ax.fill_between(x_trend, y_trend_dram * 0.5, y_trend_dram * 2, color=color_dram, alpha=0.15, zorder=0)

# Trend line for Interconnect BW
slope_inter, intercept_inter = fit_trend(interconnect_bw['year'], interconnect_bw['value'])
y_trend_inter = 10 ** (intercept_inter + slope_inter * x_trend)
ax.plot(x_trend, y_trend_inter, color=color_interconnect, linewidth=3, alpha=0.5, zorder=1)
ax.fill_between(x_trend, y_trend_inter * 0.5, y_trend_inter * 2, color=color_interconnect, alpha=0.15, zorder=0)

# Calculate scaling factors for legend
# Over 20 years, what's the multiplier?
flops_20yr = 10 ** (slope_flops * 20)
dram_20yr = 10 ** (slope_dram * 20)
inter_20yr = 10 ** (slope_inter * 20)

# Per 2 years multiplier
flops_2yr = 10 ** (slope_flops * 2)
dram_2yr = 10 ** (slope_dram * 2)
inter_2yr = 10 ** (slope_inter * 2)

# Add legend text in upper left
legend_text = (
    f"HW FLOPS:           {flops_20yr:.0f}x / 20 yrs ({flops_2yr:.1f}x/2yrs)\n"
    f"DRAM BW:            {dram_20yr:.0f}x / 20 yrs ({dram_2yr:.1f}x/2yrs)\n"
    f"Interconnect BW:   {inter_20yr:.0f}x / 20 yrs ({inter_2yr:.1f}x/2yrs)"
)

# Create colored legend manually
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

# Set log scale for y-axis
ax.set_yscale('log')

# Configure axes
ax.set_xlim(2004, 2026)
ax.set_ylim(0.01, 10000000)

# Set y-ticks
yticks = [0.01, 0.1, 1, 10, 100, 1000, 10000, 100000, 1000000]
ax.set_yticks(yticks)
ax.set_yticklabels(['0.01', '0.1', '1', '10', '100', '1000', '10000', '100000', '1000000'])

# Set x-ticks
xticks = [2005, 2008, 2011, 2014, 2017, 2020, 2023, 2026]
ax.set_xticks(xticks)

# Grid
ax.grid(True, which='major', axis='both', linestyle='-', alpha=0.3, color=COLORS['grid'])
ax.grid(True, which='minor', axis='y', linestyle='-', alpha=0.15, color=COLORS['grid'])

# Remove top and right spines
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)
ax.spines['top'].set_color(COLORS['border'])
ax.spines['right'].set_color(COLORS['border'])

plt.tight_layout()

# Save the figure
save_figure(fig, 'hardware-scaling')

print("Plot saved to figures/generated/hardware-scaling.svg and .png")
plt.close()
