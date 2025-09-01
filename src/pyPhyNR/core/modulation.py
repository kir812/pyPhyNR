"""
Modulation schemes for 5G NR
"""

from enum import Enum, auto
import numpy as np

class ModulationType(Enum):
    BPSK = auto()
    QPSK = auto()
    QAM16 = auto()
    QAM64 = auto()
    QAM256 = auto()

def map_qam64(bits: np.ndarray) -> np.ndarray:
    """
    Map 6 bits to 64QAM symbol as per 3GPP TS 38.211
    (1-2*b1)*(4-(1-2*b3)*(2-(1-2*b5))) + j*(1-2*b2)*(4-(1-2*b4)*(2-(1-2*b6)))
    """
    b = bits.reshape(-1, 6)  # Group into 6 bits
    i = (1 - 2*b[:,0]) * (4 - (1-2*b[:,2]) * (2 - (1-2*b[:,4])))
    q = (1 - 2*b[:,1]) * (4 - (1-2*b[:,3]) * (2 - (1-2*b[:,5])))
    return (i + 1j*q) / np.sqrt(42)

def map_qam256(bits: np.ndarray) -> np.ndarray:
    """
    Map 8 bits to 256QAM symbol as per 3GPP TS 38.211
    (1-2*b1)*(8-(1-2*b3)*(4-(1-2*b5)*(2-(1-2*b7)))) + 
    j*(1-2*b2)*(8-(1-2*b4)*(4-(1-2*b6)*(2-(1-2*b8))))
    """
    b = bits.reshape(-1, 8)  # Group into 8 bits
    i = (1 - 2*b[:,0]) * (8 - (1-2*b[:,2]) * (4 - (1-2*b[:,4]) * (2 - (1-2*b[:,6]))))
    q = (1 - 2*b[:,1]) * (8 - (1-2*b[:,3]) * (4 - (1-2*b[:,5]) * (2 - (1-2*b[:,7]))))
    return (i + 1j*q) / np.sqrt(170)

def generate_random_symbols(n_sc: int, n_symbols: int, modulation: ModulationType = ModulationType.QPSK) -> np.ndarray:
    """
    Generate random modulated symbols exactly matching MATLAB reference implementation
    
    Args:
        n_sc: Number of subcarriers
        n_symbols: Number of symbols
        modulation: Modulation type
        
    Returns:
        Complex array of modulated symbols
    """
    total_symbols = n_sc * n_symbols
    
    if modulation == ModulationType.QPSK:
        # QPSK: Generate random integers 0-3, then extract bits exactly like reference
        random_ints = np.random.randint(0, 4, total_symbols)
        symbols = np.zeros(total_symbols, dtype=complex)
        for i, val in enumerate(random_ints):
            # Extract bits exactly like reference: b1 = second bit, b0 = first bit
            b1 = (val >> 1) & 1  # Second bit (MATLAB bitget(x,2))
            b0 = val & 1         # First bit (MATLAB bitget(x,1))
            symbols[i] = (1/np.sqrt(2)) * ((1 - 2*b1) + 1j*(1 - 2*b0))
    
    elif modulation == ModulationType.QAM16:
        # 16QAM: Generate random integers 0-15, then extract bits like MATLAB bitget
        random_ints = np.random.randint(0, 16, total_symbols)
        symbols = np.zeros(total_symbols, dtype=complex)
        for i, val in enumerate(random_ints):
            # Extract bits like MATLAB bitget
            b1 = (val >> 0) & 1  # bitget(x,1) - LSB
            b2 = (val >> 1) & 1  # bitget(x,2)
            b3 = (val >> 2) & 1  # bitget(x,3)
            b4 = (val >> 3) & 1  # bitget(x,4) - MSB
            symbols[i] = (1/np.sqrt(10)) * (
                (1 - 2*b1) * (2 - (1-2*b3)) + 1j * (1 - 2*b2) * (2 - (1-2*b4))
            )
    
    elif modulation == ModulationType.QAM64:
        # 64QAM: Generate random integers 0-63, then extract bits like MATLAB bitget
        random_ints = np.random.randint(0, 64, total_symbols)
        symbols = np.zeros(total_symbols, dtype=complex)
        for i, val in enumerate(random_ints):
            # Extract bits like MATLAB bitget
            b1 = (val >> 0) & 1  # bitget(x,1) - LSB
            b2 = (val >> 1) & 1  # bitget(x,2)
            b3 = (val >> 2) & 1  # bitget(x,3)
            b4 = (val >> 3) & 1  # bitget(x,4)
            b5 = (val >> 4) & 1  # bitget(x,5)
            b6 = (val >> 5) & 1  # bitget(x,6) - MSB
            symbols[i] = (1/np.sqrt(42)) * (
                (1 - 2*b1) * (4 - (1-2*b3) * (2 - (1-2*b5))) +
                1j * (1 - 2*b2) * (4 - (1-2*b4) * (2 - (1-2*b6)))
            )
    
    elif modulation == ModulationType.QAM256:
        # 256QAM: Generate random integers 0-255, then extract bits like MATLAB bitget
        random_ints = np.random.randint(0, 256, total_symbols)
        symbols = np.zeros(total_symbols, dtype=complex)
        for i, val in enumerate(random_ints):
            # Extract bits like MATLAB bitget
            b1 = (val >> 0) & 1  # bitget(x,1) - LSB
            b2 = (val >> 1) & 1  # bitget(x,2)
            b3 = (val >> 2) & 1  # bitget(x,3)
            b4 = (val >> 3) & 1  # bitget(x,4)
            b5 = (val >> 5) & 1  # bitget(x,5)
            b6 = (val >> 6) & 1  # bitget(x,6)
            b7 = (val >> 7) & 1  # bitget(x,7)
            b8 = (val >> 8) & 1  # bitget(x,8) - MSB
            symbols[i] = (1/np.sqrt(170)) * (
                (1 - 2*b1) * (8 - (1-2*b3) * (4 - (1-2*b5) * (2 - (1-2*b7)))) +
                1j * (1 - 2*b2) * (8 - (1-2*b4) * (4 - (1-2*b6) * (2 - (1-2*b8))))
            )
    
    else:
        raise NotImplementedError(f"Modulation {modulation} not yet implemented")
    
    return symbols.reshape(n_sc, n_symbols)