from dataclasses import dataclass, field
from .channel_types import ChannelType
import numpy as np
from .definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT
from .channels.pdsch import PDSCH
from .numerology import NRNumerology
from .channels.base import PhysicalChannel  # For type hints only

@dataclass
class ResourceElement:
    """Single Resource Element in 5G NR grid"""
    channel_type: ChannelType = ChannelType.EMPTY
    data: complex = 0+0j

@dataclass
class ResourceGrid:
    """2D Resource Grid for 5G NR"""
    n_subcarriers: int  # Y-axis
    n_symbols: int  # X-axis
    grid: np.ndarray = field(init=False)  # Array of ResourceElements

    def __post_init__(self):
        self.grid = np.array([[ResourceElement() for _ in range(self.n_symbols)]
                             for _ in range(self.n_subcarriers)], dtype=object)

    def add_channel(self, channel: PhysicalChannel):
        """Add a physical channel to the grid"""
        start_sc = channel.start_rb * N_SC_PER_RB
        end_sc = start_sc + channel.num_rb * N_SC_PER_RB
        start_sym = channel.start_symbol + channel.slot * N_SYMBOLS_PER_SLOT
        end_sym = start_sym + channel.num_symbols

        for i in range(start_sc, end_sc):
            for j in range(start_sym, end_sym):
                self.grid[i,j].channel_type = channel.channel_type
                if hasattr(channel, 'data'):
                    self.grid[i,j].data = channel.data[i-start_sc, j-start_sym]

    @property
    def channel_types(self):
        """Get array of channel types for plotting"""
        return np.array([[re.channel_type for re in row] for row in self.grid])

    @property
    def values(self):
        """Get array of complex values"""
        return np.array([[re.data for re in row] for row in self.grid])

    def add_pdsch(self, pdsch: PDSCH):
        """Add PDSCH to grid"""
        for i, j in np.ndindex(pdsch.symbols.shape):
            self.grid[pdsch.indices[0].start + i, 
                     pdsch.indices[1].start + j].channel_type = ChannelType.PDSCH
            self.grid[pdsch.indices[0].start + i,
                     pdsch.indices[1].start + j].data = pdsch.symbols[i,j]