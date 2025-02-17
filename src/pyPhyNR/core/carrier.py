"""
5G NR Carrier Configuration
Based on MATLAB's nrCarrierConfig
"""

from dataclasses import dataclass
from .numerology import NRNumerology, get_numerology
from .definitions import get_rb_count

@dataclass
class CarrierConfig:
    """5G NR Carrier Configuration"""
    numerology: NRNumerology  # Numerology configuration
    n_size_grid: int  # Number of resource blocks
    cyclic_prefix: str = 'normal'  # 'normal' or 'extended'
    n_cell_id: int = 0  # Physical cell identity (0...1007)
    
    def __post_init__(self):
        """Validate configuration parameters"""
        # Validate cyclic prefix
        if self.cyclic_prefix not in ['normal', 'extended']:
            raise ValueError("Cyclic prefix must be 'normal' or 'extended'")
            
        # Validate cell ID
        if not 0 <= self.n_cell_id <= 1007:
            raise ValueError("Cell ID must be between 0 and 1007")
    
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