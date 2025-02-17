"""
5G NR Carrier Configuration
"""

from dataclasses import dataclass, field
from .numerology import NRNumerology, get_numerology
from .definitions import get_rb_count, N_SC_PER_RB, N_SYMBOLS_PER_SLOT
from .resources import ResourceElement
from .channel_types import ChannelType

@dataclass
class CarrierConfig:
    """5G NR Carrier Configuration"""
    numerology: NRNumerology  # Numerology configuration
    n_size_grid: int  # Number of resource blocks
    cyclic_prefix: str = 'normal'  # 'normal' or 'extended'
    n_cell_id: int = 0  # Physical cell identity (0...1007)
    resource_grid: list[ResourceElement] = field(init=False)  # List of all REs

    def __post_init__(self):
        """Initialize and validate configuration"""
        # Validate parameters
        if self.cyclic_prefix not in ['normal', 'extended']:
            raise ValueError("Cyclic prefix must be 'normal' or 'extended'")
            
        if not 0 <= self.n_cell_id <= 1007:
            raise ValueError("Cell ID must be between 0 and 1007")

        # Initialize resource grid
        slots_per_subframe = self.numerology.slots_per_subframe
        total_slots = 10 * slots_per_subframe  # 10ms frame
        total_subcarriers = self.n_size_grid * N_SC_PER_RB
        
        self.resource_grid = [
            ResourceElement(
                subcarrier=sc,
                symbol=symbol,
                slot=slot,
                channel_type=ChannelType.EMPTY,
                value=0+0j
            )
            for slot in range(total_slots)
            for symbol in range(N_SYMBOLS_PER_SLOT)
            for sc in range(total_subcarriers)
        ]

    @property
    def subcarrier_spacing(self) -> int:
        """Get subcarrier spacing in kHz"""
        return self.numerology.subcarrier_spacing
    
    @classmethod
    def from_bandwidth(cls, bandwidth_mhz: int, mu: int, **kwargs):
        """
        Create carrier config from bandwidth and numerology
        
        Args:
            bandwidth_mhz: Channel bandwidth in MHz
            mu: μ value (0-4)
            **kwargs: Additional arguments for CarrierConfig
        """
        numerology = get_numerology(mu)
        n_size_grid = get_rb_count(bandwidth_mhz, mu)
        return cls(numerology=numerology, n_size_grid=n_size_grid, **kwargs)

    def create_empty_grid(self):
        """
        Create a list of empty ResourceElements for the entire grid
        
        Returns:
            List of ResourceElements covering the entire frame
        """
        return self.resource_grid 

    def allocate_channel(self, channel_type: ChannelType, start_rb: int, num_rb: int, 
                        start_symbol: int, num_symbols: int, slot: int):
        """
        Allocate a channel to a block of resource elements
        
        Args:
            channel_type: Type of channel to allocate
            start_rb: Starting resource block index
            num_rb: Number of resource blocks
            start_symbol: Starting OFDM symbol in the slot
            num_symbols: Number of OFDM symbols
            slot: Slot number
        """
        start_sc = start_rb * N_SC_PER_RB
        num_sc = num_rb * N_SC_PER_RB
        
        for sc in range(start_sc, start_sc + num_sc):
            for symbol in range(start_symbol, start_symbol + num_symbols):
                idx = self._get_re_index(sc, symbol, slot)
                if idx is not None:
                    self.resource_grid[idx].channel_type = channel_type

    def allocate_scattered(self, channel_type: ChannelType, rb_indices: list[int], 
                          symbol_indices: list[int], slot: int):
        """
        Allocate a channel to scattered resource elements
        
        Args:
            channel_type: Type of channel to allocate
            rb_indices: List of resource block indices
            symbol_indices: List of OFDM symbol indices
            slot: Slot number
        """
        for rb in rb_indices:
            start_sc = rb * N_SC_PER_RB
            for sc in range(start_sc, start_sc + N_SC_PER_RB):
                for symbol in symbol_indices:
                    idx = self._get_re_index(sc, symbol, slot)
                    if idx is not None:
                        self.resource_grid[idx].channel_type = channel_type

    def _get_re_index(self, subcarrier: int, symbol: int, slot: int) -> int:
        """Get index of RE in the grid list"""
        for i, re in enumerate(self.resource_grid):
            if (re.subcarrier == subcarrier and 
                re.symbol == symbol and 
                re.slot == slot):
                return i
        return None 