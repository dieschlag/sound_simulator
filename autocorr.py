import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def compute_autocorrelation(signal):
    """Computes the autocorrelation of a signal.

    Args:
        signal (np.ndarray): The input audio signal.

    Returns:
        np.ndarray: Autocorrelation values.
    """
    n = len(signal)
    autocorr = np.correlate(signal, signal, mode='full')
    return autocorr[n-100:]


# Load the WAV file
filename = 'test4_long.wav'
# Load in mono and keep the original sampling rate
signal, sr = librosa.load(filename, sr=None, mono=True)

# Calculate autocorrelation
autocorr = compute_autocorrelation(signal)

# Try finding peaks directly using scipy.signal
# ", _" is used to capture only the peaks array
peaks, _ = find_peaks(autocorr)
# Sample a larger set of peaks, taking the first 10 here
print("Distance using find_peaks method:", 343 * (peaks[3] - peaks[2]) / sr, "m")  # likely affected by reverberations

# Display the autocorrelation
plt.figure(figsize=(10, 4))
plt.plot(autocorr)
plt.title('Autocorrelation of the Audio Signal')
plt.xlabel('Lag')
plt.ylabel('Autocorrelation')
plt.show()
