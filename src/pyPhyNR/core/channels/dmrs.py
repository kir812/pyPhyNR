"""
Demodulation Reference Signals (DMRS)
"""

from dataclasses import dataclass
from typing import List
from . import PhysicalChannel
from ..resources import ResourceAllocation, ChannelType

@dataclass
class DL_DMRS(PhysicalChannel):
    """Downlink Demodulation Reference Signal"""
    def __init__(self, allocations: List[ResourceAllocation]):
        super().__init__(ChannelType.DL_DMRS, allocations)
        # DL-DMRS specific parameters
        self.sequence_config = None  # To be implemented

@dataclass 
class UL_DMRS(PhysicalChannel):
    """Uplink Demodulation Reference Signal"""
    def __init__(self, allocations: List[ResourceAllocation]):
        super().__init__(ChannelType.UL_DMRS, allocations)
        # UL-DMRS specific parameters
        self.sequence_config = None  # To be implemented 