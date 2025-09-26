"""
Signal Builder for 5G NR
Provides a high-level interface for creating 5G NR signals
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np
from .carrier import CarrierConfig
from .channels import SSBlock, CORESET, PDCCH, PDSCH
from .modulation import ModulationType
from .waveform import WaveformGenerator
from .channel_types import ChannelType

class PDSCHBuilder:
    """Builder for PDSCH with fluent API for adding DMRS"""
    
    def __init__(self, signal_builder: 'NRSignalBuilder', pdsch: PDSCH):
        self.signal_builder = signal_builder
        self.pdsch = pdsch
    
    def add_dmrs(self, dmrs_positions: List[int] = None, 
                  clear_full_symbol: bool = True, 
                  subcarrier_pattern: str = "even",
                  power_offset_db: float = 0.0) -> 'NRSignalBuilder':
        """
        Add DMRS to the PDSCH with configurable options
        
        Args:
            dmrs_positions: DMRS symbol positions (default: [2, 11])
            clear_full_symbol: If True, clear entire symbol before inserting DMRS
            subcarrier_pattern: Which subcarriers to use ("even", "odd", "all", or custom list)
            power_offset_db: DMRS power relative to PDSCH in dB (default: 0.0 = same power)
            
        Returns:
            NRSignalBuilder for further method chaining
        """
        return self.signal_builder._add_dmrs_to_pdsch(
            self.pdsch, dmrs_positions, clear_full_symbol, subcarrier_pattern, power_offset_db
        )

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
                  power: float = 0.0,
                  rnti: int = 0,
                  payload_pattern: str = "0",
                  deterministic: bool = False) -> PDSCHBuilder:
        """
        Add PDSCH and return a PDSCHBuilder for chaining DMRS addition
        
        Args:
            start_rb: Starting resource block
            num_rb: Number of resource blocks
            start_symbol: Starting symbol
            num_symbols: Number of symbols
            slot_pattern: List of slots
            modulation: Modulation type ("QPSK", "QAM16", "QAM64", "QAM256")
            power: Power scaling in dB
            rnti: Radio Network Temporary Identifier
            payload_pattern: Payload pattern
            deterministic: If True, use deterministic data generation (for testing)
            
        Returns:
            PDSCHBuilder for chaining DMRS addition
        """
        if not self.grid:
            raise RuntimeError("Grid not initialized. Call initialize_grid() first")
        
        pdsch = PDSCH(
            start_rb=start_rb,
            num_rb=num_rb,
            start_symbol=start_symbol,
            num_symbols=num_symbols,
            slot_pattern=slot_pattern,
            modulation=ModulationType[modulation],
            cell_id=self.cell_id,
            power=power,
            rnti=rnti,
            payload_pattern=payload_pattern,
            deterministic=deterministic
        )
        self.grid.add_channel(pdsch)
        return PDSCHBuilder(self, pdsch)
    
    def _add_dmrs_to_pdsch(self, pdsch: PDSCH, dmrs_positions: List[int] = None, 
                          clear_full_symbol: bool = True, 
                          subcarrier_pattern: str = "even",
                          power_offset_db: float = 0.0) -> 'NRSignalBuilder':
        """
        Internal method to add DMRS to a specific PDSCH
        
        Args:
            pdsch: The PDSCH channel to add DMRS to
            dmrs_positions: DMRS symbol positions (default: [2, 11])
            clear_full_symbol: If True, clear entire symbol before inserting DMRS
            subcarrier_pattern: Which subcarriers to use ("even", "odd", "all", or custom list)
            power_offset_db: DMRS power relative to PDSCH in dB (default: 0.0 = same power)
            
        Returns:
            Self for method chaining
        """
        if not self.grid:
            raise RuntimeError("Grid not initialized. Call initialize_grid() first")
        
        # Default DMRS positions
        if dmrs_positions is None:
            dmrs_positions = [2, 11]
        
        # Get the resource grid values
        resource_grid = self.grid.values
        
        # Insert DMRS symbols only in slots where PDSCH exists
        # Use the PDSCH's slot pattern instead of all slots
        pdsch_slots = pdsch.slot_pattern
        
        # Pre-generate all DMRS sequences for better performance
        from .channels.dmrs import generate_gold_sequence, map_to_qpsk
        NoDMRSRE = 3276 // 2  # Max number of DMRS REs
        
        # Cache for DMRS sequences
        dmrs_cache = {}
        
        for slot_idx in pdsch_slots:
            for dmrs_sym in dmrs_positions:
                # Calculate absolute symbol index: iSmb = slot_idx * 14 + dmrs_sym
                absolute_sym_idx = slot_idx * 14 + dmrs_sym
                
                if absolute_sym_idx < resource_grid.shape[1]:  # Check bounds
                    # Calculate c_init
                    c_init = ((2**17) * (14*slot_idx + dmrs_sym + 1) * 
                              (2*self.cell_id + 1) + 2*self.cell_id) % (2**31)
                    
                    # Use cached sequence if available, otherwise generate
                    if c_init not in dmrs_cache:
                        c = generate_gold_sequence(c_init)
                        dmrs_cache[c_init] = map_to_qpsk(c, NoDMRSRE)
                    
                    dmrs_symbols = dmrs_cache[c_init]
                    
                    # Apply DMRS power relative to PDSCH power
                    # Get PDSCH power level
                    pdsch_power_linear = 10**(pdsch.power/20) if pdsch.power != 0.0 else 1.0
                    
                    # Apply DMRS power offset relative to PDSCH
                    dmrs_power_linear = pdsch_power_linear * 10**(power_offset_db/20)
                    dmrs_symbols *= dmrs_power_linear
                    
                    # Handle subcarrier pattern selection
                    if subcarrier_pattern == "even":
                        subcarrier_indices = list(range(0, resource_grid.shape[0], 2))  # [0, 2, 4, 6, ...]
                    elif subcarrier_pattern == "odd":
                        subcarrier_indices = list(range(1, resource_grid.shape[0], 2))  # [1, 3, 5, 7, ...]
                    elif subcarrier_pattern == "all":
                        subcarrier_indices = list(range(resource_grid.shape[0]))  # [0, 1, 2, 3, ...]
                    elif isinstance(subcarrier_pattern, list):
                        subcarrier_indices = [i for i in subcarrier_pattern if 0 <= i < resource_grid.shape[0]]
                    else:
                        raise ValueError(f"Invalid subcarrier_pattern: {subcarrier_pattern}. Use 'even', 'odd', 'all', or custom list")
                    
                    # 1. Clear symbol if requested
                    if clear_full_symbol:
                        resource_grid[:, absolute_sym_idx] = 0
                    
                    # 2. Insert DMRS on selected subcarriers
                    dmrs_length = min(len(dmrs_symbols), len(subcarrier_indices))
                    for i, sc_idx in enumerate(subcarrier_indices[:dmrs_length]):
                        resource_grid[sc_idx, absolute_sym_idx] = dmrs_symbols[i]
                    
                    # Update channel types and data for selected subcarriers
                    for sc in range(resource_grid.shape[0]):
                        if sc in subcarrier_indices[:dmrs_length]:
                            # This subcarrier gets DMRS
                            dmrs_idx = subcarrier_indices.index(sc)
                            if dmrs_idx < len(dmrs_symbols):
                                self.grid.grid[sc, absolute_sym_idx].channel_type = ChannelType.DL_DMRS
                                self.grid.grid[sc, absolute_sym_idx].data = dmrs_symbols[dmrs_idx]
                        elif clear_full_symbol:
                            # This subcarrier is cleared (0)
                            self.grid.grid[sc, absolute_sym_idx].channel_type = ChannelType.EMPTY
                            self.grid.grid[sc, absolute_sym_idx].data = 0
                        # If not clearing full symbol, other subcarriers keep their original data
        
        return self
    
    def generate_signal(self, sample_rate: Optional[float] = None, 
                       target_rms: Optional[float] = None) -> 'NRSignalBuilder':
        """
        Generate IQ samples
        
        Args:
            sample_rate: Optional new sample rate to use
            target_rms: Optional target RMS power level for normalization
            
        Returns:
            Complex IQ samples
        """
        if not self.grid:
            raise RuntimeError("Grid not initialized. Call initialize_grid() first")
            
        if sample_rate:
            self.carrier_config.set_sample_rate(sample_rate)
            
        waveform_gen = WaveformGenerator()
        iq_samples = waveform_gen.generate_frame_waveform(self.grid, self.carrier_config)
        
        # Apply power normalization if target RMS is specified
        if target_rms is not None:
            current_rms = np.sqrt(np.mean(np.abs(iq_samples)**2))
            if current_rms > 0:
                scale_factor = target_rms / current_rms
                iq_samples *= scale_factor
                print(f"Power normalized: RMS {current_rms:.2f} → {target_rms:.2f} (scale: {scale_factor:.4f})")
        
        return iq_samples
