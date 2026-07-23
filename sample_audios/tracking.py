import numpy as np
"""
before loop:
  current note = none
  note start = time
  notes = []

inside loop after detecting note name -- for total time / chunk = number of chunks - 1 (so it ends on the last note)
  if note_name = current note,
    pass
  else:
    if note_name != current_note and note_name != "unclear":
      temporary note . append (i)
      notes.append(temporary_note)
      note_name = current_note
      temporary_note = []
      list append () or replace

    if note_name == unclear
      its transitioning, so we can figure out how to fix that later i guess. 

after loop ends, 
print(notes)

if unclear and then reverts back to c4 we'll just assume that its a held note. 

"""
CHUNK = 200
notes = []
current_note = None
start_time = 0
sr = 44100
chunk_size = int(sr // (1000 // CHUNK))
time = np.arange(len(y)) / sr
note_name = None

for note in (time//(chunk_size/1000)-1):
  if note_name == "unclear":
    pass
  elif note_name == current_note:
    pass
  else:
    if current_note is not None:
      notes.append([current_note, start_time, i/sr])
    current_note = note_name
    start_time = i/sr

if current_note is not None:
  notes.append([current_note, start_time, time])

print(notes)