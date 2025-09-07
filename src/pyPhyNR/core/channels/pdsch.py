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
                 slot_pattern: list[int], modulation: ModulationType = ModulationType.QPSK,
                 cell_id: int = 0, power: float = 0.0,
                 rnti: int = 0, payload_pattern: str = "0", deterministic: bool = False):
        super().__init__(
            channel_type=ChannelType.PDSCH,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            reference_signal=None,  # No DMRS - will be added separately
            power=power,
            rnti=rnti,
            payload_pattern=payload_pattern
        )
        self.modulation = modulation
        self.cell_id = cell_id

        # Generate symbols
        self._generate_data(deterministic=deterministic)

    def _generate_data(self, deterministic=False):
        """Generate PDSCH data
        
        Args:
            deterministic: If True, use deterministic pattern (for testing/debugging)
        """
        n_sc = self.num_rb * N_SC_PER_RB
        
        if deterministic:
            # Generate deterministic data for testing
            self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)
            for sym_idx in range(self.num_symbols):
                deterministic_bits = (np.arange(n_sc) + sym_idx * 7) % 64
                symbol_data = self._bits_to_symbols(deterministic_bits, self.modulation)
                self.data[:, sym_idx] = symbol_data
        else:
            # Generate random data (default)
            self.data = generate_random_symbols(n_sc, self.num_symbols, self.modulation)
        
        # Apply power scaling if specified
        if self.power != 0.0:
            self.data *= 10**(self.power/20)  # Convert dB to linear scale
    
    def _bits_to_symbols(self, bits, modulation):
        """Convert bits to symbols"""
        if modulation == ModulationType.QAM64:
            symbols = np.zeros(len(bits), dtype=complex)
            for i, val in enumerate(bits):
                # Extract bits
                b1 = (val >> 0) & 1  # LSB
                b2 = (val >> 1) & 1
                b3 = (val >> 2) & 1
                b4 = (val >> 3) & 1
                b5 = (val >> 4) & 1
                b6 = (val >> 5) & 1  # MSB
                symbols[i] = (1/np.sqrt(42)) * (
                    (1 - 2*b1) * (4 - (1-2*b3) * (2 - (1-2*b5))) +
                    1j * (1 - 2*b2) * (4 - (1-2*b4) * (2 - (1-2*b6)))
                )
            return symbols
        else:
            raise NotImplementedError(f"Modulation {modulation} not implemented")

    def get_re_mapping(self):
        """Get RE mapping - simplified approach"""
        from ..re_mapping import REMapping
        
        mappings = {}
        
        # Calculate subcarrier range
        start_sc = self.start_rb * N_SC_PER_RB
        end_sc = start_sc + (self.num_rb * N_SC_PER_RB)
        
        for slot in self.slot_pattern:
            slot_mappings = []
            
            # Calculate symbol range for this slot
            slot_start_sym = slot * 14 + self.start_symbol
            slot_end_sym = slot_start_sym + self.num_symbols
            
            # Create mappings for this slot
            for sc in range(start_sc, end_sc):
                for sym in range(slot_start_sym, slot_end_sym):
                    local_sc = sc - start_sc
                    local_sym = sym - slot_start_sym

                    mapping = REMapping(
                        subcarrier=sc,
                        symbol=sym,
                        data=self.data[local_sc, local_sym],
                        channel_type=self.channel_type
                    )
                    slot_mappings.append(mapping)
            
            mappings[slot] = slot_mappings
        
        return mappings
