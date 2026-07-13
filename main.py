from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from notes import piano_notes

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

# np.ftt.rfft() returns Fast Fourier Transform, which is alg that converts signal from time-based
    # into individual frequency components
    # this also reduces time complexity from O(N^2) to O(Nlog N)
    # only keeps positive freq
    # all sound waves are just a bunch of sin / cosine waves added tgt
        # first & higher frequencies all tgt, so fft unmixes them

# np.abs() returns distance from origin of complex number -> a + bi where i is $$sqrt(-1)$$

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
for i in piano_notes:
  fundamental = piano_notes[i]["fundamental_hz"]
  difference = abs(peak_freq - fundamental)
  if difference <= most_accurate_note[0]:
    most_accurate_note = [difference, piano_notes[i]["note"]]
 
print(most_accurate_note[1])


# chunk_size = 1103

# for i in range(0, len(y), chunk_size):
#   print(i)
#   pass