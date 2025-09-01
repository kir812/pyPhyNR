"""
OFDM parameter calculation for 5G NR
"""

from dataclasses import dataclass
from typing import List, Literal
from ..core.definitions import BASE_SCS, BASE_FFT, TC_SCALE, K_SCALE

@dataclass
class OfdmParams:
    """3GPP-compliant OFDM parameters"""
    fs: float                 # sampling rate [Hz]
    mu: int                   # numerology
    scs_hz: float             # subcarrier spacing [Hz]
    N_useful: int             # useful IFFT size
    N_fft: int                # chosen FFT size (>= N_useful)
    cp_short: int             # normal-CP short length [samples]
    cp_long: int              # normal-CP long length [samples]
    symbols_per_slot: int     # 14 (normal CP) or 12 (extended)
    slot_duration_s: float    # 1e-3 / 2**mu
    cp_per_symbol: List[int]  # CP lengths for one slot (normal CP)

def pick_fft(n_useful: int) -> int:
    """Choose power-of-two >= N_useful"""
    n = 1
    while n < n_useful:
        n <<= 1
    return n

def calculate_ofdm_params(fs_hz: float, mu: int, cp_type: Literal["normal","extended"]="normal", custom_fft_size: int = None) -> OfdmParams:
    """
    Calculate 3GPP-compliant OFDM parameters with intelligent padding distribution
    
    Args:
        fs_hz: Sampling rate in Hz
        mu: Numerology (0-4)
        cp_type: CP type ("normal" or "extended")
        custom_fft_size: Optional custom FFT size (if None, uses standard calculation)
        
    Returns:
        OfdmParams object with calculated parameters
    """
    assert mu in (0,1,2,3,4), "NR supports mu = 0..4"
    scs_hz = 15_000 * (2 ** mu)

    # useful samples = fs / Δf
    n_useful_f = fs_hz / scs_hz
    if abs(round(n_useful_f) - n_useful_f) > 1e-9:
        # non-integer -> you can still round, but better to adjust fs
        raise ValueError(f"N_useful not integer ({n_useful_f:.6f}). Consider adjusting fs.")
    N_useful = int(round(n_useful_f))

    # Use custom FFT size if provided, otherwise use standard calculation
    if custom_fft_size is not None:
        N_fft = custom_fft_size
        # Validate that custom FFT size is >= N_useful
        if N_fft < N_useful:
            raise ValueError(f"Custom FFT size ({N_fft}) must be >= N_useful ({N_useful})")
    else:
        N_fft = pick_fft(N_useful)

    if cp_type == "extended":
        if mu != 2:
            raise ValueError("Extended CP is defined for mu=2 in NR.")
        symbols_per_slot = 12
        # 38.211 ratio: N_CP,E = 512/2048 of useful symbol (for mu=2)
        cp_e = round(N_useful * (512/2048))
        cp_per_symbol = [cp_e] * symbols_per_slot
        return OfdmParams(fs_hz, mu, scs_hz, N_useful, N_fft, cp_e, cp_e,
                          symbols_per_slot, 1e-3/(2**mu), cp_per_symbol)

    # Normal CP
    symbols_per_slot = 14
    
    # Calculate CP lengths following MATLAB reference
    # Basic time unit and scaling factor
    tc = 1/(BASE_SCS * TC_SCALE * BASE_FFT)  # Basic time unit
    k = tc * K_SCALE                         # Scaling factor
    
    # Calculate CP lengths in samples
    cp_short = round(144 * k * 2**(-mu) * fs_hz)  # Normal symbols
    cp_long = round((144 * k * 2**(-mu) + 16 * k) * fs_hz)  # First symbol

    # Long CP logic exactly as MATLAB reference
    # MATLAB: if symbcount % (7 * (2**num)) == 0
    # This means every 7*(2^mu) symbols get long CP
    long_positions = []
    for i in range(symbols_per_slot):
        if i % (7 * (2**mu)) == 0:
            long_positions.append(i)
    
    # base CP list for one slot - exactly as MATLAB reference
    cp_per_symbol = [cp_long if i in long_positions else cp_short for i in range(symbols_per_slot)]

    return OfdmParams(fs_hz, mu, scs_hz, N_useful, N_fft, cp_short, cp_long,
                      symbols_per_slot, 1e-3/(2**mu), cp_per_symbol)


if __name__ == "__main__":
    # Test with standard FFT size
    print("Standard FFT size:")
    ofdm_params = calculate_ofdm_params(11.52e6, 1)
    print(f"  N_useful: {ofdm_params.N_useful}")
    print(f"  N_fft: {ofdm_params.N_fft}")

    # Test with custom FFT size
    print("\nCustom FFT size (384):")
    ofdm_params_custom = calculate_ofdm_params(11.52e6, 1, custom_fft_size=384)
    print(f"  N_useful: {ofdm_params_custom.N_useful}")
    print(f"  N_fft: {ofdm_params_custom.N_fft}")

    # Test with None (should use standard)
    print("\nCustom FFT size (None - should use standard):")
    ofdm_params_none = calculate_ofdm_params(11.52e6, 1, custom_fft_size=None)
    print(f"  N_useful: {ofdm_params_none.N_useful}")
    print(f"  N_fft: {ofdm_params_none.N_fft}")