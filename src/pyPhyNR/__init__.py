"""
pyPhyNR - Python toolkit for 5G NR physical layer simulations
"""

__version__ = "0.1.0"

from . import core
from . import waveforms
from . import utils
from .core.signal_builder import NRSignalBuilder

# Recommended usage in documentation
__recommended_import__ = "import pyPhyNR as pynr"

# Make commonly used classes available in the root namespace
__all__ = ['NRSignalBuilder'] 