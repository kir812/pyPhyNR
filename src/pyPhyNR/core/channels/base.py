"""Base class for physical channels"""

from dataclasses import dataclass, field
import numpy as np
from typing import Optional
from ..channel_types import ChannelType
from ..definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT
from ..signals.reference import ReferenceSignal

@dataclass
class PhysicalChannel:
    """Base class for all physical channels"""
    channel_type: ChannelType
    start_rb: int
    num_rb: int
    start_symbol: int
    num_symbols: int
    slot_pattern: list = field(default_factory=list)
    reference_signal: Optional[ReferenceSignal] = None
    data: np.ndarray = field(init=False)

    def __post_init__(self):
        """Initialize and validate channel parameters"""
        if not self.slot_pattern:
            self.slot_pattern = [0]  # Default to slot 0 if not specified
        if not all(isinstance(slot, int) and slot >= 0 for slot in self.slot_pattern):
            raise ValueError("All slots must be non-negative integers")
        
        # Calculate indices for resource mapping
        self.calculate_indices()

    def calculate_indices(self):
        """Calculate frequency and time indices for all slots"""
        # Frequency domain indices (same for all slots)
        start_sc = self.start_rb * N_SC_PER_RB
        end_sc = start_sc + self.num_rb * N_SC_PER_RB
        self.freq_indices = range(start_sc, end_sc)

        # Time domain indices for each slot
        self.time_indices = {}
        for slot in self.slot_pattern:
            start_sym = self.start_symbol + slot * N_SYMBOLS_PER_SLOT
            end_sym = start_sym + self.num_symbols
            self.time_indices[slot] = range(start_sym, end_sym)

    def _generate_reference_signal(self) -> np.ndarray:
        """Generate reference signal if present"""
        if self.reference_signal:
            return self.reference_signal.generate_symbols(self.num_rb, self.num_symbols)
        return None 