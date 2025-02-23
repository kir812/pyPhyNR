"""
Physical Downlink Shared Channel (PDSCH)
"""

from dataclasses import dataclass, field
import numpy as np
from ..channel_types import ChannelType
from .base import PhysicalChannel
from ..modulation import ModulationType, generate_random_symbols
from ..definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT


class PDSCH(PhysicalChannel):
    """Physical Downlink Shared Channel"""
    def __init__(self, start_rb: int, num_rb: int, start_symbol: int, num_symbols: int, slot: int, 
                 modulation: ModulationType = ModulationType.QPSK):
        self.start_rb = start_rb
        self.num_rb = num_rb
        self.start_symbol = start_symbol
        self.num_symbols = num_symbols
        self.slot = slot
        self.modulation = modulation
        # Generate symbols
        n_sc = self.num_rb * N_SC_PER_RB
        self.symbols = generate_random_symbols(n_sc, self.num_symbols, self.modulation)

        # Calculate indices
        start_sc = self.start_rb * N_SC_PER_RB
        end_sc = start_sc + self.num_rb * N_SC_PER_RB
        start_sym = self.start_symbol + self.slot * N_SYMBOLS_PER_SLOT
        end_sym = start_sym + self.num_symbols

        self.indices = (slice(start_sc, end_sc), slice(start_sym, end_sym))
