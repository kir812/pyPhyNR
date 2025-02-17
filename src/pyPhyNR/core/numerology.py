"""
5G NR numerology configurations and related calculations
"""

from dataclasses import dataclass

@dataclass
class NRNumerology:
    mu: int  # Numerology (0-4)
    subcarrier_spacing: int  # kHz
    slot_duration: float  # ms
    slots_per_subframe: int
    slots_per_frame: int
    
NUMEROLOGIES = {
    0: NRNumerology(0, 15, 1.0, 1, 10),
    1: NRNumerology(1, 30, 0.5, 2, 20),
    2: NRNumerology(2, 60, 0.25, 4, 40),
    3: NRNumerology(3, 120, 0.125, 8, 80),
    4: NRNumerology(4, 240, 0.0625, 16, 160)
}

def get_numerology(mu: int) -> NRNumerology:
    """Get numerology configuration for given μ value."""
    if mu not in NUMEROLOGIES:
        raise ValueError(f"Invalid numerology μ={mu}. Must be 0-4.")
    return NUMEROLOGIES[mu] 