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
        """Generate PDSCH data with DMRS integration"""
        n_sc = self.num_rb * N_SC_PER_RB
        # Initialize data and channel type arrays
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
        self.channel_types = np.full((n_sc, self.num_symbols), self.channel_type, dtype=object)
        
        # Generate and place DMRS if present
        if self.reference_signal:
            # Calculate slot and symbol indices for DMRS generation
            slot_idx = self.slot_pattern[0]  # Use first slot for now
            symbol_idx = self.start_symbol
            
            dmrs_data = self.reference_signal.generate_symbols(
                num_rb=self.num_rb,
                num_symbols=self.num_symbols,
                cell_id=self.cell_id,
                slot_idx=slot_idx,
                symbol_idx=symbol_idx
            )
        else:
            dmrs_data = None
        
        # Generate PDSCH data symbols
        pdsch_data = generate_random_symbols(n_sc, self.num_symbols, self.modulation)
        
        # Place data in correct positions
        for rb in range(self.num_rb):
            rb_start = rb * N_SC_PER_RB
            
            # Place PDSCH data first (in all REs)
            for sc in range(N_SC_PER_RB):
                data_idx = rb * N_SC_PER_RB + sc
                for sym in range(self.num_symbols):
                    self.data[rb_start + sc, sym] = pdsch_data[data_idx, sym]
                    # All REs start as PDSCH
                    self.channel_types[rb_start + sc, sym] = self.channel_type
            
            # Then place DMRS in specific symbols and mark them
            if dmrs_data is not None and self.reference_signal:
                dmrs_symbols = set(self.reference_signal.positions)  # Now positions are symbol indices
                for sym in dmrs_symbols:
                    if sym < self.num_symbols:  # Only place DMRS if symbol is within our allocation
                        # Place DMRS on every other subcarrier (0, 2, 4, ...)
                        for sc_idx in range(N_SC_PER_RB // 2):  # 6 DMRS per RB
                            sc = 2 * sc_idx  # Convert to actual subcarrier index
                            dmrs_idx = rb * (N_SC_PER_RB // 2) + sc_idx  # Index into DMRS data
                            self.data[rb_start + sc, sym] = dmrs_data[dmrs_idx, 0]
                            # Mark this RE as DMRS
                            self.channel_types[rb_start + sc, sym] = ChannelType.DL_DMRS

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
