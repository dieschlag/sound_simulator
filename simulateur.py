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
positions_sources = []
snrs = []
sound_speed = 343

def sound_speed(speed):
    """Defines sound speed used during simulation.
    
    Args: 
        speed (positive float): speed of sound waves in medium.
        
    Returns: 
        None.
    """
    global soud_speed
    sound_speed = speed
    return None

def audio_to_signal(path):
    """Converts audio file file (identified by path) to signal.
    
    Args: 
        path (string): audio file path.
        
    Returns: 
        signal (np.ndarray): Floating point time series of audio.
    """
    
    signal, sr = librosa.load(path, sr=None)
    return signal


def adjust_signal_length(signals):
    """Adjusts signal lengths to match maximum length.
    
    Args: 
        signals (vec<signal>): vector contanining all signals
        
    Returns:
        adjusted_sgnals ([np.ndarray]): Signals of same length"""
        
    max_length = len(max([signal for signal in signals], key=len))
    adjusted_signals = []
    
    for signal in signals:
        if len(signal) < max_length:
            adjusted_signal = np.pad(signal, (0,longueur_max-len(signal)))
            adjusted_signals.append(adjusted_signal)
        else :
            adjusted_signals.append(signal)
    
    return adjusted_signals




def source(x,y,z,audio):
    """Adds an audio source to the given coordinates.
    
    Args:
        x (float): position of the source along the x axis
        y (float): position of the source along th y axis
        z (float): position of the source along the z axis
        audio ([np.ndarray]): audio signals played by the sources 
        
    Returns:
        None
    """
        
    positions_sources.append([[x,y,z],audio])
    
    return None



def micro(x,y,z,signal_to_noise):
    """Adds a microphone to the given coordinates.
    
    Args:
        x (float): position of the source along the x axis
        y (float): position of the source along th y axis
        z (float): position of the source along the z axis
        signal_to_noise (positive float): signal-to-noise ratio of the microphone 
        
    Returns:
        None
    """
    
    positions_micros.append([x,y,z])
    snrs.append(signal_to_noise)
    
    return None

def create_folder_and_save_signals(folder_name, signals, sampling_rate=44100):
    """ Creates a folder to store audio files of audio signals captured by microphones

    Args:
        folder_name (string): name of the folder in which audio files will be save
        signals: ([np.ndarray]audio signals captures by microphones
    
    Returns:
        None
    """
    
    # Creates folder to store recorded audio files, creates it if it does not exist, otherwise destroys content of file
    if not os.path.exists(folder_name):
        os.makedirs(folder_name) # Creates folder 
    else:
        # Deletes content of folder
        files_to_delete = glob.glob(os.path.join(folder_name, "*.wav"))
        for fichier in files_to_delete:
            os.remove(fichier)
    # Saves audio files as WAV files in mono mode
    for i, signal in enumerate(signals):
        nom_fichier = os.path.join(folder_name, f"signal_micro_{i+1}.wav")
        sf.write(nom_fichier, signal, sampling_rate)

    # Saves files in stereo mode, for each consecutive pair of microphones
    for i in range(len(signals) - 1):
        nom_fichier = os.path.join(folder_name, f"signal_successif_{i+1}_{i+2}.wav")
        signal_combine = np.zeros((max(len(signals[i]), len(signals[i+1])), 2))
        signal_combine[:len(signals[i]), 0] = signals[i]
        signal_combine[:len(signals[i+1]), 1] = signals[i+1]
        sf.write(nom_fichier, signal_combine, sampling_rate)


class Simulator:
    """ Simualtor class storing all elements linked to an ongoing simulation"""
    
    def __init__(self, positions_micros, position_sources, all_signal, ri_piece, vitesse_son, activer_reverb, bruits, fs=44100):
        """ Initializes the Simulator class

        Args:
            position_micros ([micros]): list of micros with coordinates 
            signals: ([np.ndarray]audio signals captures by microphones
        
        Returns:
            None
        """
        self.positions_micros = positions_micros
        self.positions_sources = positions_sources
        self.all_signal = all_signal
        self.ri_room = ri_room
        self.sound_speed = sound_speed
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
    signals = [audio_to_signal(position_sources[i][1])
            for i in range(len(position_sources))]

    # Trouver la longueur maximale parmi tous les signals
    

    # # Ajuster la longueur de tous les signals à la longueur_max
    signaux_ajustes = ajuster_longueur_signaux(signals)

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
    print("signals micros")
    print(signaux_micros)
    for i in range(len(signaux_micros)-1) :
        print(signaux_micros[i]-signaux_micros[i+1])
        print(signaux_micros[i])
    liste_des_signaux = signaux_micros
    taux_echantillonnage = 44100
    creer_dossier_et_enregistrer_signaux(
        "Signaux_micros", liste_des_signaux, taux_echantillonnage)


