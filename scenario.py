from simulateur import *

set_absorption_coefficients()
add_source(10, 10, 1.5, "sources/Audio6.wav")
add_microphone(1, 1, 1.5, 40)
add_microphone(1, 0.8, 1.5, 40)
add_microphone(1, 19, 1.5, 40)
add_microphone(1, 19.2, 1.5 ,40)

set_room_dimensions(10, 20, 4)
set_sound_speed(343)

simulate()

