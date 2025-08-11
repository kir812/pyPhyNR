"""
5G NR definitions and constants
"""

# Resource Block (RB) definitions
N_SC_PER_RB = 12  # Number of subcarriers per RB

# Slot and frame definitions
N_SYMBOLS_PER_SLOT = 14  # Number of OFDM symbols per slot
N_SLOTS_PER_FRAME = 20   # Number of slots per 10ms frame

# Subcarrier spacing definitions (kHz)
SCS_15 = 15
SCS_30 = 30
SCS_60 = 60
SCS_120 = 120
SCS_240 = 240

# Bandwidth definitions (MHz)
BW_5 = 5
BW_10 = 10
BW_15 = 15
BW_20 = 20
BW_25 = 25
BW_30 = 30
BW_40 = 40
BW_50 = 50
BW_60 = 60
BW_80 = 80
BW_100 = 100

# Frequency Range definitions (in Hz)
FR1_FREQ_RANGE = (410e6, 7125e6)  # 410 MHz - 7.125 GHz
FR2_1_FREQ_RANGE = (24.25e9, 52.6e9)  # 24.25 GHz - 52.6 GHz
FR2_2_FREQ_RANGE = (52.6e9, 114.25e9)  # 52.6 GHz - 114.25 GHz

# Resource block configuration for each channel bandwidth and numerology (μ)
# Format: (bandwidth_mhz, numerology): rb_count
RB_TABLE = {
    # FR1 configurations
    (5, 0): 25,
    (5, 1): 11,
    (10, 0): 52,
    (10, 1): 24,
    (10, 2): 11,
    (15, 0): 79,
    (15, 1): 38,
    (15, 2): 18,
    (20, 0): 106,
    (20, 1): 51,
    (20, 2): 24,
    (25, 0): 133,
    (25, 1): 65,
    (25, 2): 31,
    (30, 0): 160,
    (30, 1): 78,
    (30, 2): 38,
    (40, 0): 216,
    (40, 1): 106,
    (40, 2): 51,
    (50, 0): 270,
    (50, 1): 133,
    (50, 2): 65,
    (60, 0): 324,
    (60, 1): 162,
    (60, 2): 79,
    (70, 0): 378,
    (70, 1): 189,
    (70, 2): 93,
    (80, 0): 432,
    (80, 1): 217,
    (80, 2): 107,
    (90, 0): 486,
    (90, 1): 245,
    (90, 2): 121,
    (100, 0): 540,
    (100, 1): 273,
    (100, 2): 135,
    
    # FR2-1 configurations (μ = 2,3)
    (50, 2): 66,
    (50, 3): 32,
    (100, 2): 132,
    (100, 3): 66,
    (200, 2): 264,
    (200, 3): 132,
    (400, 2): 528,
    (400, 3): 264,
    
    # FR2-2 configurations (μ = 3,4)
    (400, 3): 264,
    (400, 4): 132,
    (800, 3): 528,
    (800, 4): 264,
    (1600, 3): 1056,
    (1600, 4): 528,
    (2000, 3): 1320,
    (2000, 4): 660
}

def get_rb_count(bandwidth_mhz: int, numerology: int) -> int:
    """
    Get number of resource blocks for given bandwidth and numerology
    
    Args:
        bandwidth_mhz: Channel bandwidth in MHz
        numerology: μ value (0-4)
        
    Returns:
        Number of resource blocks
        
    Raises:
        ValueError: If combination of bandwidth and numerology is not valid
    """
    key = (bandwidth_mhz, numerology)
    if key not in RB_TABLE:
        raise ValueError(
            f"Invalid combination of bandwidth ({bandwidth_mhz} MHz) "
            f"and numerology (μ={numerology})"
        )
    return RB_TABLE[key]

def get_frequency_range(frequency_hz: float) -> str:
    """
    Determine the frequency range (FR1, FR2-1, or FR2-2) for a given frequency
    
    Args:
        frequency_hz: Frequency in Hz
        
    Returns:
        String indicating frequency range ('FR1', 'FR2-1', or 'FR2-2')
        
    Raises:
        ValueError: If frequency is outside defined ranges
    """
    if FR1_FREQ_RANGE[0] <= frequency_hz <= FR1_FREQ_RANGE[1]:
        return 'FR1'
    elif FR2_1_FREQ_RANGE[0] <= frequency_hz <= FR2_1_FREQ_RANGE[1]:
        return 'FR2-1'
    elif FR2_2_FREQ_RANGE[0] <= frequency_hz <= FR2_2_FREQ_RANGE[1]:
        return 'FR2-2'
    else:
        raise ValueError(f"Frequency {frequency_hz/1e6:.2f} MHz is outside defined ranges") 