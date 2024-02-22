import numpy as np
import scipy.signal
import soundfile as sf
import librosa
import soundfile as sf


class Simulateur:
    def __init__(self, positions_micros, ri_piece, vitesse_son=343, fs=44100, snr_db=40):
        self.positions_micros = positions_micros
        self.ri_piece = ri_piece
        self.vitesse_son = vitesse_son
        self.fs = fs
        self.snr_db = snr_db

    def simuler_propagation_attenuation(self, signal, distance):
        temps_propagation = distance / self.vitesse_son
        echantillons_retard = int(temps_propagation * self.fs)
        attenuation = 1 / (distance**2)
        signal_propage = np.pad(signal, (echantillons_retard, 0), 'constant')[
            :-echantillons_retard]
        return signal_propage * attenuation

    def appliquer_reverberation(self, signal, activer_reverb=True):
        if activer_reverb:
            # convolution avec Fourier rapide
            return scipy.signal.fftconvolve(signal, self.ri_piece, mode='full')[:len(signal)]
        else:
            return signal

    def generer_bruit(self, signal):
        puissance_signal = np.mean(signal**2)
        ratio_snr = 10**(self.snr_db / 10)
        puissance_bruit = puissance_signal / ratio_snr
        bruit = np.random.normal(0, np.sqrt(puissance_bruit), len(signal))
        return bruit

    def simuler_microphones(self, signal, source, bruit_ambiant, activer_reverb=True):
        signaux_micros = []
        for micro in self.positions_micros:
            # distance de la source au micro
            distance = np.linalg.norm(np.array(source) - np.array(micro))
            signal_propage = self.simuler_propagation_attenuation(
                signal, distance)

            signal_reverbere = self.appliquer_reverberation(
                signal_propage, activer_reverb)

            bruit_micro = self.generer_bruit(signal_reverbere)

            signal_micro = signal_reverbere + bruit_micro + bruit_ambiant  # superposition
            signaux_micros.append(signal_micro)
        return signaux_micros


signal, sr = librosa.load("test3_short.wav", sr=None)
positions_micros = ([1, 3], [2, 3], [3, 3])  # positions des micros
source = [[2, 1]]  # Position de la source


# On génère une RI synthétique pour ri_piece :
# Paramètres de la RI synthétique

duree_s = len(signal)*sr
frequence_echantillonnage = sr
nbr_reflexions = 50  # Nombre de réflexions
decroissance = 0.9  # Facteur de décroissance des réflexions

taille_echantillon = len(signal)
ri_piece = np.zeros(taille_echantillon)

for i in range(nbr_reflexions):
    # Position de l'impulsion pour chaque réflexion
    position = int((i / nbr_reflexions) * taille_echantillon)
    # Amplitude décroissante pour chaque réflexion
    amplitude = decroissance ** i
    ri_piece[position] = amplitude


simulateur = Simulateur(positions_micros, ri_piece)

# # supposons qu'il n'y a pas de bruit ambiant (0dB)
# niveau_bruit_ambiant_db = 0
# bruit_ambiant = simulateur.generer_bruit(
# )  # de même longueur que le signal

# signaux_micros = simulateur.simuler_microphones(
#     signal, source, bruit_ambiant=0)

# sf.write("test_result.wav", signaux_micros[0], 44100)
