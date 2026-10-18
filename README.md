# yue

A program that transcribes monophonic audio into note names using FFT (Fast Fourier Transform)-based harmonic detection.

From the chinese word, 音**乐** (Music)

## How it Works

1. First, it loads a `.wav` file and computes its full spectrum FFT (Fast Fourier Transform). Shown as a plot.
2. Slides a ~200 ms window across the audio
3. Each chunk finds spectral peaks and estimates the audio's fundamental frequency by looking for a harmonic series among those peaks (peaks that line up as multiples as a common base frequwncy)
4. Matches the fundamental to the nearest of the 88 pinao key frequencies
5. Collapses consecutive windows with same note into a single timestamped segment

## Building the Program

Requires Python 3.9+

Run:

```
chmod +x build_mac.sh
./build_mac.sh
```

This creates `dist/yue`, a self-contained binary.

On your first run, MacOS Gatekeeper may block the binary since its unsigned. To fix this, either:

1. Right click `dist/yue` on finder -> Open -> Open (only needed once)
2. Or, Through terminal, run `xattr -dr com.apple.quarantine dist/yue`

## Usage

`./dist/yue path/to/audio.wav`
WIth no arguments, it uses the bundled `sample_audios/sample.wav`

You can also use the following flags:

- `--no-plot` to skip the sepctrum plot popup, and only print the notes
- `-h`, `-help` to show usage

### Example

`./dist/yue sample_audios/little-lamb.wav --no-plot`

Output:

```
loaded 264600 samples at 44100 Hz
6.00000 seconds

Detected notes:
  C4    0.20s ->  0.80s
  D4    0.80s ->  1.20s
  ...
```

## Project Structure

```
main.py entry point: CLI, FFT pipeline, note matching
notes.py           lookup table of the 88 piano key frequencies
sample_audios/     example .wav files to test with
other/             scratch files / earlier experiments, not used by main.py
build_mac.sh       one-time PyInstaller build script (see above)
requirements.txt   Python deps, only needed for the build step
```

## Limitations

This works only (or best) on monophonic audio, i.e. one note at a time. If you choose to use chords, it will mess up the harmonic matching step.

It only reads .wav files, but you can easily change mp3 files to wav through an online converter.

No filter for background noise, so any background noise detected can get labelled as notes.

The harmonic detection is not perfect, so you will see some notes that are misread or misoutputted.
