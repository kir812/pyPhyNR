"""
Primary Synchronization Signal (PSS)
"""

import numpy as np
from ..channel_types import ChannelType
from .base import PhysicalChannel
from ..definitions import N_SC_PER_RB

class PSS(PhysicalChannel):
    """Primary Synchronization Signal"""
    
    def __init__(self, cell_id: int, start_rb: int, start_symbol: int, slot_pattern: list[int]):
        # PSS occupies 127 subcarriers (approximately 10.6 RBs)
        num_rb = 11  # 127 subcarriers ≈ 11 RBs
        num_symbols = 1  # PSS occupies 1 symbol
        
        super().__init__(
            channel_type=ChannelType.PSS,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern
        )
        
        self.cell_id = cell_id
        self._generate_pss_sequence()
    
    def _generate_pss_sequence(self):
        """Generate PSS sequence based on TS 38.211"""
        # Extract N_cell_ID2 from cell ID
        n_cell_id2 = self.cell_id % 3
        
        # Generate m-sequence x(n) as per TS 38.211
        x = np.zeros(127 + 7, dtype=int)
        x[:7] = [0, 1, 1, 0, 1, 1, 1]  # Initial values
        
        # Generate m-sequence
        for n in range(7, 127 + 7):
            x[n] = (x[n-4] + x[n-7]) % 2
        
        # Generate PSS sequence
        pss_sequence = np.zeros(127, dtype=complex)
        for n in range(127):
            m = (n + 43 * n_cell_id2) % 127
            pss_sequence[n] = 1 - 2 * x[m + 1]  # BPSK modulation
        
        # PSS occupies 127 subcarriers, centered in the allocated RBs
        n_sc = self.num_rb * N_SC_PER_RB
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
        
        # Center the 127 PSS symbols in the allocated subcarriers
        start_sc = (n_sc - 127) // 2
        self.data[start_sc:start_sc + 127, 0] = pss_sequence
