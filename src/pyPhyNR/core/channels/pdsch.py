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
        # Initialize full data array
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
        
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
            
            # Place DMRS
            if dmrs_data is not None and self.reference_signal:
                for i, pos in enumerate(self.reference_signal.positions):
                    dmrs_idx = rb * len(self.reference_signal.positions) + i
                    for sym in range(self.num_symbols):
                        self.data[rb_start + pos, sym] = dmrs_data[dmrs_idx, sym]
            
            # Place PDSCH data (excluding DMRS positions)
            dmrs_positions = set(self.reference_signal.positions) if self.reference_signal else set()
            data_positions = [pos for pos in range(N_SC_PER_RB) if pos not in dmrs_positions]
            
            for i, pos in enumerate(data_positions):
                data_idx = rb * len(data_positions) + i
                for sym in range(self.num_symbols):
                    self.data[rb_start + pos, sym] = pdsch_data[data_idx, sym]
