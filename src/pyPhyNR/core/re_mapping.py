"""
Resource Element mapping classes
"""

from dataclasses import dataclass
from .channel_types import ChannelType

@dataclass
class REMapping:
    """Mapping of a single Resource Element"""
    subcarrier: int  # Absolute subcarrier index
    symbol: int      # Absolute symbol index
    data: complex    # Complex data value
    channel_type: ChannelType  # Type of channel occupying this RE
