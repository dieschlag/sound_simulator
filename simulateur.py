import numpy as np
import scipy.signal
import soundfile as sf
import librosa
import simpleaudio as sa
import sys
import os
import wave
import glob
from reverb import *

mic_positions = []
source_positions = []
snrs = []
sound_speed = 343
reverb = False

def set_absorption_coefficients(east=0.2, west=0.2, north=0.2, south=0.2, ceiling=0.6, floor=0.3):
    """Sets absorption coefficients for each room surface.
    
    Args:
        east (float): Absorption coefficient for the east wall.
        west (float): Absorption coefficient for the west wall.
        north (float): Absorption coefficient for the north wall.
        south (float): Absorption coefficient for the south wall.
        ceiling (float): Absorption coefficient for the ceiling.
        floor (float): Absorption coefficient for the floor.
        
    Returns:
        None
    """
    global absorption
    global reverb
    
    absorption.update({
        'east': east,
        'west': west,
        'north': north,
        'south': south,
        'ceiling': ceiling,
        'floor': floor
    })
    reverb = True
    
    return None

def set_sound_speed(speed):
    """Defines the speed of sound used during the simulation.
    
    Args: 
        speed (positive float): Speed of sound waves in the medium.
        
    Returns: 
        None.
    """
    global sound_speed
    sound_speed = speed
    return None

def audio_to_signal(path):
    """Converts an audio file (specified by path) to a signal.
    
    Args: 
        path (string): Path to the audio file.
        
    Returns: 
        signal (np.ndarray): Floating point time series of the audio.
    """
    signal, sr = librosa.load(path, sr=None)
    return signal


def adjust_signal_length(signals):
    """Adjusts the length of signals to match the maximum length.
    
    Args: 
        signals (vec<signal>): Vector containing all signals
        
    Returns:
        adjusted_signals ([np.ndarray]): Signals of the same length
    """
    max_length = len(max([signal for signal in signals], key=len))
    adjusted_signals = []
    
    for signal in signals:
        if len(signal) < max_length:
            adjusted_signal = np.pad(signal, (0, max_length - len(signal)))
            adjusted_signals.append(adjusted_signal)
        else:
            adjusted_signals.append(signal)
    
    return adjusted_signals


def add_source(x, y, z, audio):
    """Adds an audio source at the given coordinates.
    
    Args:
        x (float): Position of the source along the x-axis.
        y (float): Position of the source along the y-axis.
        z (float): Position of the source along the z-axis.
        audio ([np.ndarray]): Audio signal emitted by the source.
        
    Returns:
        None
    """
    source_positions.append([[x, y, z], audio])
    return None


def add_microphone(x, y, z, signal_to_noise):
    """Adds a microphone at the given coordinates.
    
    Args:
        x (float): Position of the microphone along the x-axis.
        y (float): Position of the microphone along the y-axis.
        z (float): Position of the microphone along the z-axis.
        signal_to_noise (positive float): Signal-to-noise ratio of the microphone.
        
    Returns:
        None
    """
    mic_positions.append([x, y, z])
    snrs.append(signal_to_noise)
    return None

def create_folder_and_save_signals(folder_name, signals, sampling_rate=44100):
    """Creates a folder to store audio files of signals captured by microphones.

    Args:
        folder_name (string): Name of the folder in which audio files will be saved.
        signals: ([np.ndarray]): Audio signals captured by the microphones.
    
    Returns:
        None
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)  # Creates folder
    else:
        # Deletes content of folder
        files_to_delete = glob.glob(os.path.join(folder_name, "*.wav"))
        for file in files_to_delete:
            os.remove(file)
    
    # Saves audio files as WAV files in mono mode
    for i, signal in enumerate(signals):
        file_name = os.path.join(folder_name, f"signal_micro_{i+1}.wav")
        sf.write(file_name, signal, sampling_rate)

    # Saves files in stereo mode, for each consecutive pair of microphones
    for i in range(len(signals) - 1):
        file_name = os.path.join(folder_name, f"signal_pair_{i+1}_{i+2}.wav")
        combined_signal = np.zeros((max(len(signals[i]), len(signals[i+1])), 2))
        combined_signal[:len(signals[i]), 0] = signals[i]
        combined_signal[:len(signals[i+1]), 1] = signals[i+1]
        sf.write(file_name, combined_signal, sampling_rate)


class Simulator:
    """Simulator class storing all elements related to an ongoing simulation."""
    
    def __init__(self, mic_positions, source_positions, all_signals, room_ir, sound_speed, reverb, snrs, fs=44100):
        
        """Initializes the Simulator class.

        Args:
            mic_positions ([micros]): List of microphone positions with coordinates.
            source_positions: ([np.ndarray]): Audio signals captured by microphones.
        
        Returns:
            None
        """
        self.mic_positions = mic_positions
        self.source_positions = source_positions
        self.all_signals = all_signals
        self.room_ir = room_ir
        self.sound_speed = sound_speed
        self.reverb = reverb
        self.snrs = snrs
        self.fs = fs

    def simulate_propagation_attenuation(self, signal, distance):
        propagation_time = distance / self.sound_speed
        delay_samples = int(propagation_time * self.fs)
        attenuation = 1 / (distance**2)
        propagated_signal = np.pad(signal, (delay_samples, 0), 'constant')[:-delay_samples]
        return propagated_signal * attenuation
    
    def apply_reverberation(self, signal, reverb):
        if self.reverb:
            # Applying reverb by convolving with a Fourier series
            return scipy.signal.fftconvolve(signal, self.room_ir, mode='full')[:len(signal)]
        else:
            print(reverb)
            print("No reverberation applied.")
            return signal

    def generate_noise(self, signal, noise_level):
        signal_power = np.mean(signal**2)
        snr_ratio = 10**(noise_level / 10)
        noise_power = signal_power / snr_ratio
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
        return noise

    def simulate_microphones(self, source_positions, reverb):
        mic_signals = []
        
        for mic in self.mic_positions:
            mic_signal = np.zeros(len(max([signal for signal in self.all_signals], key=len)))
            for i in range(len(source_positions)):
                # Calculate distance from source position to microphone
                distance = np.linalg.norm(np.array(source_positions[i][0]) - np.array(mic))
                propagated_signal = self.simulate_propagation_attenuation(self.all_signals[i], distance)
                reverberated_signal = self.apply_reverberation(propagated_signal, reverb)
                mic_noise = self.generate_noise(reverberated_signal, self.snrs[i])
                mic_signal += reverberated_signal + mic_noise  # Superposition of signals
            mic_signals.append(mic_signal)
        return mic_signals


def simulate():
    print("simulate")
    print(room_dimensions)
    print(absorption)
    print(sound_speed)  

    # Example signal loading and processing
    signals = [audio_to_signal(source_positions[i][1]) for i in range(len(source_positions))]
    adjusted_signals = adjust_signal_length(signals)
    
    all_signals = adjusted_signals
    sources = [item[0] for item in source_positions]
    room_ir = 0
    if reverb:
        room_ir = compute_room_impulse_response(absorption, room_dimensions, sources, mic_positions)

    simulator = Simulator(mic_positions, source_positions, all_signals, room_ir, sound_speed, reverb, snrs)
    mic_signals = simulator.simulate_microphones(source_positions, reverb)
    
    signal_list = mic_signals
    sampling_rate = 44100
    create_folder_and_save_signals("Microphone_Signals", signal_list, sampling_rate)
