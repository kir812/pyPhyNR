# pyPhyNR

Python toolkit for 5G NR physical layer simulations. This package provides tools and utilities for working with 5G NR physical layer concepts, including resource grid visualization, waveform generation, and signal processing techniques.

## Installation

```bash
pip install pyPhyNR
```

## Features

Current working features:
- Resource grid visualization
- Waveform generation
- OFDM signal processing
- PDSCH (Physical Downlink Shared Channel) implementation
- DMRS (Demodulation Reference Signals) for PDSCH
- Flexible numerology support

Note: Other physical channels (PBCH, PDCCH, PSS/SSS) are under development and not fully tested yet.

## Quick Start

```python
import pyPhyNR as pynr

# TDD slot configuration (20 slots per frame)
# 0: Downlink, 1: Uplink, 2: Special slot
TDD_SLOT_PATTERN = [0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Create signal builder for 20MHz carrier with 30kHz subcarrier spacing (numerology 1)
signal = pynr.NRSignalBuilder(bandwidth_mhz=20, numerology=1, cell_id=1)

# Configure carrier parameters
signal.configure_carrier(
    sample_rate=23.04e6,
    fft_size=768
).initialize_grid()

# Add PDSCH to downlink slots with DMRS
dl_slots = [i for i, slot in enumerate(TDD_SLOT_PATTERN) if slot == 0]
signal.add_pdsch(
    start_rb=0,
    num_rb=51,  # Full bandwidth
    start_symbol=0,
    num_symbols=14,  # Full slot
    slot_pattern=dl_slots,
    modulation="QAM256",
    power=100.8
).add_dmrs(
    dmrs_positions=[2, 11],  # DMRS symbols within slot
    clear_full_symbol=False,
    subcarrier_pattern="even",  # DMRS on even subcarriers
    power_offset_db=0.0
)

# Visualize resource grid
pynr.utils.plot_grid_dl(signal.carrier_config, signal.grid)

# Generate and analyze waveform
iq_samples = signal.generate_signal()
pynr.utils.plot_time_domain(iq_samples, signal.carrier_config)
pynr.utils.plot_frequency_domain(iq_samples, signal.carrier_config)
```

This example demonstrates:
- Configuring a 20 MHz TDD carrier with 30 kHz subcarrier spacing
- Setting up a realistic TDD slot pattern
- Adding PDSCH with 256-QAM modulation to downlink slots
- Configuring DMRS with proper symbol positions and power
- Visualizing and analyzing the generated signal

## Requirements

- Python >= 3.9
- NumPy
- Matplotlib
- SciPy

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

kir812

## Project Status

This project is in alpha stage (version 0.1.0). APIs may change in future releases.