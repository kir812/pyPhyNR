from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np
from .channel_types import ChannelType

@dataclass
class ResourceElement:
    """Single Resource Element in 5G NR grid"""
    subcarrier: int  # Absolute subcarrier index in grid
    symbol: int      # Absolute symbol index in grid
    channel_type: ChannelType = ChannelType.EMPTY  # Type of channel occupying this RE
    data: complex = 0+0j  # Complex data value for this RE
    
    def can_add_channel(self, new_channel) -> bool:
        """Check if a new channel can be added to this RE"""
        if self.channel_type == ChannelType.EMPTY:
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
        # Initialize grid with empty REs, each knowing its position
        self.grid = np.array([[ResourceElement(subcarrier=sc, symbol=sym) 
                              for sym in range(self.n_symbols)]
                             for sc in range(self.n_subcarriers)], dtype=object)

    def add_channel(self, channel):
        """Add a physical channel to the grid"""
        # Get channel's RE mapping
        re_mapping = channel.get_re_mapping()
        
        # Check for conflicts first
        for slot, mappings in re_mapping.items():
            for mapping in mappings:
                re = self.grid[mapping.subcarrier, mapping.symbol]
                if not re.can_add_channel(channel):
                    raise ValueError(f"Cannot add {channel.channel_type} - resource at RB {mapping.subcarrier//12}, symbol {mapping.symbol} already occupied by {re.channel_type}")
        
        # Then add channel data
        for slot, mappings in re_mapping.items():
            for mapping in mappings:
                re = self.grid[mapping.subcarrier, mapping.symbol]
                re.data = mapping.data
                re.channel_type = mapping.channel_type

    @property
    def channel_types(self):
        """Get array of channel types for plotting"""
        return np.array([[re.channel_type for re in row] for row in self.grid])

    @property
    def values(self):
        """Get array of complex values"""
        return np.array([[re.data for re in row] for row in self.grid])