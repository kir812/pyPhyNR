"""
Physical Downlink Shared Channel (PDSCH)
"""

from dataclasses import dataclass, field
import numpy as np
from typing import List
from ..channel_types import ChannelType
from . import PhysicalChannel
from ..resources import ResourceAllocation
from ..modulation import ModulationType, generate_random_symbols
from ..definitions import N_SC_PER_RB

@dataclass
class PDSCH(PhysicalChannel):
    """Physical Downlink Shared Channel"""
    data: np.ndarray = field(init=False)  # Complex symbols for transmission

    def __init__(self, start_rb: int, num_rb: int, start_symbol: int, num_symbols: int, slot: int, 
                 modulation: ModulationType = ModulationType.QPSK):
        # PDSCH allocation
        pdsch_allocation = ResourceAllocation(
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot=slot,
            channel_type=ChannelType.PDSCH
        )

        n_sc = num_rb * N_SC_PER_RB  # number of subcarriers
        self.data = generate_random_symbols(n_sc, num_symbols, modulation)

        super().__init__(ChannelType.PDSCH, [pdsch_allocation])
        # PDSCH-specific parameters
        self.dmrs_config = None  # To be implemented