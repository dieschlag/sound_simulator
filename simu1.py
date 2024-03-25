import numpy as np
import scipy.signal
import soundfile as sf
import librosa
import soundfile as sf
import simpleaudio as sa
import sys
import os
from reverb import ri
import wave


def lister_fichiers(dossier):
    """Liste tous les fichiers audio dans le dossier spécifié."""
    fichiers_liste = []
    for fichier in os.listdir(dossier):
        if fichier.endswith((".wav", ".mp3")):  # Ajoutez d'autres formats au besoin
            fichiers_liste.append(fichier)
    return fichiers_liste


def audio_to_signal(dossier, fichier_audio):
    """Convertit un fichier audio en un signal NumPy."""
    chemin_complet = os.path.join(dossier, fichier_audio)
    signal, sr = librosa.load(chemin_complet, sr=None)
    return signal


def ajuster_longueur_signaux(signaux, longueur_max):
    """Ajuste la longueur de tous les signaux à la longueur_max."""
    signaux_ajustes = []
    for signal in signaux:
        signal_ajuste = signal[:longueur_max]
        signaux_ajustes.append(signal_ajuste)
    return signaux_ajustes


chemin_du_dossier = input(
    "Entrez le chemin du dossier contenant les fichiers audio : ")

fichiers_audio = lister_fichiers(chemin_du_dossier)
signaux = [audio_to_signal(chemin_du_dossier, fichier)
           for fichier in fichiers_audio]

# Trouver la longueur maximale parmi tous les signaux
longueur_max = int(np.min([len(signal) for signal in signaux]))

# Ajuster la longueur de tous les signaux à la longueur_max
signaux_ajustes = ajuster_longueur_signaux(signaux, longueur_max)

all_signal = signaux_ajustes


class Simulateur:
    def __init__(self, positions_micros, position_sources, ri_piece, vitesse_son=343, fs=44100, snr_db=40):
        self.positions_micros = positions_micros
        self.position_sources = position_sources
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

    def simuler_microphones(self, positions_source, activer_reverb=True):
        signaux_micros = []
        signal_reverbere = []
        signal_propage = []
        signal_micro = 0
        for micro in self.positions_micros:
            for i in range(len(positions_source)):
                # distance de la positions_source au micro
                distance = np.linalg.norm(
                    np.array(positions_source[i]) - np.array(micro))
                signal_propage = self.simuler_propagation_attenuation(
                    all_signal[i], distance)

                signal_reverbere = self.appliquer_reverberation(
                    signal_propage, activer_reverb)

                bruit_micro = self.generer_bruit(signal_reverbere)

                signal_micro += signal_reverbere + bruit_micro  # superposition

            signaux_micros.append(signal_micro)
        return signaux_micros


signal, sr = librosa.load("sources/"+fichiers_audio[0], sr=None)
positions_micros = ([1, 3], [2, 3], [3, 3])  # positions des micros

# Position de la positions_source
position_sources = [[2.5, 1], [2, 1], [1.5, 1]]


# On génère une RI synthétique pour ri_piece :
# Paramètres de la RI synthétique

duree_s = len(signal)*sr
frequence_echantillonnage = sr
nbr_reflexions = 5  # Nombre de réflexions
decroissance = 0.8  # Facteur de décroissance des réflexions

taille_echantillon = len(signal)
ri_piece = ri

simulateur = Simulateur(positions_micros, position_sources, ri_piece)

# supposons qu'il n'y a pas de bruit ambiant (0dB)
# signal, sr = librosa.load("test3_short.wav", sr=None)
# positions_source = [[2, 1]]  # Position de la positions_source du bruit ambiant

signaux_micros = simulateur.simuler_microphones(position_sources)

# sf.write("test_result_mic4.wav", signaux_micros[2], 44100)

# wave_obj = sa.WaveObject.from_wave_file("test_result_mic4.wav")
# play_obj = wave_obj.play()
# play_obj.wait_done()  # pour s'écouter le résultat


def creer_dossier_et_enregistrer_signaux(nom_dossier, signaux, taux_echantillonnage=44100):
    """
    Crée un dossier et enregistre une liste de signaux audio dans ce dossier.

    :param nom_dossier: Nom du dossier à créer.
    :param signaux: Liste des signaux audio à enregistrer (chaque signal est un tableau NumPy).
    :param taux_echantillonnage: Taux d'échantillonnage des signaux audio (en Hz).
    """
    # Créer le dossier si celui-ci n'existe pas
    if not os.path.exists(nom_dossier):
        os.makedirs(nom_dossier)

    # Enregistrer chaque signal dans le dossier sous forme de fichier WAV
    for i, signal in enumerate(signaux):
        nom_fichier = os.path.join(nom_dossier, f"signal_micro_{i+1}.wav")
        sf.write(nom_fichier, signal, taux_echantillonnage)
        print(f"Signal {i+1} enregistré sous : {nom_fichier}")

# Exemple d'utilisation
# `taux_echantillonnage` doit correspondre au taux d'échantillonnage des signaux contenus dans `liste_des_signaux`


liste_des_signaux = signaux_micros  # Votre liste de signaux ici
# Taux d'échantillonnage des signaux (à ajuster selon vos données)
taux_echantillonnage = 44100

creer_dossier_et_enregistrer_signaux(
    "Signaux_micros", liste_des_signaux, taux_echantillonnage)
