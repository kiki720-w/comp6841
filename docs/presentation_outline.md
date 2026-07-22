# 3-Minute Presentation Outline

## 0:00-0:25 What the project is

I looked at game trainers through a security engineering lens. My question was: if a single-player game trusts local state like HP, gold, and enemy HP, how can that be abused?

Mention that I used a real Slay the Spire 2 trainer as the case study, but my own attack code only targets a controlled demo.

## 0:25-0:55 How I found evidence

Show the static analyser output.

Point out:

- `SlayTheSpire2.exe`
- `WriteProcessMemory`
- `VirtualProtect`
- `aobscanregion`
- `mono`

Explain that these strings gave me a technical hypothesis: the trainer is probably finding runtime state or code regions and modifying them.

## 0:55-1:45 What I built

Show the memory target screenshot with PID, address, and offsets.

Then show the before/after memory write screenshot.

Say:

> This is my controlled reproduction of the core idea. The trainer opens my target process, reads the game-state struct, and writes new values.

Mention the result:

- player HP changed to 999;
- enemy HP changed to 1;
- gold changed to 999.

## 1:45-2:20 Defence side

Show the suspicious-state detection screenshot.

Explain:

- HP above max HP is impossible in normal rules;
- gold is far above expected range;
- simple anomaly detection can catch this class of tampering.

Then mention the limitation: local checks can be patched or bypassed, so shared outcomes need stronger validation.

## 2:20-2:50 Challenge

Talk about the project change:

- first I built a JSON-state demo;
- it worked, but it was too simple;
- I upgraded to a process-memory demo using Windows APIs;
- I added a magic marker so the trainer refuses to write if the address is wrong.

## 2:50-3:00 Reflection

End with:

> The main lesson was that the visible cheat is only the symptom. The real security issue is the trust boundary: if the defender trusts local state too much, the attacker gets room to change the outcome.
