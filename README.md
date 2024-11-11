This project is a school project aiming to simulate sound propagation in a room, including reverberation, and reception from microphones at chosen positions.

The simulator only simulates a closed room with no external perturbations.

You can set up specific configurations by editing the scenario.py file and using available functions to specifiy parameters:

- set_room_dimensions(x.y.z): specifies room dimensions
- add_micro(x,y,z, alpha): adds new microphone at given coordinates and specific signal-to-noise ratio
- add_source(x,y,z,"/path/to/audio/file"): adds new audio source in sumlation at given coordinates
- set_absorption_coefficients(east=0.2, west=0.2, north=0.2, south=0.2, ceiling=0.6, floor=0.3): activates reverberation simlation with default parameters defined
- set_sound_speed: sets the speed of sound to simulate
- simulate(): launches the simulation

When simuler() is called, a new folder Signaux_micros is created in which the sounds registered by microphones is registered. New audio sources can be added in the sources folder.

The reverberation is applied by convoluting an impulse response to the sound signal. The impulse response is the propagation of an impulse in the room, generated using the library pyroomacoustics. The convolution is applied with scipy.signal.fftconvolve.

