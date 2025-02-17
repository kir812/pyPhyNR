"""
Common types and enums for 5G NR
"""

from enum import Enum, auto

class ChannelType(Enum):
    """5G NR Physical Channel and Signal Types"""
    # Downlink Channels
    PDSCH = auto()    # Physical Downlink Shared Channel
    PDCCH = auto()    # Physical Downlink Control Channel
    PBCH = auto()     # Physical Broadcast Channel
    
    # Synchronization Signals
    PSS = auto()      # Primary Synchronization Signal
    SSS = auto()      # Secondary Synchronization Signal
    
    # Reference Signals
    DMRS = auto()     # Demodulation Reference Signal
    PTRS = auto()     # Phase Tracking Reference Signal
    CSI_RS = auto()   # Channel State Information Reference Signal
    
    EMPTY = auto()    # Unallocated 