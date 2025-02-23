"""Base class for physical channels"""

from dataclasses import dataclass, field
import numpy as np
from ..channel_types import ChannelType

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