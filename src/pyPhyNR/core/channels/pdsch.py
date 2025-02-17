"""
Physical Downlink Shared Channel (PDSCH)
"""

from dataclasses import dataclass
from typing import List
from ..types import ChannelType
from . import PhysicalChannel
from ..resources import ResourceAllocation

@dataclass
class PDSCH(PhysicalChannel):
    """Physical Downlink Shared Channel"""
    def __init__(self, allocations: List[ResourceAllocation]):
        super().__init__(ChannelType.PDSCH, allocations)
        # PDSCH-specific parameters
        self.dmrs_config = None  # To be implemented 