"""
SS/PBCH Block (SSBlock) - Container for PSS, SSS, and PBCH
"""

import numpy as np
from typing import List
from ..channel_types import ChannelType
from .base import PhysicalChannel
from .pss import PSS
from .sss import SSS
from .pbch import PBCH
from ..definitions import N_SC_PER_RB

class SSBlock(PhysicalChannel):
    """
    SS/PBCH Block - Composite channel containing PSS, SSS, and PBCH
    
    Fixed dimensions: 240 subcarriers x 4 symbols
    Internal structure:
    - Symbol 0: PSS (127 subcarriers, centered)
    - Symbol 1: PBCH (240 subcarriers) + PBCH DMRS
    - Symbol 2: SSS (127 subcarriers, centered)  
    - Symbol 3: PBCH (240 subcarriers) + PBCH DMRS
    """
    
    def __init__(self, cell_id: int, start_rb: int, start_symbol: int, slot_pattern: list[int],
                 ssb_index: int = 0, half_frame: int = 0):
        # SSBlock has fixed dimensions: 240 subcarriers × 4 symbols
        num_rb = 20  # 240 subcarriers = 20 RBs
        num_symbols = 4  # SSBlock occupies 4 symbols
        
        super().__init__(
            channel_type=ChannelType.SS_BURST,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern
        )
        
        self.cell_id = cell_id
        self.ssb_index = ssb_index
        self.half_frame = half_frame
        
        # Create internal bitmap for RE placement
        self._create_internal_bitmap()
        
        # Create SSB components
        self._create_ssb_components()
        
        # Generate combined data
        self._generate_ssb_data()
    
    def _create_internal_bitmap(self):
        """Create internal bitmap for RE placement within SSBlock"""
        # Bitmap: 0=PBCH, 1=PSS, 2=SSS, 3=PBCH_DMRS
        self.re_bitmap = np.zeros((240, 4), dtype=int)
        
        # PSS: Symbol 0, subcarriers 56-182 (127 subcarriers, centered)
        pss_start = 56
        pss_end = 183
        self.re_bitmap[pss_start:pss_end, 0] = 1  # PSS
        
        # SSS: Symbol 2, subcarriers 56-182 (127 subcarriers, centered)
        self.re_bitmap[pss_start:pss_end, 2] = 2  # SSS
        
        # PBCH: Symbols 1 and 3, all 240 subcarriers
        self.re_bitmap[:, 1] = 0  # PBCH
        self.re_bitmap[:, 3] = 0  # PBCH
        
        # PBCH DMRS: Insert DMRS positions based on cell ID
        v = self.cell_id % 4
        for rb in range(20):  # 20 RBs
            rb_start = rb * 12
            for i in range(3):  # 3 DMRS positions per RB
                pos = (i * 4 + v) % 12
                sc_idx = rb_start + pos
                if sc_idx < 240:
                    self.re_bitmap[sc_idx, 1] = 3  # PBCH DMRS symbol 1
                    self.re_bitmap[sc_idx, 3] = 3  # PBCH DMRS symbol 3
    
    def _create_ssb_components(self):
        """Create individual SSB components"""
        # PSS: Symbol 0
        self.pss = PSS(
            cell_id=self.cell_id,
            start_rb=self.start_rb,
            start_symbol=self.start_symbol,
            slot_pattern=self.slot_pattern
        )
        
        # SSS: Symbol 2
        self.sss = SSS(
            cell_id=self.cell_id,
            start_rb=self.start_rb,
            start_symbol=self.start_symbol + 2,  # Symbol 2
            slot_pattern=self.slot_pattern
        )
        
        # PBCH: Symbols 1 and 3
        self.pbch = PBCH(
            cell_id=self.cell_id,
            start_rb=self.start_rb,
            start_symbol=self.start_symbol + 1,  # Symbol 1
            slot_pattern=self.slot_pattern,
            ssb_index=self.ssb_index,
            half_frame=self.half_frame
        )
    
    def _generate_ssb_data(self):
        """Generate combined SSB data from all components"""
        n_sc = self.num_rb * N_SC_PER_RB  # 240 subcarriers
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
        
        # Extract data from components and place according to bitmap
        for sc in range(n_sc):
            for sym in range(self.num_symbols):
                re_type = self.re_bitmap[sc, sym]
                
                if re_type == 1:  # PSS
                    # Map to PSS data (centered in 132 subcarriers)
                    pss_sc = sc - 56  # PSS starts at subcarrier 56
                    if 0 <= pss_sc < 127:
                        self.data[sc, sym] = self.pss.data[pss_sc, 0]
                
                elif re_type == 2:  # SSS
                    # Map to SSS data (centered in 132 subcarriers)
                    sss_sc = sc - 56  # SSS starts at subcarrier 56
                    if 0 <= sss_sc < 127:
                        self.data[sc, sym] = self.sss.data[sss_sc, 0]
                
                elif re_type == 0:  # PBCH
                    # Map to PBCH data
                    pbch_sym = sym - 1  # PBCH uses symbols 1 and 3
                    if pbch_sym >= 0 and pbch_sym < 2:
                        self.data[sc, sym] = self.pbch.data[sc, pbch_sym]
                
                elif re_type == 3:  # PBCH DMRS
                    # Map to PBCH DMRS data
                    pbch_sym = sym - 1  # PBCH uses symbols 1 and 3
                    if pbch_sym >= 0 and pbch_sym < 2:
                        # Find DMRS position within PBCH
                        rb = sc // 12
                        pos_in_rb = sc % 12
                        v = self.cell_id % 4
                        dmrs_positions = [(i * 4 + v) % 12 for i in range(3)]
                        
                        if pos_in_rb in dmrs_positions:
                            dmrs_idx = dmrs_positions.index(pos_in_rb)
                            self.data[sc, sym] = self.pbch.reference_signal.generate_symbols(1, 1)[dmrs_idx, 0]
