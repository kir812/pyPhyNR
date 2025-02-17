"""
5G NR Physical Channels and Signals
"""

from dataclasses import dataclass
from typing import List
from ..types import ChannelType
from ..resources import ResourceAllocation

@dataclass
class PhysicalChannel:
    """Base class for all physical channels"""
    channel_type: ChannelType
    allocations: List[ResourceAllocation]

from .pdsch import PDSCH
from .pdcch import PDCCH
from .dmrs import DMRS

__all__ = [
    'PhysicalChannel',
    'PDSCH',
    'PDCCH',
    'DMRS'
] 