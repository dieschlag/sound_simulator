import pyroomacoustics as pra
import numpy as np
import scipy.signal
import librosa
import soundfile as sf
import simpleaudio as sa

# Room dimensions (width, length, height) in meters

room_dimensions = []

def set_room_dimensions(width=5.0, length=10.0, height=2):
    """Sets the dimensions of the room."""
    params = [width, length, height]
    for item in params:
        room_dimensions.append(item)
    return None

# Absorption coefficients for each surface of the room
absorption = {}



def compute_room_impulse_response(absorption, room_dimensions, source_positions, microphone_positions):
    """Computes the room impulse response using pyroomacoustics.

    Args:
        absorption (dict): Dictionary of absorption coefficients for each surface.
        room_dimensions (list): List containing the width, length, and height of the room.
        source_positions (list): List of coordinates for each audio source.
        microphone_positions (list): List of coordinates for each microphone.

    Returns:
        np.ndarray: reverberated signal received at the microphone.
    """
    # Creating a sample audio signal (as an impulse signal)
    signal_duration = 1  # in seconds
    fs = 44100  # sampling frequency
    t = np.linspace(0, signal_duration, int(fs * signal_duration), endpoint=False)
    signal = np.zeros_like(t)
    signal[0] = 1  # Creates an impulse at the start of the signal

    # Create the room
    room = pra.ShoeBox(room_dimensions, absorption=absorption, max_order=10, fs=fs)

    # Add sources to the room with the defined signal
    for position in source_positions:
        room.add_source(position, signal=signal)

    # Add microphones at specified positions
    for position in microphone_positions:
        position_array = np.array([position]).T  # Transpose to get a 2D list (or use np.array(position).reshape(-1, len(position)))
        room.add_microphone_array(pra.MicrophoneArray(position_array, fs=44100))

    # Simulation
    room.simulate()

    # Retrieve the reverberated signal at the microphone
    return room.mic_array.signals[0, :]
