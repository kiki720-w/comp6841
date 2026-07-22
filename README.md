# Slay the Spire 2 Trainer Security Project

This is my COMP6841 project for the "create something to demonstrate a concept or help with analysis" category.

The project looks at a game-hacking question:

> If a single-player game trusts important local state, how can a trainer abuse that state, and how could a defender notice it?

I used a real Slay the Spire 2 trainer as the case study, then built controlled demos to reproduce the same kind of weakness safely.

## What is included

```text
tools/static_trainer_analyzer.py   Static analysis helper for trainer-like PE files
src/toy_card_game.py               First toy game demo using a signed JSON state file
src/trainer_prototype.py           First controlled trainer prototype
src/defence_monitor.py             Simple HMAC/anomaly monitor for the JSON demo
src/memory_target_game.py          Controlled process target with a GameState struct in memory
src/memory_trainer_demo.py         Controlled trainer using Windows process-memory APIs
docs/project_output.md             Main project output notes
docs/report_draft.md               Short report draft
docs/presentation_outline.md       3 minute presentation outline
docs/evidence_log_template.md      Screenshot/evidence checklist
```

## What is not included

This repository does not contain:

- the Slay the Spire 2 trainer binary;
- game files;
- a working Slay the Spire 2 cheat;
- game-specific memory addresses, patch bytes, or AOB signatures.

The active attack code only targets my controlled demo programs.

## Static analysis

Run this against the trainer zip/exe:

```powershell
python tools\static_trainer_analyzer.py "D:\game hacking\Slay the Spire 2 Early Access Plus 20 Trainer.zip"
```

The useful evidence I saw included `SlayTheSpire2.exe`, `WriteProcessMemory`, `VirtualProtect`, `aobscanregion`, `mono`, and `getmonostruct`.

## File-state demo

This was my first prototype. It is useful for explaining the basic idea, but it is less realistic than the memory demo.

```powershell
python src\toy_card_game.py --reset --init-only
python src\defence_monitor.py
python src\trainer_prototype.py --gold 999 --player-hp 999 --one-hit-kill --reason "controlled demo"
python src\defence_monitor.py
```

Expected idea:

- before tampering, the state is clean;
- the trainer changes HP, enemy HP, and gold;
- the monitor detects the changed state.

## Process-memory demo

This is the stronger technical demo.

Terminal 1:

```powershell
python src\memory_target_game.py
```

Copy the printed PID and `GameState address`.

Terminal 2:

```powershell
python src\memory_trainer_demo.py --pid <PID> --address <ADDRESS> --gold 999 --player-hp 999 --one-hit-kill
```

The trainer reads the target process state, writes new values, and prints before/after values. The target process then reports suspicious values such as HP above max HP or unusually high gold.

## Project argument

The real trainer gave me evidence of likely memory-oriented behaviour. The controlled memory demo gave me a safe way to show the same class of attack. The defence side shows that local checks can detect obvious tampering, but stronger protection is needed when outcomes affect anything shared, such as achievements, leaderboards, or online systems.
