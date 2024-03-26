from simu1 import *

"""
-------------------------------------------------------------------------------------------
A modifier
-------------------------------------------------------------------------------------------
"""


### Rajouter sources et micros :
source(3, 3, 4, "Audio5")
print(position_sources)
source(4,4,4, "Audio6")
print(position_sources)

micro(5,5,5)
print(positions_micros)

### Modifier les constantes :




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
print(all_signal)

simulateur = Simulateur(positions_micros, position_sources, all_signal, ri_piece)
signaux_micros = simulateur.simuler_microphones(position_sources)
liste_des_signaux = signaux_micros
taux_echantillonnage = 44100
creer_dossier_et_enregistrer_signaux(
    "Signaux_micros", liste_des_signaux, taux_echantillonnage)

