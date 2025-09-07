"""
Waveform generation for 5G NR
"""

import numpy as np
from .resources import ResourceGrid
from .definitions import N_SC_PER_RB, N_SYMBOLS_PER_SLOT
from .carrier import CarrierConfig
from ..waveforms.ofdm import OfdmParams, calculate_ofdm_params

class WaveformGenerator:
    """
    Waveform generator for 5G NR signals using 3GPP-compliant parameters
    """

    def __init__(self):
        """
        Initialize waveform generator
        """
        pass

    def _get_ofdm_params(self, carrier_config: CarrierConfig) -> OfdmParams:
        """Calculate 3GPP OFDM parameters for this carrier.
        Args
        ----
        carrier_config: Carrier configuration

        Returns
        -------
        OfdmParams
            Calculated OFDM parameters using the user's sample rate.
        """
        # Use the user's sample rate directly
        user_fs = carrier_config.sample_rate
        
        return calculate_ofdm_params(
            fs_hz=user_fs,
            mu=carrier_config.numerology.mu,
            cp_type="normal",  # We can make this configurable later
            custom_fft_size=carrier_config.fft_size
        )

    def generate_ofdm_symbol(self, data: np.ndarray, ofdm_params: OfdmParams, symbol_idx: int) -> np.ndarray:
        """
        Generate OFDM symbol
        
        Args:
            data: Frequency domain data (complex)
            ofdm_params: OFDM parameters
            symbol_idx: Symbol index within slot (0-13)
            
        Returns:
            Time domain OFDM symbol with CP
        """
        # Get CP length for this symbol
        cp_length = ofdm_params.cp_per_symbol[symbol_idx]

        # Zero-pad to FFT size
        FD_symb = np.concatenate([data, np.zeros(ofdm_params.N_fft - len(data))])
        
        # Circshift to center the data
        shift_amount = round((ofdm_params.N_fft - len(data)) / 2)
        FD_symb = np.roll(FD_symb, shift_amount)
        
        
        # IFFT with ifftshift
        ifft_input = np.fft.ifftshift(FD_symb)
        
        TD_symb = np.fft.ifft(ifft_input)
        
        
        # Add cyclic prefix: [TD_symb[-cp_length:] TD_symb]
        TD_symb_cpincl = np.concatenate([TD_symb[-cp_length:], TD_symb])
        
        
        return TD_symb_cpincl

    def generate_slot_waveform(self, grid: ResourceGrid, slot_idx: int, ofdm_params: OfdmParams) -> np.ndarray:
        """
        Generate waveform for a single slot
        
        Args:
            grid: Resource grid
            slot_idx: Slot index
            ofdm_params: OFDM parameters
            
        Returns:
            IQ samples for the slot
        """
        # Get slot data from grid
        slot_start = slot_idx * N_SYMBOLS_PER_SLOT
        slot_end = slot_start + N_SYMBOLS_PER_SLOT

        slot_data = grid.values[:, slot_start:slot_end]
        

        # Generate OFDM symbols for the slot
        slot_waveform = []
        for sym_idx in range(N_SYMBOLS_PER_SLOT):
            symbol_data = slot_data[:, sym_idx]
            ofdm_symbol = self.generate_ofdm_symbol(symbol_data, ofdm_params, sym_idx)
            slot_waveform.append(ofdm_symbol)

        return np.concatenate(slot_waveform)

    def generate_frame_waveform(self, grid: ResourceGrid, carrier_config: CarrierConfig) -> np.ndarray:
        """
        Generate complete frame waveform
        
        Args:
            grid: Resource grid with all channels
            carrier_config: Carrier configuration
            
        Returns:
            IQ samples for the entire frame
        """
        # Get OFDM parameters using the user's sample rate
        ofdm_params = self._get_ofdm_params(carrier_config)

        # Calculate total slots
        slots_per_subframe = carrier_config.numerology.slots_per_subframe
        total_slots = 10 * slots_per_subframe  # 10 subframes

        frame_waveform = []

        # Generate waveform for each slot
        for slot_idx in range(total_slots):
            slot_waveform = self.generate_slot_waveform(grid, slot_idx, ofdm_params)
            frame_waveform.append(slot_waveform)
        
        waveform = np.concatenate(frame_waveform)
        

        return waveform

    def get_waveform_parameters(self, carrier_config: CarrierConfig) -> dict:
        """
        Get waveform parameters for the carrier configuration
        
        Args:
            carrier_config: Carrier configuration
            
        Returns:
            Dictionary with waveform parameters
        """
        ofdm_params = self._get_ofdm_params(carrier_config)

        # Calculate total slots
        slots_per_subframe = carrier_config.numerology.slots_per_subframe
        total_slots = 10 * slots_per_subframe
        total_symbols = total_slots * N_SYMBOLS_PER_SLOT

        # Calculate total samples
        samples_per_symbol = [ofdm_params.N_useful + cp for cp in ofdm_params.cp_per_symbol]
        total_samples = sum(samples_per_symbol) * total_slots

        return {
            'fft_size': ofdm_params.N_fft,
            'useful_size': ofdm_params.N_useful,
            'cp_short': ofdm_params.cp_short,
            'cp_long': ofdm_params.cp_long,
            'cp_per_symbol': ofdm_params.cp_per_symbol,
            'samples_per_symbol': samples_per_symbol,
            'total_slots': total_slots,
            'total_symbols': total_symbols,
            'total_samples': total_samples,
            'subcarrier_spacing': ofdm_params.fs/ofdm_params.N_fft,
            'sample_rate': ofdm_params.fs,
            'slot_duration': ofdm_params.slot_duration_s,
            'num_rb': carrier_config.n_resource_blocks,
            'numerology': ofdm_params.mu
        }
