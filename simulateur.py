import numpy as np
import scipy.signal
import soundfile as sf


class Simulateur:
    def __init__(self, positions_micros, ri_piece, vitesse_son=343, fs=44100):
        self.positions_micros = positions_micros
        self.ri_piece = ri_piece
        self.vitesse_son = vitesse_son
        self.fs = fs

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

    def generer_bruit(self, longueur, niveau_db):
        puissance_bruit = 10**(niveau_db / 10)
        return np.random.normal(0, np.sqrt(puissance_bruit), longueur)

    def simuler_microphones(self, signal, source, bruit_ambiant, niveau_bruit_micro_db, activer_reverb=True):
        signaux_micros = []
        for micro in self.positions_micros:
            # distance de la source au micro
            distance = np.linalg.norm(np.array(source) - np.array(micro))
            signal_propage = self.simuler_propagation_attenuation(
                signal, distance)
            signal_reverbere = self.appliquer_reverberation(
                signal_propage, activer_reverb)
            bruit_micro = self.generer_bruit(
                len(signal_reverbere), niveau_bruit_micro_db)
            signal_micro = signal_reverbere + bruit_micro + bruit_ambiant
            signaux_micros.append(signal_micro)
        return signaux_micros


positions_micros = [...]  # positions des micros
ri_piece = [...]  # RI locale
simulateur = Simulateur(positions_micros, ri_piece)
source = [...]  # Position de la source
# bruit_ambiant = simulateur.generer_bruit(longueur_signal, niveau_bruit_ambiant_db)
# signaux_micros = simulateur.simuler_microphones(signal, source, bruit_ambiant, niveau_bruit_micro_db)
