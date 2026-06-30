import librosa
import numpy as np
import matplotlib.pyplot as plt

filename = "sample.wav"

y, sr = librosa.load(filename)

# y is amplitude of wave, sr is frequency of sampling
# so, at each instance it takes the amplitude and stores it in an array
print(f"loaded {len(y)} samples at {sr} Hz")
print(f"{len(y) / sr:.5f} seconds")

# np.arange(leny) / sr bc $\frac{samples}{\frac{samples}{second}}$ = seconds
time = np.arange(len(y)) / sr

plt.figure(figsize=(10,4))
plt.plot(time, y)
plt.xlabel("Time (s)")
plt.ylabel("Waveform amp / time")
plt.grid(True)
plt.show()