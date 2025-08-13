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
        """Calculate standard 3GPP OFDM parameters for this carrier.

        The 3GPP-defined sampling rate is derived from the number of
        configured resource blocks and numerology. If the user supplies a
        different ``CarrierConfig.sample_rate`` the waveform will later be
        resampled, but the OFDM parameters are always based on the standard
        rate to preserve the requested sub-carrier spacing.

        Args
        ----
        carrier_config: Carrier configuration

        Returns
        -------
        OfdmParams
            Calculated OFDM parameters using the standard sampling rate.
        """
        scs_hz = carrier_config.subcarrier_spacing * 1000
        n_subcarriers = carrier_config.n_resource_blocks * N_SC_PER_RB
        # FFT size defined as next power-of-two >= occupied subcarriers
        n_fft = 1 << (n_subcarriers - 1).bit_length()
        standard_fs = scs_hz * n_fft

        return calculate_ofdm_params(
            fs_hz=standard_fs,
            mu=carrier_config.numerology.mu,
            cp_type="normal",  # We can make this configurable later
        )

    def generate_ofdm_symbol(self, data: np.ndarray, ofdm_params: OfdmParams, symbol_idx: int) -> np.ndarray:
        """
        Generate OFDM symbol with proper CP
        
        Args:
            data: Frequency domain data (complex)
            ofdm_params: OFDM parameters
            symbol_idx: Symbol index within slot (0-13)
            
        Returns:
            Time domain OFDM symbol with CP
        """
        # Get CP length for this symbol
        cp_length = ofdm_params.cp_per_symbol[symbol_idx]

        # Zero-pad to FFT size for IFFT computation
        padded_data = np.zeros(ofdm_params.N_fft, dtype=complex)
        start_idx = ofdm_params.N_fft // 2 - len(data) // 2
        padded_data[start_idx:start_idx + len(data)] = data

        # IFFT
        time_symbol_full = np.fft.ifft(padded_data)

        # Extract only the useful samples (N_useful) from the center
        # This maintains the correct timing at the output sample rate
        start_useful = (ofdm_params.N_fft - ofdm_params.N_useful) // 2
        end_useful = start_useful + ofdm_params.N_useful
        time_symbol = time_symbol_full[start_useful:end_useful]

        # Add cyclic prefix
        cp = time_symbol[-cp_length:]
        return np.concatenate([cp, time_symbol])

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
        # Get OFDM parameters at the 3GPP-defined sampling rate
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

        # Resample if user-selected rate differs from standard rate
        if abs(ofdm_params.fs - carrier_config.sample_rate) > 1:
            from ..utils import resample_waveform
            waveform = resample_waveform(waveform, ofdm_params.fs, carrier_config.sample_rate)

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

        # Calculate total samples at the standard rate
        samples_per_symbol = [ofdm_params.N_useful + cp for cp in ofdm_params.cp_per_symbol]
        total_samples = sum(samples_per_symbol) * total_slots

        # Adjust sample count if resampling is needed
        if abs(ofdm_params.fs - carrier_config.sample_rate) > 1:
            total_samples = int(round(total_samples * carrier_config.sample_rate / ofdm_params.fs))
            sample_rate = carrier_config.sample_rate
        else:
            sample_rate = ofdm_params.fs

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
            'subcarrier_spacing': ofdm_params.scs_hz,
            'sample_rate': sample_rate,
            'slot_duration': ofdm_params.slot_duration_s,
            'num_rb': carrier_config.n_resource_blocks,
            'numerology': ofdm_params.mu
        }
