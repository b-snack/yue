#!/usr/bin/env python3
"""
yue - transcribe monophonic audio into piano note names
using FFT-based harmonic/pitch detection.
"""
import argparse
import sys
from pathlib import Path

from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt

from notes import piano_notes

# ------------------- CONSTANTS -------------------

CHUNK = 200  # ms, controls the analysis window size
SPEED_OF_SOUND = 340  # m/s (reserved for future use)

# -------------------- FUNCTIONS ---------------------


def load_audio(filename):
  """
  Reads a .wav, converts to mono float32 array, y, with sample rate, sr.
  Mono means that instead of having two channels (e.g. stereo left & right),
  the audio is combined into one. 
  """
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
  """
  Takes a supposed fundamental, and matches the harmonics with their closest frequency matches.
  Adds the loudness of all four points and returns it as score.
  For future reference in case of confusion, chunk amp is the loudness, and frequencies_chunk is a list of
  all the frequencies in progression (e.g. [50, 100, 150, 200]); they match with a loud (think of it as x and y axis)

  Fundamental ratio is the loudness against the total added loudness
  """
  harmonics = []
  for i in range(1, 5):
    target_freq = fundamental * i
    index = np.argmin(np.abs(frequencies_chunk - target_freq))
    harmonics.append(chunk_amp[index])

  score = sum(harmonics)

  if score > 0:
    fundamental_ratio = harmonics[0] / score
  else:
    fundamental_ratio = 0.0
  return score, fundamental_ratio


def analyze(filename, show_plot=True):
  notes = []
  current_note = None
  start_time = 0

  y, sr = load_audio(filename)

  y_fft = np.fft.rfft(y)
  amp = np.abs(y_fft)
  frequencies = np.fft.rfftfreq(len(y), d=1.0/sr)

  peak_indices = find_peaks(amp)
  peak_freqs = frequencies[peak_indices]
  peak_amps = amp[peak_indices]

  if show_plot:
    plt.figure(figsize=(10, 4))
    plt.plot(frequencies, amp, color='r', label='Spectrum')
    plt.scatter(peak_freqs, peak_amps, color='blue', zorder=3, label='Peaks')
    plt.xlabel("frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title(Path(filename).name)
    plt.grid(True)
    plt.legend()
    plt.show()

  chunk_size = int(sr // (1000 // CHUNK))

  for i in range(0, len(y), chunk_size):
    chunk_data = y[i: i+chunk_size]

    y_fft_chunk = np.fft.rfft(chunk_data)
    chunk_amp = np.abs(y_fft_chunk)
    frequencies_chunk = np.fft.rfftfreq(chunk_size, d=1.0/sr)

    scores = []
    max_score = 0
    for note in piano_notes:
      score, fundamental_ratio = score_note(piano_notes[note]["fundamental_hz"], chunk_amp, frequencies_chunk)
      scores.append((score, fundamental_ratio, piano_notes[note]["note"]))

      if score > max_score:
        max_score = score

    detected_notes = []
    if max_score > 0:
      for score, fundamental_ratio, note_name in scores:
        if score > max_score * 0.6 and fundamental_ratio > 0.15:
          detected_notes.append(note_name)

    if detected_notes == current_note:
      pass

    else:
      if current_note is not None:
        notes.append([current_note, start_time, i/sr])
      current_note = detected_notes
      start_time = i/sr

  if current_note is not None:
    notes.append([current_note, start_time, len(y)/sr])

  return notes


def main():
  parser = argparse.ArgumentParser(
    prog="yue",
    description="Transcribe monophonic audio into note names using FFT-based harmonic detection."
  )
  parser.add_argument(
    "audio_file",
    nargs="?",
    default="sample_audios/sample.wav",
    help="Path to a .wav file to analyze (default: sample_audios/sample.wav)"
  )
  parser.add_argument(
    "--no-plot",
    action="store_true",
    help="Skip the frequency spectrum plot popup"
  )
  args = parser.parse_args()

  if not Path(args.audio_file).exists():
    print(f"error: file not found: {args.audio_file}", file=sys.stderr)
    sys.exit(1)

  notes = analyze(args.audio_file, show_plot=not args.no_plot)

  print("\nDetected notes:")
  if not notes:
    print("  (none)")
  for note, start, end in notes:
    print(f"  {note}  {start:6.2f}s -> {end:6.2f}s")


if __name__ == "__main__":
  main()