import numpy as np
from fractions import Fraction
from scipy.signal import resample_poly


def resample_waveform(iq: np.ndarray, fs_in: float, fs_out: float) -> np.ndarray:
    """Resample complex waveform to a new sampling rate.

    Parameters
    ----------
    iq : np.ndarray
        Complex IQ samples at the original sampling rate.
    fs_in : float
        Original sampling rate in Hz.
    fs_out : float
        Desired sampling rate in Hz.

    Returns
    -------
    np.ndarray
        Resampled IQ array at ``fs_out``.
    """
    if fs_in == fs_out:
        return iq

    frac = Fraction(fs_out, fs_in).limit_denominator(1000)
    return resample_poly(iq, frac.numerator, frac.denominator)
