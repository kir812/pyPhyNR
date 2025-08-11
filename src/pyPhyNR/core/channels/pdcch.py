"""
Physical Downlink Control Channel (PDCCH)
"""

from dataclasses import dataclass
import numpy as np
from typing import List
from ..channel_types import ChannelType
from .base import PhysicalChannel
from ..signals.reference import DMRS
from ..modulation import ModulationType, generate_random_symbols
from ..definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT

# PDCCH DMRS positions within each REG (1 RB x 1 symbol)
DMRS_POSITIONS = [1, 5, 9]  # 0-based indexing
DATA_POSITIONS = [i for i in range(N_SC_PER_RB) if i not in DMRS_POSITIONS]

@dataclass
class PDCCH(PhysicalChannel):
    """
    Physical Downlink Control Channel
    
    Must be transmitted within CORESET region.
    Includes DMRS on specific RE positions.
    """
    def __init__(self, 
                 start_rb: int,
                 num_rb: int,
                 start_symbol: int,
                 num_symbols: int,
                 slot_pattern: list,
                 modulation: ModulationType = ModulationType.QPSK):
        
        super().__init__(
            channel_type=ChannelType.PDCCH,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            reference_signal=DMRS(positions=DMRS_POSITIONS)
        )
        
        self.modulation = modulation
        
        # Generate data
        self._generate_data()
    
    def _generate_data(self):
        """Generate PDCCH data"""
        n_sc = self.num_rb * N_SC_PER_RB
        # Initialize full data array
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
        
        # Generate and place DMRS if present
        dmrs_data = self._generate_reference_signal()
        
        # Generate and place PDCCH data
        n_data = self.num_rb * len(DATA_POSITIONS)
        pdcch_data = generate_random_symbols(n_data, self.num_symbols, self.modulation)
        
        # Place data in correct positions
        for rb in range(self.num_rb):
            rb_start = rb * N_SC_PER_RB
            
            # Place DMRS
            if dmrs_data is not None:
                for i, pos in enumerate(self.reference_signal.positions):
                    dmrs_idx = rb * len(self.reference_signal.positions) + i
                    for sym in range(self.num_symbols):
                        self.data[rb_start + pos, sym] = dmrs_data[dmrs_idx, sym]
            
            # Place PDCCH data
            for i, pos in enumerate(DATA_POSITIONS):
                data_idx = rb * len(DATA_POSITIONS) + i
                for sym in range(self.num_symbols):
                    self.data[rb_start + pos, sym] = pdcch_data[data_idx, sym]

    def calculate_indices(self):
        """Calculate indices for both data and DMRS positions"""
        # Get all positions for each RB
        sc_indices = []
        for rb in range(self.num_rb):
            rb_start = (self.start_rb + rb) * N_SC_PER_RB
            # Add all positions (both data and DMRS)
            sc_indices.extend([rb_start + pos for pos in range(N_SC_PER_RB)])
        
        self.freq_indices = sc_indices
        
        # Time indices remain the same as parent class
        self.time_indices = {}
        for slot in self.slot_pattern:
            start_sym = self.start_symbol + slot * N_SYMBOLS_PER_SLOT
            end_sym = start_sym + self.num_symbols
            self.time_indices[slot] = range(start_sym, end_sym)