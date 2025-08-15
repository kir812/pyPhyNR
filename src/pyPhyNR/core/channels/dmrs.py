"""
Demodulation Reference Signals (DMRS) and Reference Signal Base Classes
"""

from dataclasses import dataclass
import numpy as np
from typing import List
from ..channel_types import ChannelType
from ..modulation import ModulationType, generate_random_symbols

def generate_gold_sequence(c_init: int, length: int) -> np.ndarray:
    """
    Generate Gold sequence based on 31-bit LFSR as per TS 38.211
    
    Args:
        c_init: 31-bit initialization value
        length: Length of sequence to generate
        
    Returns:
        Binary sequence (0s and 1s)
    """
    # Initialize LFSR states
    x1 = np.zeros(31, dtype=int)
    x1[0] = 1  # First LFSR: x1(0) = 1, x1(n) = 0 for n = 1, 2, ..., 30
    
    x2 = np.zeros(31, dtype=int)
    # Second LFSR: initialize with c_init
    for i in range(31):
        x2[i] = (c_init >> i) & 1
    
    # Generate sequence with Nc = 1600 offset as per TS 38.211
    Nc = 1600
    total_length = Nc + length
    
    # Generate x1 sequence: x1(n+31) = x1(n+3) + x1(n)
    for n in range(31, total_length):
        x1_new = (x1[n-28] + x1[n-31]) % 2
        x1 = np.append(x1, x1_new)
    
    # Generate x2 sequence: x2(n+31) = x2(n+3) + x2(n+2) + x2(n+1) + x2(n)
    for n in range(31, total_length):
        x2_new = (x2[n-28] + x2[n-29] + x2[n-30] + x2[n-31]) % 2
        x2 = np.append(x2, x2_new)
    
    # Gold sequence: c(n) = (x1(n+Nc) + x2(n+Nc)) mod 2
    gold_seq = (x1[Nc:Nc+length] + x2[Nc:Nc+length]) % 2
    
    return gold_seq

def map_to_qpsk(binary_seq: np.ndarray) -> np.ndarray:
    """
    Map binary sequence to QPSK symbols as per TS 38.211
    
    Args:
        binary_seq: Binary sequence (0s and 1s)
        
    Returns:
        Complex QPSK symbols
    """
    # Ensure even length
    if len(binary_seq) % 2 != 0:
        raise ValueError("Binary sequence length must be even for QPSK mapping")
    
    # Split into m1 and m2
    m1 = binary_seq[::2]  # Even indices
    m2 = binary_seq[1::2]  # Odd indices
    
    # QPSK mapping: 1/sqrt(2) * (1-2*m1 + j*(1-2*m2))
    qpsk_symbols = (1/np.sqrt(2)) * ((1 - 2*m1) + 1j * (1 - 2*m2))
    
    return qpsk_symbols

@dataclass
class ReferenceSignal:
    """Base class for all reference signals"""
    positions: List[int]  # RE positions within RB
    channel_type: ChannelType
    
    def generate_symbols(self, num_rb: int, num_symbols: int) -> np.ndarray:
        """Generate reference signal symbols"""
        n_positions = len(self.positions)
        n_sc = num_rb * n_positions
        return generate_random_symbols(n_sc, num_symbols, ModulationType.QPSK)

@dataclass
class DMRS(ReferenceSignal):
    """Demodulation Reference Signal"""
    def __init__(self, positions: List[int]):
        super().__init__(
            positions=positions,
            channel_type=ChannelType.DL_DMRS
        )

@dataclass
class PDSCH_DMRS(ReferenceSignal):
    """PDSCH-specific Demodulation Reference Signal"""
    def __init__(self, positions: List[int] = None):
        # Default PDSCH DMRS positions (type 1, single symbol)
        if positions is None:
            positions = [0, 2, 4, 6, 8, 10]  # Every other subcarrier
        super().__init__(
            positions=positions,
            channel_type=ChannelType.DL_DMRS
        )
    
    def generate_symbols(self, num_rb: int, num_symbols: int, 
                        cell_id: int, slot_idx: int, symbol_idx: int) -> np.ndarray:
        """
        Generate PDSCH DMRS symbols as per TS 38.211 Section 7.4.1.1.1
        
        Args:
            num_rb: Number of resource blocks
            num_symbols: Number of symbols
            cell_id: Cell ID
            slot_idx: Slot index
            symbol_idx: Symbol index within slot
            
        Returns:
            Complex DMRS symbols
        """
        n_positions = len(self.positions)
        n_sc = num_rb * n_positions
        
        # PDSCH DMRS initialization formula from TS 38.211
        c_init = (2**17 * (14 * slot_idx + symbol_idx + 1) * (2 * cell_id + 1) + 2 * cell_id) % (2**31)
        
        # Generate Gold sequence for all symbols
        total_binary_symbols = n_sc * num_symbols * 2  # *2 for QPSK mapping
        binary_seq = generate_gold_sequence(c_init, total_binary_symbols)
        
        # Map to QPSK symbols
        qpsk_symbols = map_to_qpsk(binary_seq)
        
        # Reshape to (n_sc, num_symbols)
        return qpsk_symbols.reshape(n_sc, num_symbols)

@dataclass
class PBCH_DMRS(ReferenceSignal):
    """PBCH-specific Demodulation Reference Signal"""
    def __init__(self, cell_id: int):
        # PBCH DMRS positions depend on cell ID
        v = cell_id % 4
        positions = [(i * 4 + v) % 12 for i in range(3)]  # 3 positions per RB
        super().__init__(
            positions=positions,
            channel_type=ChannelType.DL_DMRS
        )
        self.cell_id = cell_id
    
    def generate_symbols(self, num_rb: int, num_symbols: int, 
                        ssb_index: int = 0, half_frame: int = 0) -> np.ndarray:
        """
        Generate PBCH DMRS symbols as per TS 38.211 Section 7.4.1.1.2
        
        Args:
            num_rb: Number of resource blocks
            num_symbols: Number of symbols
            ssb_index: SSB index
            half_frame: Half frame index (0 or 1)
            
        Returns:
            Complex DMRS symbols
        """
        n_positions = len(self.positions)
        n_sc = num_rb * n_positions
        
        # Calculate i_ssb based on SSB index and half frame
        if ssb_index <= 3:  # L_max <= 4
            i_ssb = ssb_index + 4 * half_frame
        else:  # L_max > 4
            i_ssb = ssb_index + 8 * half_frame
        
        # PBCH DMRS initialization formula from TS 38.211
        c_init = (2**11 * (i_ssb + 1) * (self.cell_id // 4 + 1) + 
                  2**6 * (i_ssb + 1) + self.cell_id % 4) % (2**31)
        
        # Generate Gold sequence for all symbols
        total_binary_symbols = n_sc * num_symbols * 2  # *2 for QPSK mapping
        binary_seq = generate_gold_sequence(c_init, total_binary_symbols)
        
        # Map to QPSK symbols
        qpsk_symbols = map_to_qpsk(binary_seq)
        
        # Reshape to (n_sc, num_symbols)
        return qpsk_symbols.reshape(n_sc, num_symbols)
