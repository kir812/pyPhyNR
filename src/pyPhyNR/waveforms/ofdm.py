"""
OFDM parameter calculation for 5G NR
"""

from dataclasses import dataclass
from typing import List, Literal

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
    cp_short = round(N_useful * (144/2048))
    cp_long  = round(N_useful * (160/2048))

    # Long CP once every 0.5 ms. That means:
    # - mu >= 1 (slot ≤ 0.5 ms): symbol 0 of every slot is long
    # - mu == 0 (slot = 1 ms): symbols 0 and 7 inside the slot are long
    long_positions = [0] if mu >= 1 else [0, 7]

    # base CP list for one slot
    cp_per_symbol = [cp_long if i in long_positions else cp_short for i in range(symbols_per_slot)]
    sym_samples = [N_useful + c for c in cp_per_symbol]

    # timing compensation to hit exact slot length
    slot_samples_target = int(round(fs_hz * (1e-3 / (2**mu))))  # 1 ms / 2^mu
    deficit = slot_samples_target - sum(sym_samples)

    # Distribute padding to CPs (prefer long-CP first, then spread from end)
    if deficit > 0:
        order = long_positions + [i for i in range(symbols_per_slot-1, -1, -1)
                                  if i not in long_positions]
        k = 0
        for _ in range(deficit):
            i = order[k % len(order)]
            cp_per_symbol[i] += 1
            sym_samples[i] += 1
            k += 1

    elif deficit < 0:
        order = [i for i in range(symbols_per_slot-1, -1, -1) if cp_per_symbol[i] > 0]
        k = 0
        for _ in range(-deficit):
            i = order[k % len(order)]
            cp_per_symbol[i] -= 1
            sym_samples[i] -= 1
            k += 1

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