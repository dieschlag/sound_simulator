from simu1 import *
from reverb import *

"""
-------------------------------------------------------------------------------------------
A modifier
-------------------------------------------------------------------------------------------
"""


### Rajouter sources et micros :
source(1, 5, 1, "Audio6")
micro(1,1,1.5)
micro(1.2,1,1.5)
# micro(2.4,1,1.5)
# micro(2.6,1,1.5)
micro(9,1,1.5)
micro(8.8,1,1.5)

### Modifier les constantes :

piece(10, 20, 4)
absorption_coeff()
vitesse_son(343)
# vitesse_son = 343
fs = 44100
snr_db = 40

simu()


"""
-------------------------------------------------------------------------------------------
Ne pas modifier
-------------------------------------------------------------------------------------------
"""

