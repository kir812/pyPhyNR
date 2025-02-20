"""
Plotting utilities for 5G NR visualizations
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from ..core.carrier import CarrierConfig
from ..core.definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT, N_SUBFRAMES_PER_FRAME
from ..core.channel_types import ChannelType
from ..core.resources import ResourceElement
from matplotlib.patches import Patch

# Downlink channel colors
DL_CHANNEL_COLORS = {
    ChannelType.EMPTY: 'blue',
    # Downlink Channels
    ChannelType.PDSCH: 'cyan',
    ChannelType.PDCCH: 'orange',
    ChannelType.PBCH: 'green',
    ChannelType.CORESET: 'lime',
    ChannelType.SS_BURST: 'red',
    # Synchronization
    ChannelType.PSS: 'magenta',
    ChannelType.SSS: 'pink',
    # Reference Signals
    ChannelType.DL_DMRS: 'yellow',
    ChannelType.DL_PTRS: 'purple',
    ChannelType.CSI_RS: 'brown'
}

# Uplink channel colors
UL_CHANNEL_COLORS = {
    ChannelType.EMPTY: 'blue',
    # Uplink Channels
    ChannelType.PUSCH: 'cyan',
    ChannelType.PUCCH: 'orange',
    ChannelType.PRACH: 'red',
    # Reference Signals
    ChannelType.UL_DMRS: 'yellow',
    ChannelType.UL_PTRS: 'purple',
    ChannelType.SRS: 'magenta'
}

def plot_grid_dl(carrier_config: CarrierConfig):
    """
    Plot downlink frame of the resource grid
    
    Args:
        carrier_config: Carrier configuration
    """
    return _plot_frame(carrier_config, DL_CHANNEL_COLORS, "Downlink")

def plot_grid_ul(carrier_config: CarrierConfig):
    """
    Plot uplink frame of the resource grid
    
    Args:
        carrier_config: Carrier configuration
    """
    return _plot_frame(carrier_config, UL_CHANNEL_COLORS, "Uplink")

def _plot_frame(carrier_config: CarrierConfig, channel_colors: dict, direction: str):
    """Internal function for plotting resource grid"""
    # Calculate grid dimensions
    slots_per_subframe = carrier_config.numerology.slots_per_subframe
    total_slots = N_SUBFRAMES_PER_FRAME * slots_per_subframe
    total_symbols = total_slots * N_SYMBOLS_PER_SLOT
    total_subcarriers = carrier_config.n_size_grid * N_SC_PER_RB

    # Create colormap from the colors
    colors = ['white'] * (max(ch.value for ch in ChannelType) + 1)
    for ch_type in channel_colors.keys():
        colors[ch_type.value] = channel_colors[ch_type]
    custom_cmap = ListedColormap(colors)

    fig, ax = plt.subplots(figsize=(22, 10))
    
    # Get channel types array from ResourceGrid
    grid_values = np.array([[ch_type.value for ch_type in row] 
                           for row in carrier_config.resource_grid.channel_types])
    
    ax.imshow(grid_values, aspect='auto', interpolation='nearest', 
              cmap=custom_cmap, origin='lower', vmin=0, vmax=len(colors)-1)

    # Draw horizontal lines between RBs (every 12 subcarriers)
    for sc in range(0, total_subcarriers + 1, N_SC_PER_RB):
        ax.axhline(y=sc-0.5, color='black', linestyle='-', linewidth=1.0, alpha=0.8)

    # Draw vertical lines between slots (every 14 OFDM symbols)
    for symbol in range(0, total_symbols + 1, N_SYMBOLS_PER_SLOT):
        ax.axvline(x=symbol-0.5, color='black', linestyle='-', linewidth=1.0, alpha=0.8)

    ax.grid(False)

    ax.set_title(
        f'5G NR Resource Grid\n'
        f'μ={carrier_config.numerology.mu}, '
        f'RB={carrier_config.n_size_grid} ({total_subcarriers} subcarriers), '
        f'SCS={carrier_config.numerology.subcarrier_spacing}kHz'
    )

    # Add labels
    ax.set_ylabel('Subcarriers (RE)')
    ax.set_xlabel('OFDM Symbols')

    symbol_step = N_SYMBOLS_PER_SLOT  # Show one number per slot
    selected_symbols = np.arange(0, total_symbols, symbol_step)
    ax.set_xticks(selected_symbols)
    ax.set_xticklabels(selected_symbols)

    # Create legend patches only for channels in the color map
    legend_elements = [
        Patch(facecolor=channel_colors[ch_type], label=ch_type.name)
        for ch_type in channel_colors.keys()  # Only use channels defined in the color map
    ]
    
    # Add legend to the right of the plot
    ax.legend(handles=legend_elements, 
             bbox_to_anchor=(1.05, 1),
             loc='upper left',
             borderaxespad=0.)
    
    # Adjust layout to make room for legend
    plt.tight_layout()
    plt.subplots_adjust(right=0.85)

    plt.show()
    return grid_values 