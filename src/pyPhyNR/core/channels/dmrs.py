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
    Generate Gold sequence exactly matching MATLAB reference
    
    Args:
        c_init: 31-bit initialization value
        
    Returns:
        Binary sequence (0s and 1s)
    """
    # Initialize x1 sequence exactly as reference
    x1_init = np.array([1] + [0]*30)
    x1 = x1_init.copy()
    
    # Initialize x2 sequence from c_init exactly as reference
    x2_init = np.zeros(31)
    for ii in range(31):
        x2_init[ii] = (c_init >> ii) & 1
    x2 = x2_init.copy()
    
    # Generate sequences exactly as reference
    MPN = (2**16) - 1
    for n in range(MPN):
        x1 = np.append(x1, (x1[n+3] + x1[n]) % 2)
        x2 = np.append(x2, (x2[n+3] + x2[n+2] + x2[n+1] + x2[n]) % 2)
    
    # Generate c sequence with NC offset exactly as reference
    NC = 1600
    c = np.zeros(MPN - NC, dtype=int)
    for n in range(MPN - NC):
        c[n] = (x1[n + NC] + x2[n + NC]) % 2
    
    return c

def map_to_qpsk(c: np.ndarray, n_symbols: int) -> np.ndarray:
    """
    Map binary sequence to QPSK symbols
    
    Args:
        c: Binary sequence (0s and 1s)
        n_symbols: Number of QPSK symbols to generate
        
    Returns:
        Complex QPSK symbols
    """
    # MATLAB indexing: c(2*n-1) and c(2*n+1-1) for n=1,2,3,...
    # Python indexing: c[2*n-1] and c[2*n+1-1] for n=0,1,2,...
    DMRS_cmplx = np.zeros(n_symbols, dtype=complex)
    for n in range(n_symbols):
        real_part = (1 - 2*c[2*n-1]) / np.sqrt(2)
        imag_part = (1 - 2*c[2*n+1-1]) / np.sqrt(2)
        DMRS_cmplx[n] = real_part + 1j * imag_part
    
    return DMRS_cmplx

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
        Generate PDSCH DMRS symbols exactly matching MATLAB reference
        
        Args:
            num_rb: Number of resource blocks
            num_symbols: Number of symbols
            cell_id: Cell ID
            slot_idx: Slot index
            symbol_idx: Symbol index within slot
            
        Returns:
            Complex DMRS symbols
        """
        # Calculate c_init exactly as MATLAB
        c_init = ((2**17) * (14*slot_idx + symbol_idx + 1) * 
                  (2*cell_id + 1) + 2*cell_id) % (2**31)
        
        # Generate Gold sequence - always generate full length
        c = generate_gold_sequence(c_init)
        
        # Map to QPSK symbols - take only what we need
        n_sc = num_rb * 6  # 6 DMRS REs per RB (every other subcarrier)
        dmrs_symbols = map_to_qpsk(c, n_sc)
        
        # Return as column vector (n_sc, 1)
        return dmrs_symbols.reshape(-1, 1)

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
