from dataclasses import dataclass, field
from .channel_types import ChannelType
import numpy as np
from .definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT

@dataclass
class ResourceElement:
    """Single Resource Element in 5G NR grid"""
    channel_type: ChannelType = ChannelType.EMPTY
    data: complex = 0+0j

@dataclass
class PhysicalChannel:
    """Base class for all physical channels"""
    channel_type: ChannelType
    start_rb: int
    num_rb: int
    start_symbol: int
    num_symbols: int
    slot: int
    data: np.ndarray = field(init=False)

@dataclass
class ResourceGrid:
    """2D Resource Grid for 5G NR"""
    n_subcarriers: int
    n_symbols: int
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