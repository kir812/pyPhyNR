from dataclasses import dataclass
from .channels import ChannelType

@dataclass
class ResourceElement:
    """Single Resource Element in 5G NR grid"""
    subcarrier: int      # Subcarrier index within the grid
    symbol: int          # OFDM symbol index
    slot: int            # Slot number
    channel_type: ChannelType = ChannelType.EMPTY
    value: complex = 0+0j

@dataclass
class ResourceAllocation:
    """Resource allocation in 5G NR grid"""
    start_rb: int        # Starting RB index
    num_rb: int          # Number of RBs
    start_symbol: int    # Starting symbol
    num_symbols: int     # Number of symbols
    slot: int            # Slot number
    channel_type: ChannelType
    pattern: str = 'full'  # 'full', 'scattered', etc. for different mapping patterns 