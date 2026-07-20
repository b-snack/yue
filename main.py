from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from notes import piano_notes

# ------------------- CONSTANTS -------------------

CHUNK = 200
SPEED_OF_SOUND = 340 # m \cdot s^(-1)

# -------------------- FUNCTIONS ---------------------
def load_audio(filename):
  sr, y = wavfile.read(filename)

  if y.dtype != np.float32:
    y=y.astype(np.float32) / np.iinfo(y.dtype).max

  if len(y.shape) > 1:
    y=np.mean(y, axis=1)

  # y is amplitude of wave, sr is frequency of sampling
  # so, at each instance it takes the amplitude and stores it in an array
  print(f"loaded {len(y)} samples at {sr} Hz")
  print(f"{len(y) / sr:.5f} seconds")

  return y, sr

def find_peaks(amp):
  peaks = []
  for i in range(1, len(amp)-1):
    if amp[i] > amp[i-1] and amp[i] > amp[i+1] and amp[i] > 500:
      peaks.append(i)

  return peaks

def find_fundamental(peak_indices, frequencies_chunk):
  peaks = frequencies_chunk[peak_indices]
  
  if len(peaks) == 0:
    return 0
  
  if len(peaks) == 1:
    return peaks[0]

  peaks = np.sort(peaks)

  diffs = []
  for i in range(len(peaks) - 1):
    one_diff = peaks[i+1] - peaks[i]
    diffs.append(one_diff)

  candidate = min(diffs)

  multiples = np.round(peaks / candidate)
  errors = np.abs(peaks - (multiples * candidate))

  if np.all(errors <= 5.0):
    fundamental = candidate
  else:
    fundamental = peaks[0]

  return fundamental
  
  
def match_note(peak_freq):
  most_accurate_note = [abs(peak_freq - piano_notes[1]["fundamental_hz"]), piano_notes[1]["note"]]
  for _ in piano_notes:
    fundamental = piano_notes[_]["fundamental_hz"]
    difference = abs(peak_freq - fundamental)
    if difference <= most_accurate_note[0]:
      most_accurate_note = [difference, piano_notes[_]["note"]]
  
  return most_accurate_note[1]

def score_note(fundamental, chunk_amp, frequencies_chunk):
  pass    

def main():
  y, sr = load_audio("sample.wav")

  # np.arange(leny) / sr bc $\frac{samples}{\frac{samples}{second}}$ = seconds
  time = np.arange(len(y)) / sr


  y_fft = np.fft.rfft(y)
  # nps.abs strips the phase and takes the magnitude bc phase is not needed. 

  amp = np.abs(y_fft)

  frequencies = np.fft.rfftfreq(len(y), d=1.0/sr)

  # np.argmax() returns the index of the largest value of an array; the index by itself isn't useful but
  # since freq & mangitude are same length and addup, the index can look up the frequency
  peak_indices = find_peaks(amp)
  peak_freqs = frequencies[peak_indices]
  peak_amps = amp[peak_indices] # freq of loudest bin

  plt.figure(figsize=(10,4))
  plt.plot(frequencies, amp, color='r', label='Spectrum')

  plt.scatter(peak_freqs, peak_amps, color='blue', zorder=3, label='Peaks')

  plt.xlabel("frequency (Hz)")
  plt.ylabel("Magnitude")
  plt.grid(True)
  plt.legend()
  plt.show()

  chunk_size = int(sr // (1000 // CHUNK))

  for i in range(0, len(y), chunk_size):

    chunk_data = y[i: i+chunk_size]

    # nps.abs strips the phase and takes the magnitude bc phase is not needed. 

    y_fft_chunk = np.fft.rfft(chunk_data)
    chunk_amp = np.abs(y_fft_chunk)
    frequencies_chunk = np.fft.rfftfreq(chunk_size, d=1.0/sr)

    # np.argmax() returns the index of the largest value of an array; the index by itself isn't useful but
    # since freq & mangitude are same length and addup, the index can look up the frequency

    peak_index_chunk = find_peaks(chunk_amp)
    peak_freq_chunk = find_fundamental(peak_index_chunk, frequencies_chunk) # freq of loudest bin
    current_note_name = match_note(peak_freq_chunk)

    print(f'{current_note_name} from {i / sr:.3f} to {(i+chunk_size)/ sr:.3f} seconds')
    print(f'peak frequency = {peak_freq_chunk:.2f} Hz')

    # print(sr / chunk_size)

if __name__ == "__main__":
  main()
