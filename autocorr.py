import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def autocorrelation(signal):
    # Calcul de l'autocorrélation d'un signal
    n = len(signal)
    autocorr = np.correlate(signal, signal, mode='full')
    return autocorr[n-100:]


# Charger le fichier WAV
filename = 'test4_long.wav'
# Charger en mono et conserver la fréquence d'origine
signal, sr = librosa.load(filename, sr=None, mono=True)

# Calculer l'autocorrélation
autocorr = autocorrelation(signal)

# # Delta vu entre les deux premiers pics d'autocorell, en secondes
# print("temps de décalage :", (149-98.99)/sr, "s")
# # on convertit en distance et on obtient quelque chose de plutôt cohérent.
# print("distance correspondante", 343*(149-98.99)/sr, "m")

# Essayons de fin les peaks directement via scipy.signal
# ", _" permet de choper juste le tableau des pics
peaks, _ = find_peaks(autocorr)
# échantillon de pics plus grand, on prend les 10 premiers ici
print("distance avec la méthode find_peaks", 343 *
      (peaks[3]-peaks[2])/sr, "m")  # surely dû aux autres reverbs

# Afficher l'autocorrélation
plt.figure(figsize=(10, 4))
plt.plot(autocorr)
plt.title('Autocorrélation du signal audio')
plt.xlabel('Décalage')
plt.ylabel('Autocorrélation')
plt.show()
