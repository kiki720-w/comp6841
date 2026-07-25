# 5-Minute Live Presentation Outline

The class update changed the presentation from video submission to live presentation, so this outline is designed for about five minutes in front of the tutor. I should not try to explain every line of code. The goal is to show the project result, the challenge, and why it is security-related.

## 0:00-0:40 Opening: what I investigated

Say:

> My project is about game trainers and client-side trust. I wanted to understand how a trainer can turn normal single-player gameplay into effects like infinite gold or one-hit kills, and how a defender might detect that.

Mention:

- real Slay the Spire 2 trainer used as case study;
- my own active attack code only targets controlled demo programs;
- project category: creating something to demonstrate a security concept and help analysis.

## 0:40-1:25 Evidence from the real trainer

Show Figure 1: `屏幕截图 2026-07-22 234845.png`.

Point out:

- `SlayTheSpire2.exe`
- `WriteProcessMemory`
- `VirtualProtect`
- `aobscanregion`
- `mono`
- `getmonostruct`

Say:

> These strings do not fully reverse engineer the trainer, but they gave me a strong hypothesis that the trainer is doing runtime scanning and memory/state modification.

## 1:25-2:05 First prototype

Show Figure 2: `屏幕截图 2026-07-22 235025.png`.

Explain:

- I first built a toy card game with local HP, enemy HP, gold, and energy.
- The first trainer prototype changed a local state file.
- The defence monitor detected integrity mismatch and impossible values.

Then say:

> This worked, but it was too simple for COMP6841 because it was file tampering, not process-memory tampering.

## 2:05-3:10 Main technical demo: process-memory trainer

Show Figure 3: `屏幕截图 2026-07-22 235449.png`.

Explain the chain:

1. `memory_target_game.py` runs a controlled game-like process.
2. It stores a `GameState` struct in memory.
3. `memory_trainer_demo.py` opens that process.
4. It reads the state using `ReadProcessMemory`.
5. It writes new values using `WriteProcessMemory`.

Point to the values:

- player HP changed from `0` to `999`;
- enemy HP changed from `18` to `1`;
- gold changed from `359` to `999`.

Say:

> This is the strongest technical part of my project because it reproduces the core trainer idea at process-memory level in a controlled environment.

## 3:10-3:55 Defence and security link

Show Figure 4: `屏幕截图 2026-07-23 001223.png`.

Explain:

- HP above max HP is impossible under normal rules.
- Gold is much higher than expected.
- The target process flags this as suspicious.

Security link:

> The vulnerability is not just "the player can cheat". The security issue is the trust boundary: the defender is trusting local client state that a local process can modify.

Mention limitations:

- local checks can be patched or bypassed;
- shared outcomes need stronger validation, such as server-side checks, replay verification, strict mod permissions, or achievement validation.

## 3:55-4:35 Challenges

Talk about three challenges:

- Scope: I wanted realism, but did not want to submit a working Slay the Spire 2 cheat.
- Technical depth: the first JSON demo was too shallow, so I upgraded to process memory.
- Safety: I added a magic marker so the memory trainer refuses to write if the address is wrong.

## 4:35-5:00 Reflection and closing

Say:

> The main thing I learned is that the visible cheat effect is only the symptom. The deeper problem is where the defender places trust. If important state and enforcement are both inside a local client, the attacker has room to change the outcome.

End with:

- GitHub has the code;
- report/project output has screenshots and evidence;
- future work would compare memory trainers with OCR advisers or mod APIs.
