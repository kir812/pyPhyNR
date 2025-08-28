"""
Signal Builder for 5G NR
Provides a high-level interface for creating 5G NR signals
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .carrier import CarrierConfig
from .channels import SSBlock, CORESET, PDCCH, PDSCH
from .modulation import ModulationType
from .waveform import WaveformGenerator

@dataclass
class CarrierParameters:
    """Carrier configuration parameters"""
    bandwidth_mhz: int
    numerology: int
    sample_rate: Optional[float] = None
    fft_size: Optional[int] = None
    num_rb: Optional[int] = None
    cp_type: str = "normal"

class NRSignalBuilder:
    """High-level interface for creating 5G NR signals"""
    def __init__(self, bandwidth_mhz: int, numerology: int, cell_id: int):
        """
        Initialize signal builder
        
        Args:
            bandwidth_mhz: Carrier bandwidth in MHz
            numerology: Numerology (0=15kHz, 1=30kHz, etc)
            cell_id: Physical cell ID
        """
        self.carrier_params = CarrierParameters(
            bandwidth_mhz=bandwidth_mhz,
            numerology=numerology
        )
        self.cell_id = cell_id
        self.carrier_config = None
        self.grid = None
        
    def configure_carrier(self, 
                         sample_rate: Optional[float] = None,
                         fft_size: Optional[int] = None,
                         num_rb: Optional[int] = None,
                         cp_type: str = "normal") -> 'NRSignalBuilder':
        """
        Configure carrier parameters
        
        Args:
            sample_rate: Sample rate in Hz
            fft_size: FFT size
            num_rb: Number of resource blocks
            cp_type: Cyclic prefix type ('normal' or 'extended')
            
        Returns:
            Self for method chaining
        """
        self.carrier_params.sample_rate = sample_rate
        self.carrier_params.fft_size = fft_size
        self.carrier_params.num_rb = num_rb
        self.carrier_params.cp_type = cp_type
        return self
    
    def initialize_grid(self) -> 'NRSignalBuilder':
        """
        Initialize resource grid with current configuration
        
        Returns:
            Self for method chaining
        """
        # Create carrier config
        self.carrier_config = CarrierConfig.from_bandwidth(
            self.carrier_params.bandwidth_mhz,
            self.carrier_params.numerology
        )
        
        # Apply custom configurations
        if self.carrier_params.sample_rate:
            self.carrier_config.set_sample_rate(self.carrier_params.sample_rate)
        if self.carrier_params.fft_size:
            self.carrier_config.set_fft_size(self.carrier_params.fft_size)
        if self.carrier_params.num_rb:
            self.carrier_config.n_resource_blocks = self.carrier_params.num_rb
            
        # Create grid
        self.grid = self.carrier_config.get_resource_grid()
        return self
    
    def get_carrier_config(self) -> Dict[str, Any]:
        """Get current carrier configuration"""
        if not self.carrier_config:
            raise RuntimeError("Carrier not initialized. Call initialize_grid() first")
            
        return {
            'bandwidth_mhz': self.carrier_params.bandwidth_mhz,
            'numerology': self.carrier_params.numerology,
            'sample_rate': self.carrier_config.sample_rate,
            'fft_size': self.carrier_config.fft_size,
            'num_rb': self.carrier_config.n_resource_blocks,
            'cp_type': self.carrier_params.cp_type
        }
    
    def add_coreset_pdcch(self,
                  start_rb: int,
                  num_rb: int,
                  start_symbol: int,
                  num_symbols: int,
                  slot_pattern: List[int],
                  power: float = 0.0,
                  rnti: int = 0,
                  payload_pattern: str = "0") -> 'NRSignalBuilder':
        """
        Add CORESET and PDCCH
        
        Args:
            start_rb: Starting resource block
            num_rb: Number of resource blocks
            start_symbol: Starting symbol
            num_symbols: Number of symbols
            slot_pattern: List of slots
            power: Power scaling in dB
            rnti: Radio Network Temporary Identifier
            payload_pattern: Payload pattern
            
        Returns:
            Self for method chaining
        """
        if not self.grid:
            raise RuntimeError("Grid not initialized. Call initialize_grid() first")
            
        # Add CORESET first
        coreset = CORESET(
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            power=power,
            rnti=rnti,
            payload_pattern=payload_pattern
        )
        self.grid.add_channel(coreset)
        
        # Add PDCCH on top of CORESET
        pdcch = PDCCH(
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            cell_id=self.cell_id,
            power=power,
            rnti=rnti,
            payload_pattern=payload_pattern
        )
        self.grid.add_channel(pdcch)
        return self
        
    def add_ssb(self, 
                start_rb: int,
                start_symbol: int,
                slot_pattern: List[int],
                power: float = 0.0,
                ssb_index: int = 0,
                half_frame: int = 0) -> 'NRSignalBuilder':
        """
        Add SS/PBCH Block
        
        Args:
            start_rb: Starting resource block
            start_symbol: Starting symbol
            slot_pattern: List of slots containing SSB
            power: Power scaling in dB
            ssb_index: SSB index
            half_frame: Half frame index
            
        Returns:
            Self for method chaining
        """
        if not self.grid:
            raise RuntimeError("Grid not initialized. Call initialize_grid() first")
            
        ssb = SSBlock(
            cell_id=self.cell_id,
            start_rb=start_rb,
            start_symbol=start_symbol,
            slot_pattern=slot_pattern,
            ssb_index=ssb_index,
            half_frame=half_frame,
            power=power
        )
        self.grid.add_channel(ssb)
        return self
    
    def add_pdsch(self,
                  start_rb: int,
                  num_rb: int,
                  start_symbol: int,
                  num_symbols: int,
                  slot_pattern: List[int],
                  modulation: str = "QAM64",
                  dmrs_type: str = "A",
                  dmrs_add_pos: int = 1,
                  power: float = 0.0,
                  rnti: int = 0,
                  payload_pattern: str = "0") -> 'NRSignalBuilder':
        """
        Add PDSCH
        
        Args:
            start_rb: Starting resource block
            num_rb: Number of resource blocks
            start_symbol: Starting symbol
            num_symbols: Number of symbols
            slot_pattern: List of slots
            modulation: Modulation type ("QPSK", "QAM16", "QAM64", "QAM256")
            dmrs_type: DMRS type ("A" or "B")
            dmrs_add_pos: Additional DMRS positions
            power: Power scaling in dB
            rnti: Radio Network Temporary Identifier
            payload_pattern: Payload pattern
            slot_count: Number of slots to repeat pattern
            
        Returns:
            Self for method chaining
        """
        if not self.grid:
            raise RuntimeError("Grid not initialized. Call initialize_grid() first")
            
        # Get DMRS positions based on type
        dmrs_positions = self._get_dmrs_positions(dmrs_type, dmrs_add_pos)
        
        pdsch = PDSCH(
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            modulation=ModulationType[modulation],
            dmrs_positions=dmrs_positions,
            cell_id=self.cell_id,
            power=power,
            rnti=rnti,
            payload_pattern=payload_pattern
        )
        self.grid.add_channel(pdsch)
        return self
    
    def _get_dmrs_positions(self, dmrs_type: str, add_pos: int) -> List[int]:
        """Get DMRS positions based on type and additional positions"""
        if dmrs_type == "A":
            base_pos = [0, 2, 4, 6, 8, 10]  # Type A positions
        else:  # Type B
            base_pos = [0, 1, 6, 7]  # Type B positions
            
        # TODO: Handle additional positions based on add_pos parameter
        return base_pos
    
    def generate_signal(self, sample_rate: Optional[float] = None) -> 'NRSignalBuilder':
        """
        Generate IQ samples
        
        Args:
            sample_rate: Optional new sample rate to use
            
        Returns:
            Complex IQ samples
        """
        if not self.grid:
            raise RuntimeError("Grid not initialized. Call initialize_grid() first")
            
        if sample_rate:
            self.carrier_config.set_sample_rate(sample_rate)
            
        waveform_gen = WaveformGenerator()
        return waveform_gen.generate_frame_waveform(self.grid, self.carrier_config)
