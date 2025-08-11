"""
5G NR Carrier Configuration
"""

from dataclasses import dataclass, field
from .numerology import NRNumerology, get_numerology
from .definitions import get_rb_count, N_SC_PER_RB, N_SYMBOLS_PER_SLOT
from .resources import ResourceElement, ResourceGrid, PhysicalChannel
from .channel_types import ChannelType


@dataclass
class CarrierConfig:
    """5G NR Carrier Configuration"""
    numerology: NRNumerology
    n_resource_blocks: int
    cyclic_prefix: str = 'normal'
    n_cell_id: int = 0
    sample_rate: float = 122880000.0
    tdd_pattern: list[int] = None
    special_slot_pattern: list[int] = None

    def __post_init__(self):
        if self.cyclic_prefix not in ['normal', 'extended']:
            raise ValueError("Cyclic prefix must be 'normal' or 'extended'")
        if not 0 <= self.n_cell_id <= 1007:
            raise ValueError("Cell ID must be between 0 and 1007")

    @classmethod
    def from_bandwidth(cls, bandwidth_mhz: int, mu: int) -> 'CarrierConfig':
        """Create carrier config from bandwidth"""
        numerology = get_numerology(mu)
        n_rb = get_rb_count(bandwidth_mhz, mu)
        return cls(numerology=numerology, n_resource_blocks=n_rb)

    @property
    def subcarrier_spacing(self) -> int:
        """Get subcarrier spacing in kHz"""
        return self.numerology.subcarrier_spacing

    def get_resource_grid(self) -> ResourceGrid:
        """Create and return a resource grid based on this carrier config"""
        slots_per_subframe = self.numerology.slots_per_subframe
        total_slots = 10 * slots_per_subframe  # 10ms frame
        total_symbols = N_SYMBOLS_PER_SLOT * total_slots
        total_subcarriers = self.n_resource_blocks * N_SC_PER_RB

        return ResourceGrid(
            n_subcarriers=total_subcarriers,
            n_symbols=total_symbols,
        )

    def set_sample_rate(self, sample_rate: float):
        """Set sample rate for the carrier"""
        self.sample_rate = sample_rate

    def set_tdd_pattern(self, tdd_pattern: list[int]):
        """Set TDD pattern for the carrier"""
        self.tdd_pattern = tdd_pattern

    def set_special_slot_pattern(self, special_slot_pattern: list[int]):
        """Set special slot pattern for the carrier"""
        self.special_slot_pattern = special_slot_pattern

