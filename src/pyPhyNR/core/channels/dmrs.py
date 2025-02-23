"""
Demodulation Reference Signals (DMRS)
"""

from dataclasses import dataclass
from typing import List
from . import PhysicalChannel
from ..channel_types import ChannelType

@dataclass
class DL_DMRS(PhysicalChannel):
    """Downlink Demodulation Reference Signal"""
    def __init__(self):
        super().__init__(ChannelType.DL_DMRS)
        # DL-DMRS specific parameters
        self.sequence_config = None  # To be implemented

@dataclass 
class UL_DMRS(PhysicalChannel):
    """Uplink Demodulation Reference Signal"""
    def __init__(self):
        super().__init__(ChannelType.UL_DMRS)
        # UL-DMRS specific parameters
        self.sequence_config = None  # To be implemented 