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
    if modulation == ModulationType.QPSK:
        return (1/np.sqrt(2)) * (np.random.randint(0, 2, (n_sc, n_symbols)) * 2 - 1 + 
                                1j * (np.random.randint(0, 2, (n_sc, n_symbols)) * 2 - 1))
    else:
        raise NotImplementedError(f"Modulation {modulation} not yet implemented")