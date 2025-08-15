"""
Secondary Synchronization Signal (SSS)
"""

import numpy as np
from ..channel_types import ChannelType
from .base import PhysicalChannel
from ..definitions import N_SC_PER_RB

class SSS(PhysicalChannel):
    """Secondary Synchronization Signal"""
    
    def __init__(self, cell_id: int, start_rb: int, start_symbol: int, slot_pattern: list[int]):
        # SSS occupies 127 subcarriers (approximately 10.6 RBs)
        num_rb = 11  # 127 subcarriers ≈ 11 RBs
        num_symbols = 1  # SSS occupies 1 symbol
        
        super().__init__(
            channel_type=ChannelType.SSS,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern
        )
        
        self.cell_id = cell_id
        self._generate_sss_sequence()
    
    def _generate_sss_sequence(self):
        """Generate SSS sequence based on TS 38.211"""
        # Extract N_cell_ID1 and N_cell_ID2 from cell ID
        n_cell_id1 = self.cell_id // 3
        n_cell_id2 = self.cell_id % 3
        
        # Calculate m0 and m1 as per TS 38.211
        m0 = 15 * (n_cell_id1 // 112) + 5 * n_cell_id2
        m1 = n_cell_id1 % 112
        
        # Generate m-sequences x0(n) and x1(n)
        x0 = np.zeros(127 + 7, dtype=int)
        x1 = np.zeros(127 + 7, dtype=int)
        
        # Initial values
        x0[:7] = [1, 0, 0, 0, 0, 0, 0]
        x1[:7] = [1, 0, 0, 0, 0, 0, 0]
        
        # Generate m-sequences
        for n in range(7, 127 + 7):
            x0[n] = (x0[n-4] + x0[n-7]) % 2
            x1[n] = (x1[n-1] + x1[n-7]) % 2
        
        # Generate SSS sequence
        sss_sequence = np.zeros(127, dtype=complex)
        for n in range(127):
            x0_val = 1 - 2 * x0[(n + m0) % 127 + 1]
            x1_val = 1 - 2 * x1[(n + m1) % 127 + 1]
            sss_sequence[n] = x0_val * x1_val  # BPSK modulation
        
        # SSS occupies 127 subcarriers, centered in the allocated RBs
        n_sc = self.num_rb * N_SC_PER_RB
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
        
        # Center the 127 SSS symbols in the allocated subcarriers
        start_sc = (n_sc - 127) // 2
        self.data[start_sc:start_sc + 127, 0] = sss_sequence
