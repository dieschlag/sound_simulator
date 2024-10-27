This project is a school project aiming to simulate sound propagation in a room, including reverberation, and reception from microphones at chosen positions.

The simulator only simulates a closed room with no external perturbations.

You can set up specific configurations by editing the scenario.py file and using available functions to specifiy parameters:

- piece(x.y.z): specifies room dimensions
- micro(x,y,z, alpha): adds new microphone at given coordinates and specific signal-to-noise ratio
- source(x,y,z,"/path/to/audio/file"): adds new audio source in sumlation at given coordinates
- absorption_coeff(east=0.2, west=0.2, north=0.2, south=0.2, ceiling=0.6, floor=0.3): activates reverberation simlation with default parameters defined
- vitesse_son: gives the speed of sound to simulate
- simuler(): launches the simulation

When simuler() is called, a new folder Signaux_micros is created in which the sounds registered by microphones is registered. New audio sources can be added in the sources folder