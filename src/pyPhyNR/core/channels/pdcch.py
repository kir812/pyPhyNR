"""
Physical Downlink Control Channel (PDCCH)
"""

from dataclasses import dataclass
from typing import List
from . import PhysicalChannel
from ..channel_types import ChannelType

@dataclass
class PDCCH(PhysicalChannel):
    """Physical Downlink Control Channel"""
    def __init__(self):
        super().__init__(ChannelType.PDCCHs)
        # PDCCH-specific parameters
        self.coreset_config = None  # To be implemented 