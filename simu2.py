import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
import pyroomacoustics as pra
import soundfile as sf
import simpleaudio as sa

# The desired reverberation time and dimensions of the room
rt60 = 0.5  # seconds
room_dim = [9, 7.5, 3.5]  # meters

# We invert Sabine's formula to obtain the parameters for the ISM simulator
e_absorption, max_order = pra.inverse_sabine(rt60, room_dim)

# Create the room
room = pra.ShoeBox(
    room_dim, fs=16000, materials=pra.Material(e_absorption), max_order=max_order
)


# import a mono wavfile as the source signal
# the sampling frequency should match that of the room
_, audio = wavfile.read('test3_short.wav')

# place the source in the room
room.add_source([2.5, 3.73, 1.76], signal=audio, delay=1.3)

# define the locations of the microphones
mic_locs = np.c_[
    [6.3, 4.87, 1.2],  # mic 1
    [6.3, 4.93, 1.2],  # mic 2
]

# finally place the array in the room
room.add_microphone_array(mic_locs)

room.compute_rir()

# plot the RIR between mic 1 and source 0
plt.plot(room.rir[1][0])
plt.show()


sf.write("test_result_simu2.wav", room.rir[1][0], 44100)

wave_obj = sa.WaveObject.from_wave_file("test_result_simu2.wav")
play_obj = wave_obj.play()
play_obj.wait_done()  # pour s'écouter le résultat
