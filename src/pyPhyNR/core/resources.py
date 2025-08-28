from dataclasses import dataclass, field
from .channel_types import ChannelType
import numpy as np
from .channels.base import PhysicalChannel
from .channels.ssblock import SSBlock

@dataclass
class ResourceElement:
    """Single Resource Element in 5G NR grid"""
    channel: PhysicalChannel = None  # Reference to the channel that owns this RE
    
    @property
    def channel_type(self) -> ChannelType:
        """Get channel type of this RE"""
        if not self.channel:
            return ChannelType.EMPTY
            
        # Check if this RE is a DMRS position
        if isinstance(self.channel, SSBlock):
            # For SSBlock, check the internal bitmap
            sc = self.re_idx
            sym = self.sym_idx
            if self.channel.re_bitmap[sc, sym] == 3:  # 3 = PBCH DMRS in SSBlock
                return ChannelType.DL_DMRS
        elif self.channel.reference_signal and self.re_idx % 12 in self.channel.reference_signal.positions:
            return ChannelType.DL_DMRS
            
        return self.channel.channel_type
    
    @property
    def data(self) -> complex:
        """Get data value for this RE"""
        return 0+0j if self.channel is None else self.channel.data[self.re_idx, self.sym_idx]
    
    def __init__(self):
        self.channel = None
        self.re_idx = 0  # Index within channel's data array
        self.sym_idx = 0

    def can_add_channel(self, new_channel: PhysicalChannel) -> bool:
        """Check if a new channel can be added to this RE"""
        if self.channel is None:
            return True
        # PDCCH can be added on top of CORESET
        if new_channel.channel_type == ChannelType.PDCCH and self.channel_type == ChannelType.CORESET:
            return True
        return False

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
        # For each slot in the pattern
        for slot in channel.slot_pattern:
            time_indices = channel.time_indices[slot]

            # Check for conflicts
            for i in channel.freq_indices:
                for j in time_indices:
                    re = self.grid[i, j]
                    if not re.can_add_channel(channel):
                        existing_type = re.channel_type if re.channel else "EMPTY"
                        raise ValueError(f"Cannot add {channel.channel_type} - resource at RB {i//12}, symbol {j} already occupied by {existing_type}")

            # If no conflicts, add the channel
            for i in channel.freq_indices:
                for j in time_indices:
                    re = self.grid[i, j]
                    re.channel = channel
                    re.re_idx = i - min(channel.freq_indices)
                    re.sym_idx = j - min(time_indices)

    @property
    def channel_types(self):
        """Get array of channel types for plotting"""
        return np.array([[re.channel_type for re in row] for row in self.grid])

    @property
    def values(self):
        """Get array of complex values"""
        return np.array([[re.data for re in row] for row in self.grid])