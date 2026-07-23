
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