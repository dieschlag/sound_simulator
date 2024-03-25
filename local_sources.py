import numpy as np
import librosa
from scipy.signal import correlate
from scipy.optimize import minimize

def charger_signal(fichier):
    signal, sr = librosa.load(fichier, sr=None)
    return signal, sr

def calculer_tdoa(signal1, signal2, fs):
    correlation = correlate(signal1, signal2, mode='full', method='fft')
    decalage = correlation.argmax() - (len(signal1) - 1)
    tdoa = decalage / fs
    return tdoa

def fonction_objectif(X, positions_mics, tdoas, vitesse_son=343):
    erreurs = []
    for i in range(len(tdoas)):
        distance1 = np.linalg.norm(X - positions_mics[0])
        distance2 = np.linalg.norm(X - positions_mics[i + 1])
        tdoa_calculee = (distance2 - distance1) / vitesse_son
        erreurs.append((tdoa_calculee - tdoas[i]) ** 2)
    return sum(erreurs)

def localiser_source(positions_mics, tdoas):
    resultat = minimize(fonction_objectif, np.array([0, 0]), args=(positions_mics, tdoas), method='Nelder-Mead')
    return resultat.x

# Positions des microphones (à définir selon votre configuration)
positions_mics = ([1, 3], [2, 3], [3, 3])
# Pour chaque source, vous devez identifier les segments temporels où elle est active
# et charger ces segments pour chaque microphone
# Exemple : segments_source1 = [('micro1_source1.wav', 'micro2_source1.wav', 'micro3_source1.wav'), ...]

positions_sources = []

for segments_source in segments_sources:
    signaux = [charger_signal(fichier)[0] for fichier in segments_source]
    fs = charger_signal(segments_source[0])[1]  # Supposé identique pour tous les fichiers
    tdoas = [calculer_tdoa(signaux[0], signal, fs) for signal in signaux[1:]]

    position_source = localiser_source(positions_mics, tdoas)
    positions_sources.append(position_source)

print(f"Positions estimées des sources sonores : {positions_sources}")
