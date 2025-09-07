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
    Generate random modulated symbols
    
    Args:
        n_sc: Number of subcarriers
        n_symbols: Number of symbols
        modulation: Modulation type
        
    Returns:
        Complex array of modulated symbols
    """
    total_symbols = n_sc * n_symbols
    
    if modulation == ModulationType.QPSK:
        # QPSK: Generate random bits and map to QPSK symbols
        bits = np.random.randint(0, 2, total_symbols * 2)  # 2 bits per symbol
        symbols = np.zeros(total_symbols, dtype=complex)
        for i in range(total_symbols):
            b1 = bits[2*i]     # First bit
            b0 = bits[2*i + 1] # Second bit
            symbols[i] = (1/np.sqrt(2)) * ((1 - 2*b1) + 1j*(1 - 2*b0))
    
    elif modulation == ModulationType.QAM16:
        # 16QAM: Generate random bits and map to 16QAM symbols
        bits = np.random.randint(0, 2, total_symbols * 4)  # 4 bits per symbol
        symbols = np.zeros(total_symbols, dtype=complex)
        for i in range(total_symbols):
            b1 = bits[4*i]     # First bit
            b2 = bits[4*i + 1] # Second bit
            b3 = bits[4*i + 2] # Third bit
            b4 = bits[4*i + 3] # Fourth bit
            symbols[i] = (1/np.sqrt(10)) * (
                (1 - 2*b1) * (2 - (1-2*b3)) + 1j * (1 - 2*b2) * (2 - (1-2*b4))
            )
    
    elif modulation == ModulationType.QAM64:
        # 64QAM: Generate random bits and map to 64QAM symbols
        bits = np.random.randint(0, 2, total_symbols * 6)  # 6 bits per symbol
        symbols = np.zeros(total_symbols, dtype=complex)
        for i in range(total_symbols):
            b1 = bits[6*i]     # First bit
            b2 = bits[6*i + 1] # Second bit
            b3 = bits[6*i + 2] # Third bit
            b4 = bits[6*i + 3] # Fourth bit
            b5 = bits[6*i + 4] # Fifth bit
            b6 = bits[6*i + 5] # Sixth bit
            symbols[i] = (1/np.sqrt(42)) * (
                (1 - 2*b1) * (4 - (1-2*b3) * (2 - (1-2*b5))) +
                1j * (1 - 2*b2) * (4 - (1-2*b4) * (2 - (1-2*b6)))
            )
        
    
    elif modulation == ModulationType.QAM256:
        # 256QAM: Generate random bits and map to 256QAM symbols
        bits = np.random.randint(0, 2, total_symbols * 8)  # 8 bits per symbol
        symbols = np.zeros(total_symbols, dtype=complex)
        for i in range(total_symbols):
            b1 = bits[8*i]     # First bit
            b2 = bits[8*i + 1] # Second bit
            b3 = bits[8*i + 2] # Third bit
            b4 = bits[8*i + 3] # Fourth bit
            b5 = bits[8*i + 4] # Fifth bit
            b6 = bits[8*i + 5] # Sixth bit
            b7 = bits[8*i + 6] # Seventh bit
            b8 = bits[8*i + 7] # Eighth bit
            symbols[i] = (1/np.sqrt(170)) * (
                (1 - 2*b1) * (8 - (1-2*b3) * (4 - (1-2*b5) * (2 - (1-2*b7)))) +
                1j * (1 - 2*b2) * (8 - (1-2*b4) * (4 - (1-2*b6) * (2 - (1-2*b8))))
            )
    
    else:
        raise NotImplementedError(f"Modulation {modulation} not yet implemented")
    
    return symbols.reshape(n_sc, n_symbols)