"""
CORESET (Control Resource Set) implementation for 5G NR
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List
import numpy as np
from ..channel_types import ChannelType
from .base import PhysicalChannel
from ..definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT

class REGMappingType(Enum):
    """REG Mapping Type for CORESET"""
    NON_INTERLEAVED = auto()
    INTERLEAVED = auto()

@dataclass
class CORESET(PhysicalChannel):
    """
    Control Resource Set (CORESET) configuration
    """
    def __init__(self, 
                 start_rb: int,
                 num_rb: int,
                 start_symbol: int,
                 num_symbols: int,
                 slot_pattern: list,
                 rb_offset: int = 0,
                 rbg_bitmap: List[int] = None,
                 reg_mapping_type: REGMappingType = REGMappingType.NON_INTERLEAVED,
                 reg_bundle_size: int = 6,
                 power: float = 0.0,
                 rnti: int = 0,
                 payload_pattern: str = "0"):

        if num_rb % 6 != 0:
            raise ValueError("CORESET must be configured with a number of RBs that is a multiple of 6")

        self.rb_offset = rb_offset
        num_rbgs = num_rb // 6
        self.rbg_bitmap = rbg_bitmap if rbg_bitmap is not None else [1] * num_rbgs  # Default all RBGs used
        self.reg_mapping_type = reg_mapping_type
        self.reg_bundle_size = reg_bundle_size

        super().__init__(
            channel_type=ChannelType.CORESET,
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            power=power,
            rnti=rnti,
            payload_pattern=payload_pattern
        )

        self._validate_params()

        # Initialize data array
        n_sc = self.num_rb * N_SC_PER_RB
        self.data = np.zeros((n_sc, self.num_symbols), dtype=complex)

    def _validate_params(self):
        """Validate CORESET configuration parameters"""
        if not 1 <= self.num_symbols <= 3:
            raise ValueError("CORESET duration must be between 1 and 3 symbols")

        for slot in self.slot_pattern:
            if self.start_symbol + self.num_symbols > 14:
                raise ValueError(f"CORESET cannot extend beyond slot boundary in slot {slot}")

        effective_start_rb = self.start_rb + self.rb_offset
        if effective_start_rb < 0:
            raise ValueError(f"Effective starting RB (start_rb + rb_offset = {effective_start_rb}) cannot be negative")

        num_rbgs = self.num_rb // 6
        if len(self.rbg_bitmap) != num_rbgs:
            raise ValueError("RBG bitmap length must match number of RBGs (num_rb/6)")
        if not all(bit in [0, 1] for bit in self.rbg_bitmap):
            raise ValueError("RBG bitmap must contain only 0s and 1s")

        if self.reg_mapping_type == REGMappingType.INTERLEAVED:
            valid_bundle_sizes = [2, 3, 6]
            if self.reg_bundle_size not in valid_bundle_sizes:
                raise ValueError(f"REG bundle size must be one of {valid_bundle_sizes}")

    def get_reg_indices(self) -> List[tuple]:
        """
        Get REG indices based on mapping type
        Returns list of (start_sc, start_symbol) tuples for each REG
        """
        regs = []
        active_rbgs = [i for i, bit in enumerate(self.rbg_bitmap) if bit == 1]
        effective_start_rb = self.start_rb + self.rb_offset

        if self.reg_mapping_type == REGMappingType.NON_INTERLEAVED:
            # Sequential mapping
            for rbg_idx in active_rbgs:
                for rb_offset in range(6):  # Each RBG contains 6 RBs
                    rb = rbg_idx * 6 + rb_offset
                    for symbol in range(self.num_symbols):
                        start_sc = (effective_start_rb + rb) * N_SC_PER_RB
                        regs.append((start_sc, self.start_symbol + symbol))
        else:
            # Interleaved mapping
            reg_bundles = [active_rbgs[i:i + self.reg_bundle_size] 
                         for i in range(0, len(active_rbgs), self.reg_bundle_size)]

            for bundle_idx, bundle in enumerate(reg_bundles):
                for rbg_idx in bundle:
                    for rb_offset in range(6):  # Each RBG contains 6 RBs
                        rb = rbg_idx * 6 + rb_offset
                        for symbol in range(self.num_symbols):
                            start_sc = (effective_start_rb + rb) * N_SC_PER_RB
                            regs.append((start_sc, self.start_symbol + symbol))

        return regs 

    def calculate_indices(self):
        """Calculate frequency and time indices for all slots"""
        # Get active RBs based on RBG bitmap
        active_rbs = []
        for rbg_idx, bit in enumerate(self.rbg_bitmap):
            if bit == 1:
                # Each active RBG contributes 6 consecutive RBs
                rb_start = rbg_idx * 6
                for rb_offset in range(6):
                    active_rbs.append(rb_start + rb_offset)

        effective_start_rb = self.start_rb + self.rb_offset

        sc_indices = []
        for rb in active_rbs:
            start_sc = (effective_start_rb + rb) * N_SC_PER_RB
            sc_indices.extend(range(start_sc, start_sc + N_SC_PER_RB))

        self.freq_indices = sc_indices

        self.time_indices = {}
        for slot in self.slot_pattern:
            start_sym = self.start_symbol + slot * N_SYMBOLS_PER_SLOT
            end_sym = start_sym + self.num_symbols
            self.time_indices[slot] = range(start_sym, end_sym) 