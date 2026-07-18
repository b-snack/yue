from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from notes import piano_notes

CHUNK = 50
SPEED_OF_SOUND = 340 # m \cdot s^(-1)

filename = "sample.wav"

sr, y = wavfile.read(filename)

if y.dtype != np.float32:
  y=y.astype(np.float32) / np.iinfo(y.dtype).max

if len(y.shape) > 1:
  y=np.mean(y, axis=1)

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

y_fft = np.fft.rfft(y)
# nps.abs strips the phase and takes the magnitude bc phase is not needed. 

amp = np.abs(y_fft)

frequencies = np.fft.rfftfreq(len(y), d=1.0/sr)

plt.figure(figsize=(10,4))
plt.plot(frequencies, amp, color='r')
plt.title("Freq spectrum")
plt.xlabel("Frequency")
plt.ylabel("Magnitude")
plt.grid(True)
plt.show()

# np.argmax() returns the index of the largest value of an array; the index by itself isn't useful but
# since freq & mangitude are same length and addup, the index can look up the frequency

peak_index = np.argmax(amp)
peak_freq = frequencies[peak_index] # freq of loudest bin

most_accurate_note = [abs(peak_freq - piano_notes[1]["fundamental_hz"]), piano_notes[1]["note"]]

print(most_accurate_note[1])

chunk_size = int(sr // (1000 // CHUNK))

for i in range(0, len(y), chunk_size):

  y_fft = np.fft.rfft(y[i: i+chunk_size])
  # nps.abs strips the phase and takes the magnitude bc phase is not needed. 

  amp = np.abs(y_fft)

  frequencies = np.fft.rfftfreq(chunk_size, d=1.0/sr)

  # np.argmax() returns the index of the largest value of an array; the index by itself isn't useful but
  # since freq & mangitude are same length and addup, the index can look up the frequency

  peak_index = np.argmax(amp)
  peak_freq = frequencies[peak_index] # freq of loudest bin

  most_accurate_note = [abs(peak_freq - piano_notes[1]["fundamental_hz"]), piano_notes[1]["note"]]
  for _ in piano_notes:
    fundamental = piano_notes[_]["fundamental_hz"]
    difference = abs(peak_freq - fundamental)
    if difference <= most_accurate_note[0]:
      most_accurate_note = [difference, piano_notes[_]["note"]]
  
  print(f"{most_accurate_note[1]} from {i / sr} to {(i + chunk_size) / sr} seconds")
  print(f"peak frequency = {peak_freq}")

def find_peaks(amp):
  peaks = []
  for i in range(1, len(amp)-1):
    if amp[i] > amp[i-1] and amp[i] > amp[i+1] and amp[i] > 500:
      peaks.append(i)
  
