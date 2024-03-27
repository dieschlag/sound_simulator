import pyroomacoustics as pra
import numpy as np
import scipy.signal
import librosa
import soundfile as sf
import simpleaudio as sa


# Dimensions de la pièce (largeur, longueur, hauteur) en mètres

dimensions_piece = []

def piece(largeur=5.0, longueur=10.0, hauteur=2):
    param =  [largeur, longueur, hauteur]
    for item in param:
        dimensions_piece.append(item)
    return None
    


# Coefficients d'absorption pour chaque surface de la pièce

absorption = {}

def absorption_coeff(east=0.2, west=0.2, north=0.2, south=0.2, ceiling=0.6, floor=0.3):
    global absorption
    absorption.update({
        'east': east,
        'west': west,
        'north': north,
        'south': south,
        'ceiling': ceiling,
        'floor': floor
    })
    print(absorption)
    return absorption
    
     

def ri(absorption, dimensions_piece, source_positions, microphone_positions) :

    # Création d'un signal audio exemple (comme un signal impulsionnel)
    duree_signal = 1  # en secondes
    fs = 44100  # fréquence d'échantillonnage
    t = np.linspace(0, duree_signal, int(fs * duree_signal), endpoint=False)
    signal = np.zeros_like(t)
    signal[0] = 1  # Création d'une impulsion au début du signal

    # Création de la pièce
    piece = pra.ShoeBox(dimensions_piece, absorption=absorption,
                        max_order=10, fs=fs)

    # Ajout de la source à la pièce avec le signal défini
    # source_position = [2, 3.5, 1.2]  # Position de la source (x, y, z) en mètres
    # # Assurez-vous d'ajouter le signal ici
    # piece.add_source(source_position, signal=signal)

    for position in source_positions:
        piece.add_source(position, signal=signal)


    # Position du microphone

    for position in microphone_positions:
        position_array = np.array([position]).T  # Transposer pour obtenir une liste 2D (ou utiliser np.array(position).reshape(-1, len(position)))
        piece.add_microphone_array(pra.MicrophoneArray(position_array, fs=44100))
    # micro = np.array([[2.5, 1, 1.5]]).T  # Coordonnées (x, y, z) en mètres
    # piece.add_microphone_array(pra.MicrophoneArray(micro, fs=fs))

    # Simulation
    piece.simulate()

    # Récupération du signal réverbéré au microphone
    return piece.mic_array.signals[0, :]

    # sf.write("test_reverb1.wav", ri, 44100)

    # wave_obj = sa.WaveObject.from_wave_file("test_reverb1.wav")
    # play_obj = wave_obj.play()
    # play_obj.wait_done()  # pour s'écouter le résultat
