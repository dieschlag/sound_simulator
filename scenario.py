from simu1 import *
from reverb import *

"""
-------------------------------------------------------------------------------------------
A modifier
-------------------------------------------------------------------------------------------
"""


### Rajouter sources et micros :
source(2.5, 5, 1, "Audio6")
micro(2,1,1.5)
micro(2.2.5,1.2.5,1.5)
micro(2.4,1,1.5)
micro(2.6,1,1.5)
micro(2.8,1,1.5)
micro(3,1,1.5)

### Modifier les constantes :

dimensions_piece = piece()
absorption = absorption_coeff()
vitesse_son = 343
fs = 44100
snr_db = 40


"""
-------------------------------------------------------------------------------------------
Ne pas modifier
-------------------------------------------------------------------------------------------
"""

chemin_du_dossier = input(
"Entrez le chemin du dossier contenant les fichiers audio : ")

fichiers_audio = lister_fichiers(chemin_du_dossier)
signaux = [audio_to_signal(chemin_du_dossier, position_sources[i][1] + ".wav")
           for i in range(len(position_sources))]

# Trouver la longueur maximale parmi tous les signaux
longueur_max = int(np.min([len(signal) for signal in signaux]))

# Ajuster la longueur de tous les signaux à la longueur_max
signaux_ajustes = ajuster_longueur_signaux(signaux, longueur_max)

all_signal = signaux_ajustes
sources= [item[0] for item in position_sources]
print(all_signal)
print(sources)
print(absorption)

ri_piece = ri(absorption, dimensions_piece, sources, positions_micros)

simulateur = Simulateur(positions_micros, position_sources, all_signal, ri_piece)
signaux_micros = simulateur.simuler_microphones(position_sources)
liste_des_signaux = signaux_micros
taux_echantillonnage = 44100
creer_dossier_et_enregistrer_signaux(
    "Signaux_micros", liste_des_signaux, taux_echantillonnage)

