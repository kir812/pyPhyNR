"""
Physical Downlink Shared Channel (PDSCH)
"""

import numpy as np
from ..channel_types import ChannelType
from .base import PhysicalChannel
from ..modulation import ModulationType, generate_random_symbols
from ..definitions import N_SC_PER_RB

class PDSCH(PhysicalChannel):
    """Physical Downlink Shared Channel"""
    def __init__(self, start_rb: int, num_rb: int, start_symbol: int, num_symbols: int, 
                 slot_pattern: list[int], modulation: ModulationType = ModulationType.QPSK):
        super().__init__(
            channel_type=ChannelType.PDSCH,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern
        )
        self.modulation = modulation

        # Generate symbols
        n_sc = self.num_rb * N_SC_PER_RB
        self.data = generate_random_symbols(n_sc, self.num_symbols, self.modulation)
