"""
Demodulation Reference Signals (DMRS) and Reference Signal Base Classes
"""

from dataclasses import dataclass
import numpy as np
from typing import List
from ..channel_types import ChannelType
from ..modulation import ModulationType, generate_random_symbols
from ..definitions import MAX_DMRS_RE

def generate_gold_sequence(c_init: int) -> np.ndarray:
    """
    Generate Gold sequence
    
    Args:
        c_init: 31-bit initialization value
        
    Returns:
        Binary sequence (0s and 1s)
    """
    # Initialize x1 sequence
    x1_init = np.array([1] + [0]*30)
    x1 = x1_init.copy()
    
    # Initialize x2 sequence from c_init
    x2_init = np.zeros(31)
    for ii in range(31):
        x2_init[ii] = (c_init >> ii) & 1
    x2 = x2_init.copy()
    
    # Generate sequences (optimized with pre-allocation)
    MPN = (2**16) - 1
    x1 = np.zeros(31 + MPN, dtype=int)
    x2 = np.zeros(31 + MPN, dtype=int)
    
    # Copy initial values
    x1[:31] = x1_init
    x2[:31] = x2_init
    
    # Generate sequences using vectorized operations where possible
    for n in range(MPN):
        x1[n + 31] = (x1[n + 3] + x1[n]) % 2
        x2[n + 31] = (x2[n + 3] + x2[n + 2] + x2[n + 1] + x2[n]) % 2
    
    # Generate c sequence with NC offset
    NC = 1600
    c = (x1[NC:NC + MPN - NC] + x2[NC:NC + MPN - NC]) % 2
    
    return c

def map_to_qpsk(c: np.ndarray, n_symbols: int) -> np.ndarray:
    """
    Map binary sequence to QPSK symbols (optimized)
    
    Args:
        c: Binary sequence (0s and 1s)
        n_symbols: Number of QPSK symbols to generate
        
    Returns:
        Complex QPSK symbols
    """

    real_bits = c[0:2*n_symbols:2]
    imag_bits = c[1:2*n_symbols:2]
    
    real_part = (1 - 2*real_bits) / np.sqrt(2)
    imag_part = (1 - 2*imag_bits) / np.sqrt(2)
    
    return real_part + 1j * imag_part

@dataclass
class ReferenceSignal:
    """Base class for all reference signals"""
    positions: List[int]
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

        if positions is None:
            positions = [0, 2, 4, 6, 8, 10]
        super().__init__(
            positions=positions,
            channel_type=ChannelType.DL_DMRS
        )
    
    def generate_symbols(self, num_rb: int, num_symbols: int, 
                        cell_id: int, slot_idx: int, symbol_idx: int) -> np.ndarray:
        """
        Generate PDSCH DMRS symbols
        
        Args:
            num_rb: Number of resource blocks
            num_symbols: Number of symbols
            cell_id: Cell ID
            slot_idx: Slot index
            symbol_idx: Symbol index within slot
            
        Returns:
            Complex DMRS symbols
        """
        # Calculate c_init
        c_init = ((2**17) * (14*slot_idx + symbol_idx + 1) * 
                  (2*cell_id + 1) + 2*cell_id) % (2**31)
        
        c = generate_gold_sequence(c_init)

        # Map to QPSK symbols: NoDMRSRE = 3276//2 = 1638
        NoDMRSRE = 3276 // 2  # Max number of DMRS REs in one symbol
        dmrs_symbols = map_to_qpsk(c, NoDMRSRE)

        # Return as column vector (n_sc, 1)
        return dmrs_symbols.reshape(-1, 1)

