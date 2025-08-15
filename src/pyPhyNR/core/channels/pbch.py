"""
Physical Broadcast Channel (PBCH)
"""

import numpy as np
from ..channel_types import ChannelType
from .base import PhysicalChannel
from ..modulation import ModulationType, generate_random_symbols
from ..definitions import N_SC_PER_RB
from .dmrs import PBCH_DMRS

class PBCH(PhysicalChannel):
    """Physical Broadcast Channel"""
    
    def __init__(self, cell_id: int, start_rb: int, start_symbol: int, slot_pattern: list[int],
                 ssb_index: int = 0, half_frame: int = 0):
        # PBCH occupies 240 subcarriers (20 RBs) across 2 symbols
        num_rb = 20  # 240 subcarriers = 20 RBs
        num_symbols = 2  # PBCH occupies symbols 1 and 3
        
        super().__init__(
            channel_type=ChannelType.PBCH,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            reference_signal=PBCH_DMRS(cell_id=cell_id)
        )
        
        self.cell_id = cell_id
        self.ssb_index = ssb_index
        self.half_frame = half_frame
        self._generate_pbch_data()
    
    def _generate_pbch_data(self):
        """Generate PBCH data with DMRS integration"""
        n_sc = self.num_rb * N_SC_PER_RB  # 240 subcarriers
        # Initialize full data array
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
        
        # Generate and place DMRS if present
        if self.reference_signal:
            dmrs_data = self.reference_signal.generate_symbols(
                num_rb=self.num_rb,
                num_symbols=self.num_symbols,
                ssb_index=self.ssb_index,
                half_frame=self.half_frame
            )
        else:
            dmrs_data = None
        
        # Generate PBCH data symbols (QPSK modulation)
        pbch_data = generate_random_symbols(n_sc, self.num_symbols, ModulationType.QPSK)
        
        # Place data in correct positions
        for rb in range(self.num_rb):
            rb_start = rb * N_SC_PER_RB
            
            # Place DMRS
            if dmrs_data is not None and self.reference_signal:
                for i, pos in enumerate(self.reference_signal.positions):
                    dmrs_idx = rb * len(self.reference_signal.positions) + i
                    for sym in range(self.num_symbols):
                        self.data[rb_start + pos, sym] = dmrs_data[dmrs_idx, sym]
            
            # Place PBCH data (excluding DMRS positions)
            dmrs_positions = set(self.reference_signal.positions) if self.reference_signal else set()
            data_positions = [pos for pos in range(N_SC_PER_RB) if pos not in dmrs_positions]
            
            for i, pos in enumerate(data_positions):
                data_idx = rb * len(data_positions) + i
                for sym in range(self.num_symbols):
                    self.data[rb_start + pos, sym] = pbch_data[data_idx, sym]
