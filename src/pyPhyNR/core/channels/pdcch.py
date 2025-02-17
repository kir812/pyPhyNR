"""
Physical Downlink Control Channel (PDCCH)
"""

from dataclasses import dataclass
from typing import List
from . import PhysicalChannel, ChannelType
from ..resources import ResourceAllocation

@dataclass
class PDCCH(PhysicalChannel):
    """Physical Downlink Control Channel"""
    def __init__(self, allocations: List[ResourceAllocation]):
        super().__init__(ChannelType.PDCCH, allocations)
        # PDCCH-specific parameters
        self.coreset_config = None  # To be implemented 