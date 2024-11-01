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
bruits = []
vitesse_son = 343

def vitesse_son(vitesse):
    global vitesse_son
    vitesse_son = vitesse
    return None

def audio_to_signal(chemin):
    """Convertit un fichier audio en un signal NumPy."""
    signal, sr = librosa.load(chemin, sr=None)
    print("signal")
    print(signal)
    return signal


def ajuster_longueur_signaux(signaux):
    """Ajuste la longueur de tous les signaux à la longueur_max."""
    longueur_max = len(max([signal for signal in signaux], key=len))
    signaux_ajustes = []
    for signal in signaux:
        if len(signal) < longueur_max:
            signal_ajuste = np.pad(signal, (0,longueur_max-len(signal)))
            signaux_ajustes.append(signal_ajuste)
        else :
            signaux_ajustes.append(signal)
    return signaux_ajustes




def source(x,y,z,audio):
    position_sources.append([[x,y,z],audio])
    return None



def micro(x,y,z,bruit):
    positions_micros.append([x,y,z])
    bruits.append(bruit)
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

    for i in range(len(signaux) - 1):
        nom_fichier = os.path.join(nom_dossier, f"signal_successif_{i+1}_{i+2}.wav")
        # Créer un tableau vide pour le signal combiné
        signal_combine = np.zeros((max(len(signaux[i]), len(signaux[i+1])), 2))
        # Assigner le son du microphone i à l'oreille gauche
        signal_combine[:len(signaux[i]), 0] = signaux[i]
        # Assigner le son du microphone i+1 à l'oreille droite
        signal_combine[:len(signaux[i+1]), 1] = signaux[i+1]
        # Enregistrer le signal combiné dans un fichier WAV
        sf.write(nom_fichier, signal_combine, taux_echantillonnage)
        print(f"Signaux {i+1} et {i+2} superposés et enregistrés sous : {nom_fichier}")

class Simulateur:
    def __init__(self, positions_micros, position_sources, all_signal, ri_piece, vitesse_son, activer_reverb, bruits, fs=44100):
        self.positions_micros = positions_micros
        self.position_sources = position_sources
        self.all_signal = all_signal
        self.ri_piece = ri_piece
        self.vitesse_son = vitesse_son
        self.activer_reverb = activer_reverb
        self.bruits = bruits
        self.fs = fs

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
    
    def appliquer_reverberation(self, signal, activer_reverb):
        if self.activer_reverb:
            # convolution avec Fourier rapide
            return scipy.signal.fftconvolve(signal, self.ri_piece, mode='full')[:len(signal)]
        else:
            print("nope")
            return signal

    def generer_bruit(self, signal, bruit):
        puissance_signal = np.mean(signal**2)
        ratio_snr = 10**(bruit / 10)
        puissance_bruit = puissance_signal / ratio_snr
        bruit = np.random.normal(0, np.sqrt(puissance_bruit), len(signal))
        return bruit

    def simuler_microphones(self, positions_source, activer_reverbs):
        signaux_micros = []
        signal_reverbere = []
        signal_propage = []
        
        for (i, micro) in enumerate(self.positions_micros):
            signal_micro = np.zeros(len(max([signal for signal in self.all_signal], key=len)))
            # print("toutes les listes")
            # print([signal for signal in self.all_signal])
            # print("taille maximale")
            # print(len(max([signal for signal in self.all_signal], key=len)))
            for i in range(len(positions_source)):
                # distance de la positions_source au micro
                distance = np.linalg.norm(
                    np.array(positions_source[i][0]) - np.array(micro))
                print("position source")
                print(positions_source[i][0])
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
                bruit_micro = self.generer_bruit(signal_reverbere, self.bruits[i])
                print("bruit_micro")
                signal_micro += signal_reverbere + bruit_micro  # superposition
                print(signal_micro)
            signaux_micros.append(signal_micro)
        return signaux_micros



def simuler():

    print(dimensions_piece)
    print(absorption)
    print(vitesse_son)  

    # dimensions_piece = piece()
    # absorption = absorption_coeff()

    # chemin_du_dossier = input(
    # "Entrez le chemin du dossier contenant les fichiers audio : ")

    # fichiers_audio = lister_fichiers(chemin_du_dossier)
    signaux = [audio_to_signal(position_sources[i][1])
            for i in range(len(position_sources))]

    # Trouver la longueur maximale parmi tous les signaux
    

    # # Ajuster la longueur de tous les signaux à la longueur_max
    signaux_ajustes = ajuster_longueur_signaux(signaux)

    all_signal = signaux_ajustes
    sources= [item[0] for item in position_sources]
    print(all_signal)
    print(sources)
    print(absorption)
    ri_piece = 0
    if activer_reverb:
        ri_piece = ri(absorption, dimensions_piece, sources, positions_micros)

    simulateur = Simulateur(positions_micros, position_sources, all_signal, ri_piece, vitesse_son, activer_reverb, bruits)
    signaux_micros = simulateur.simuler_microphones(position_sources, activer_reverb)
    print("signaux micros")
    print(signaux_micros)
    for i in range(len(signaux_micros)-1) :
        print(signaux_micros[i]-signaux_micros[i+1])
        print(signaux_micros[i])
    liste_des_signaux = signaux_micros
    taux_echantillonnage = 44100
    creer_dossier_et_enregistrer_signaux(
        "Signaux_micros", liste_des_signaux, taux_echantillonnage)


