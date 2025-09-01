"""
Physical Downlink Shared Channel (PDSCH)
"""

import numpy as np
from ..channel_types import ChannelType
from .base import PhysicalChannel
from ..modulation import ModulationType, generate_random_symbols
from ..definitions import N_SC_PER_RB
from .dmrs import PDSCH_DMRS

class PDSCH(PhysicalChannel):
    """Physical Downlink Shared Channel"""
    def __init__(self, start_rb: int, num_rb: int, start_symbol: int, num_symbols: int, 
                 slot_pattern: list[int], modulation: ModulationType = ModulationType.QPSK,
                 dmrs_positions: list[int] = None, cell_id: int = 0, power: float = 0.0,
                 rnti: int = 0, payload_pattern: str = "0"):
        super().__init__(
            channel_type=ChannelType.PDSCH,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            reference_signal=PDSCH_DMRS(positions=dmrs_positions),
            power=power,
            rnti=rnti,
            payload_pattern=payload_pattern
        )
        self.modulation = modulation
        self.cell_id = cell_id

        # Generate symbols
        self._generate_data()

    def _generate_data(self):
        """Generate PDSCH data with DMRS integration exactly matching MATLAB reference"""
        n_sc = self.num_rb * N_SC_PER_RB
        
        # Initialize data and channel type arrays
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
        self.channel_types = np.full((n_sc, self.num_symbols), self.channel_type, dtype=object)
        
        # Generate modulated symbols using the modulation type specified in constructor
        self.data = generate_random_symbols(n_sc, self.num_symbols, self.modulation)
        self.channel_types = np.full((n_sc, self.num_symbols), self.channel_type, dtype=object)
        
        # Then place DMRS in specific symbols, KEEPING data on odd subcarriers (like reference)
        if self.reference_signal:
            dmrs_symbols = set(self.reference_signal.positions)
            for sym in dmrs_symbols:
                if sym < self.num_symbols:
                    # Generate DMRS for this specific symbol (like reference)
                    # Reference: slot_num = iSmb // 14 where iSmb = slot_start + sym
                    # For our case, we need to calculate the actual slot number
                    slot_start = min(self.slot_pattern)  # Get the starting slot
                    slot_num = slot_start  # This should be 0 for the first slot
                    dmrs_data = self.reference_signal.generate_symbols(
                        num_rb=self.num_rb,
                        num_symbols=1,  # Only 1 symbol
                        cell_id=self.cell_id,
                        slot_idx=slot_num,
                        symbol_idx=sym
                    )
                    
                    # Insert DMRS on even subcarriers, KEEP data on odd subcarriers (like reference)
                    dmrs_length = min(len(dmrs_data), n_sc // 2)
                    self.data[::2, sym] = dmrs_data[:dmrs_length, 0]  # Even subcarriers get DMRS
                    # Odd subcarriers keep their original PDSCH data values
                    
                    # Mark even subcarriers as DMRS
                    for sc in range(0, n_sc, 2):
                        if sc < n_sc:
                            self.channel_types[sc, sym] = ChannelType.DL_DMRS

    def get_re_mapping(self):
        """Get RE mapping using pre-computed channel types"""
        from ..re_mapping import REMapping
        
        mappings = {}
        
        for slot in self.slot_pattern:
            slot_mappings = []
            time_indices = self.time_indices[slot]
            
            for i in self.freq_indices:
                for j in time_indices:
                    local_i = i - min(self.freq_indices)
                    local_j = j - min(time_indices)
                    
                    # Use pre-computed channel type instead of base class channel_type
                    ch_type = self.channel_types[local_i, local_j]
                    
                    mapping = REMapping(
                        subcarrier=i,
                        symbol=j,
                        data=self.data[local_i, local_j],
                        channel_type=ch_type
                    )
                    slot_mappings.append(mapping)
            
            mappings[slot] = slot_mappings
        
        return mappings
