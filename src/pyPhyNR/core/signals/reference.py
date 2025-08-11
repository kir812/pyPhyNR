"""Base classes for reference signals"""

from dataclasses import dataclass
import numpy as np
from typing import List
from ..channel_types import ChannelType
from ..modulation import ModulationType, generate_random_symbols

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