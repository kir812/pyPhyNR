"""
Demodulation Reference Signal (DMRS)
"""

from dataclasses import dataclass
from typing import List
from . import PhysicalChannel, ChannelType
from ..resources import ResourceAllocation

@dataclass
class DMRS(PhysicalChannel):
    """Demodulation Reference Signal"""
    def __init__(self, allocations: List[ResourceAllocation]):
        super().__init__(ChannelType.DMRS, allocations)
        # DMRS-specific parameters
        self.sequence_config = None  # To be implemented 