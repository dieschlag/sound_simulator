from simulateur import *

source(2.5, 5, 1, "sources/Audio6.wav")

micro(1, 1, 1.5, 40)
micro(1.25, 1, 1.5, 40)
micro(2.5, 1, 1.5, 40)
micro(3.75, 1, 1.5, 40)
micro(4, 1, 1, 40)

piece(5, 10, 2)
absorption_coeff(east=0.2, west=0.2, north=0.2, south=0.2, ceiling=0.6, floor=0.3)
vitesse_son(343)

simuler()