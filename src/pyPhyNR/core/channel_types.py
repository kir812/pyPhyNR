"""
Common types and enums for 5G NR
"""

from enum import Enum, auto

class ChannelType(Enum):
    """5G NR Physical Channel and Signal Types"""
    EMPTY = auto()    # Unallocated 

    # Downlink Channels
    PDSCH = auto()    # Physical Downlink Shared Channel
    PDCCH = auto()    # Physical Downlink Control Channel
    PBCH = auto()     # Physical Broadcast Channel
    CORESET = auto()  # Control Resource Set
    SS_BURST = auto() # SS/PBCH Block Repetition Burst

    # Uplink Channels
    PUSCH = auto()    # Physical Uplink Shared Channel
    PUCCH = auto()    # Physical Uplink Control Channel
    PRACH = auto()    # Physical Random Access Channel
    
    # Synchronization Signals (Downlink)
    PSS = auto()      # Primary Synchronization Signal
    SSS = auto()      # Secondary Synchronization Signal

    # Reference Signals
    ## Downlink Reference Signals
    DL_DMRS = auto()  # Downlink Demodulation Reference Signal
    DL_PTRS = auto()  # Downlink Phase Tracking Reference Signal
    CSI_RS = auto()   # Channel State Information Reference Signal
    
    ## Uplink Reference Signals
    UL_DMRS = auto()  # Uplink Demodulation Reference Signal
    UL_PTRS = auto()  # Uplink Phase Tracking Reference Signal
    SRS = auto()      # Sounding Reference Signal