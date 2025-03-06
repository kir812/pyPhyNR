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
    shape = (n_sc, n_symbols)

    if modulation == ModulationType.QPSK:
        # QPSK: (±1 ± j)/√2
        return (1/np.sqrt(2)) * (np.random.randint(0, 2, shape) * 2 - 1 + 
                                1j * (np.random.randint(0, 2, shape) * 2 - 1))

    elif modulation == ModulationType.QAM16:
        # 16QAM: (±1 ± j, ±3 ± 3j)/√10
        real = np.random.randint(0, 4, shape) * 2 - 3
        imag = np.random.randint(0, 4, shape) * 2 - 3
        return (real + 1j * imag) / np.sqrt(10)

    elif modulation == ModulationType.QAM64:
        # 64QAM: (±1,±3,±5,±7 ± j)/√42
        real = np.random.randint(0, 8, shape) * 2 - 7
        imag = np.random.randint(0, 8, shape) * 2 - 7
        return (real + 1j * imag) / np.sqrt(42)

    elif modulation == ModulationType.QAM256:
        # 256QAM: (±1,±3,...,±15 ± j)/√170
        real = np.random.randint(0, 16, shape) * 2 - 15
        imag = np.random.randint(0, 16, shape) * 2 - 15
        return (real + 1j * imag) / np.sqrt(170)
    
    else:
        raise NotImplementedError(f"Modulation {modulation} not yet implemented")