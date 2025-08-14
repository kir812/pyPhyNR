"""
Plotting utilities for 5G NR visualizations
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from ..core.carrier import CarrierConfig
from ..core.definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT
from ..core.channel_types import ChannelType
from matplotlib.patches import Patch
from ..core.resources import ResourceGrid

# Downlink channel colors
DL_CHANNEL_COLORS = {
    ChannelType.EMPTY: 'white',
    # Downlink Channels
    ChannelType.PDSCH: 'blue',
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
    ChannelType.EMPTY: 'white',
    # Uplink Channels
    ChannelType.PUSCH: 'blue',
    ChannelType.PUCCH: 'orange',
    ChannelType.PRACH: 'red',
    # Reference Signals
    ChannelType.UL_DMRS: 'yellow',
    ChannelType.UL_PTRS: 'purple',
    ChannelType.SRS: 'magenta'
}

def plot_grid_dl(carrier: CarrierConfig, grid: ResourceGrid):
    """Plot downlink resource grid"""
    return _plot_frame(carrier, grid, DL_CHANNEL_COLORS, "Downlink")

def plot_grid_ul(grid: ResourceGrid):
    """
    Plot uplink frame of the resource grid
    
    Args:
        grid: Resource grid to plot
    """
    return _plot_frame(grid, UL_CHANNEL_COLORS, "Uplink")

def _plot_frame(carrier: CarrierConfig, grid: ResourceGrid, channel_colors: dict, direction: str):
    """Internal plotting function"""
    total_symbols = grid.n_symbols
    total_subcarriers = grid.n_subcarriers

    # Create colormap from the colors
    colors = ['white'] * (max(ch.value for ch in ChannelType) + 1)
    for ch_type in channel_colors.keys():
        colors[ch_type.value] = channel_colors[ch_type]
    custom_cmap = ListedColormap(colors)

    fig, ax = plt.subplots(figsize=(22, 10))

    # Get channel types array from ResourceGrid
    grid_values = np.array([[ch_type.value for ch_type in row] 
                           for row in grid.channel_types])

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
        f'μ={carrier.numerology.mu}, '
        f'RB={carrier.n_resource_blocks} ({grid.n_subcarriers} subcarriers), '
        f'SCS={carrier.subcarrier_spacing}kHz'
    )

    # Add labels
    ax.set_ylabel('Subcarriers (RE)')
    ax.set_xlabel('OFDM Symbols')

    symbol_step = N_SYMBOLS_PER_SLOT  # Show one number per slot
    selected_symbols = np.arange(0, total_symbols, symbol_step)
    ax.set_xticks(selected_symbols)
    ax.set_xticklabels(selected_symbols)

    legend_elements = [
        Patch(facecolor=channel_colors[ch_type], label=ch_type.name)
        for ch_type in channel_colors.keys()  # Only use channels defined in the color map
    ]

    ax.legend(handles=legend_elements, 
             bbox_to_anchor=(1.05, 1),
             loc='upper left',
             borderaxespad=0.)

    plt.tight_layout()
    plt.subplots_adjust(right=0.85)

    plt.show()

def plot_constellation(*symbols, labels=None, title: str = "Constellation Diagram"):
    """
    Plot constellation diagram for multiple sets of complex values
    
    Args:
        *symbols: One or more arrays of complex values
        labels: List of labels for each symbol set
        title: Plot title
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    if labels is None:
        labels = [f"Channel {i+1}" for i in range(len(symbols))]
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(symbols)))  # Get different colors
    
    for values, label, color in zip(symbols, labels, colors):
        ax.scatter(np.real(values), np.imag(values), 
                  alpha=0.5, label=label, color=color)
    
    ax.grid(True)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
    ax.set_title(title)
    ax.set_xlabel('Real')
    ax.set_ylabel('Imaginary')
    ax.set_aspect('equal')
    plt.show()


# Waveform visualization functions
def plot_time_domain(waveform: np.ndarray, carrier_config: CarrierConfig, title: str = "Time Domain Signal"):
    """
    Plot time domain representation of the waveform
    
    Args:
        waveform: Complex IQ samples
        carrier_config: Carrier configuration (contains sample rate)
        title: Plot title
    """
    time_axis = np.arange(len(waveform)) / carrier_config.sample_rate * 1000  # Convert to ms
    
    plt.figure(figsize=(12, 8))

    # Plot magnitude
    plt.subplot(2, 1, 1)
    plt.plot(time_axis, np.abs(waveform))
    plt.title(f"{title} - Magnitude")
    plt.xlabel("Time (ms)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    # Plot phase
    # plt.subplot(2, 1, 2)
    # plt.plot(time_axis, np.angle(waveform, deg=True))
    # plt.title(f"{title} - Phase")
    # plt.xlabel("Time (ms)")
    # plt.ylabel("Phase (degrees)")
    # plt.grid(True)

    plt.tight_layout()
    plt.show()


def plot_frequency_domain(waveform: np.ndarray, carrier_config: CarrierConfig, title: str = "Frequency Domain"):
    """
    Plot frequency domain representation of the waveform
    
    Args:
        waveform: Complex IQ samples
        carrier_config: Carrier configuration (contains sample rate)
        title: Plot title
    """
    # Apply windowing to reduce spectral leakage
    window = np.hanning(len(waveform))
    windowed_signal = waveform * window
    
    # FFT
    fft_result = np.fft.fftshift(np.fft.fft(windowed_signal))
    freq_axis = (np.fft.fftfreq(len(waveform), 1/carrier_config.sample_rate)) / 1e6  # Convert to MHz
    
    # Power spectral density
    psd = np.abs(fft_result)**2
    psd_db = 10 * np.log10(psd + 1e-12)  # Add small value to avoid log(0)
    
    plt.figure(figsize=(12, 6))
    plt.plot(freq_axis, psd_db)
    plt.title(f"{title} - Power Spectral Density")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power (dB)")
    plt.grid(True)
    plt.xlim(-carrier_config.sample_rate/2e6, carrier_config.sample_rate/2e6)  # Show full bandwidth
    plt.ylim(-40, 60)
    plt.tight_layout()
    plt.show()

