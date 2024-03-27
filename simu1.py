import numpy as np
import scipy.signal
import soundfile as sf
import librosa
import soundfile as sf
import simpleaudio as sa
import sys
import os
import wave
import glob
from reverb import *

positions_micros = []
position_sources = []
vitesse_son = 343

def vitesse_son(vitesse):
    global vitesse_son
    vitesse_son = vitesse
    return None

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




def source(x,y,z,audio):
    position_sources.append([[x,y,z],audio])
    return None



def micro(x,y,z):
    positions_micros.append([x,y,z])
    return None

def creer_dossier_et_enregistrer_signaux(nom_dossier, signaux, taux_echantillonnage=44100):
    """
    Crée un dossier et enregistre une liste de signaux audio dans ce dossier.

    :param nom_dossier: Nom du dossier à créer.
    :param signaux: Liste des signaux audio à enregistrer (chaque signal est un tableau NumPy).
    :param taux_echantillonnage: Taux d'échantillonnage des signaux audio (en Hz).
    """
    # Créer le dossier si celui-ci n'existe pas et retire les fichiers dans le dossier si ce dernier existe déjà
    if not os.path.exists(nom_dossier):
        os.makedirs(nom_dossier)
    else:
        # Supprimer tous les fichiers existants dans le dossier
        fichiers_a_supprimer = glob.glob(os.path.join(nom_dossier, "*.wav"))
        for fichier in fichiers_a_supprimer:
            os.remove(fichier)

    # Enregistrer chaque signal dans le dossier sous forme de fichier WAV
    for i, signal in enumerate(signaux):
        nom_fichier = os.path.join(nom_dossier, f"signal_micro_{i+1}.wav")
        sf.write(nom_fichier, signal, taux_echantillonnage)
        print(f"Signal {i+1} enregistré sous : {nom_fichier}")
    
    for i, signal in enumerate(signaux):
        

        # Si ce n'est pas le dernier signal
        if i < len(signaux) - 1:
            nom_fichier = os.path.join(nom_dossier, f"signal_successif_{i+1}_{i+2}.wav")
            # Superposer le signal actuel avec le suivant
            signal = signal + signaux[i + 1]
            # Enregistrer le signal dans un fichier WAV
            sf.write(nom_fichier, signal, taux_echantillonnage)
            print(f"Signaux {i+1} et {i+2} supperposés et enregistrés sous : {nom_fichier}")

class Simulateur:
    def __init__(self, positions_micros, position_sources, all_signal, ri_piece, vitesse_son, fs=44100, snr_db=40):
        self.positions_micros = positions_micros
        self.position_sources = position_sources
        self.all_signal = all_signal
        self.ri_piece = ri_piece
        self.vitesse_son = vitesse_son
        self.fs = fs
        self.snr_db = snr_db

    def simuler_propagation_attenuation(self, signal, distance):
        temps_propagation = distance / self.vitesse_son
        print("distance :")
        print(distance)
        echantillons_retard = int(temps_propagation * self.fs)
        print("echantillon retard:")
        print(echantillons_retard)
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
        
        for micro in self.positions_micros:
            signal_micro = 0
            for i in range(len(positions_source)):
                # distance de la positions_source au micro
                distance = np.linalg.norm(
                    np.array(positions_source[i][0]) - np.array(micro))
                print(distance)
                print(self.all_signal[i])
                signal_propage = self.simuler_propagation_attenuation(
                    self.all_signal[i], distance)
                print("signal_propage")
                print(signal_propage)
                signal_reverbere = self.appliquer_reverberation(
                    signal_propage, activer_reverb)
                print("signal_reverbe")
                print(signal_reverbere)
                bruit_micro = self.generer_bruit(signal_reverbere)
                print("bruit_micro")
                signal_micro += signal_reverbere + bruit_micro  # superposition
                print(signal_micro)
            signaux_micros.append(signal_micro)
        return signaux_micros



def simu():

    print(dimensions_piece)
    print(absorption)
    print(vitesse_son)  

    # dimensions_piece = piece()
    # absorption = absorption_coeff()

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

    simulateur = Simulateur(positions_micros, position_sources, all_signal, ri_piece, vitesse_son)
    signaux_micros = simulateur.simuler_microphones(position_sources)
    print("signaux micros")
    print(signaux_micros)
    for signal in signaux_micros :
        print("signal micro:")
        print(signal)
    liste_des_signaux = signaux_micros
    taux_echantillonnage = 44100
    creer_dossier_et_enregistrer_signaux(
        "Signaux_micros", liste_des_signaux, taux_echantillonnage)


