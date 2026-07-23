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
    y = y.astype(np.float32) / np.iinfo(y.dtype).max

  if len(y.shape) > 1:
    y = np.mean(y, axis=1)

  print(f"loaded {len(y)} samples at {sr} Hz")
  print(f"{len(y) / sr:.5f} seconds")

  return y, sr

def find_peaks(amp):
  peaks = []
  for i in range(1, len(amp)-1):
    if amp[i] > amp[i-1] and amp[i] > amp[i+1] and amp[i] > 25 * np.mean(amp):
      peaks.append(i)
      
  return peaks

def find_fundamental(peak_indices, frequencies_chunk):
  peaks = frequencies_chunk[peak_indices]
  # print(f"Raw: {peaks}")

  if len(peaks) == 0:
    return None

  if len(peaks) == 1:
    return peaks[0]

  peaks = np.sort(peaks)

  diffs = []
  for i in range(len(peaks) - 1):
    one_diff = peaks[i+1] - peaks[i]
    diffs.append(one_diff)

  valid_diffs = []
  for d in diffs:
    if d >= 27.5:
      valid_diffs.append(d)
  
  if len(valid_diffs) == 0:
    return None
  
  unique_diffs = []
  for d in valid_diffs:
    if d not in unique_diffs:
      unique_diffs.append(d)
  
  sorted_diffs = sorted(unique_diffs)

  top_3_candidates = []
  for i in range(min(3, len(sorted_diffs))):
    top_3_candidates.append(sorted_diffs[i])

  best_candidate = None
  best_score = 0

  for candidate in top_3_candidates:
    has_fundamental_peak = np.any(np.abs(peaks - candidate) <= 5.0)
    if not has_fundamental_peak:
      continue

    multiples = np.round(peaks / candidate)
    errors = np.abs(peaks - (multiples * candidate))
    allowed_tolerances = np.maximum(5.0, 0.05 * (multiples * candidate))

    matching_peaks = []
    for i in range(len(peaks)):
      if errors[i] <= allowed_tolerances[i]:
        matching_peaks.append(peaks[i])
    
    score = len(matching_peaks)

    if score / len(peaks) >= 0.70 and len(matching_peaks) >= 2:
      if score > best_score:
        best_score = score
        best_candidate = candidate
      elif score == best_score:
        if best_candidate is None or candidate < best_candidate:
          best_candidate = candidate

  # print(f"Peaks Hz: {peaks}")
  # print(f"diffs: {diffs}")
  # print(f"candidate: {candidate}")
  # print(f"errors: {errors}")

  return best_candidate

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
  notes = []
  current_note = None
  start_time = 0

  y, sr = load_audio("record1.wav")

  time = np.arange(len(y)) / sr

  y_fft = np.fft.rfft(y)
  amp = np.abs(y_fft)
  frequencies = np.fft.rfftfreq(len(y), d=1.0/sr)

  peak_indices = find_peaks(amp)
  peak_freqs = frequencies[peak_indices]
  peak_amps = amp[peak_indices]

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

    y_fft_chunk = np.fft.rfft(chunk_data)
    chunk_amp = np.abs(y_fft_chunk)
    frequencies_chunk = np.fft.rfftfreq(chunk_size, d=1.0/sr)

    # print(f"max amp in chunk: {np.max(chunk_amp):.2f}")

    peak_index_chunk = find_peaks(chunk_amp)
    peak_freq_chunk = find_fundamental(peak_index_chunk, frequencies_chunk)

    current_note_name = None

    if peak_freq_chunk is None:
      current_note_name = "unclear"
    else:
      current_note_name = match_note(peak_freq_chunk)

    if current_note_name == "unclear":
      pass

    elif current_note_name == current_note:
      pass
    
    else:
      if current_note is not None:
        notes.append([current_note, start_time, i/sr])
      current_note = current_note_name
      start_time = i/sr

  if current_note is not None:
    notes.append([current_note, start_time, len(y)/sr])

  print(notes)

if __name__ == "__main__":
  main()