# Evidence Log Template

Use this file while working. Put screenshots and command output into the final project output PDF.

## 1. Real trainer sample

- File name:
- Source:
- SHA256:
- File size:
- Signature status:
- Static indicators found:
  - `SlayTheSpire2.exe`
  - `WriteProcessMemory`
  - `VirtualProtect`
  - `aobscanregion`
  - `mono`

Screenshots to capture:

- Trainer UI.
- Game state before enabling trainer option.
- Game state after enabling infinite gold / one-hit kill.
- Static analyser output.

## 2. Discovery process

Describe how the weakness was discovered:

- Behaviour observed:
- Static strings/API evidence:
- Hypothesis:
- What was confirmed:
- What was not confirmed:

## 3. Controlled attack demo

Commands run:

```powershell
python src/toy_card_game.py --reset --init-only
python src/trainer_prototype.py --gold 999 --player-hp 999 --one-hit-kill
python src/defence_monitor.py
```

Evidence:

- State before tampering:
- State after tampering:
- Defence monitor output:

## 4. Debugging and challenge notes

- Problem encountered:
- What I tried:
- What worked:
- What I would change next time:

## 5. Controlled process-memory demo

Terminal 1:

```powershell
python src/memory_target_game.py
```

Record:

- PID:
- GameState address:
- Initial HP/gold/enemy values:

Terminal 2:

```powershell
python src/memory_trainer_demo.py --pid <PID> --address <ADDRESS> --gold 999 --player-hp 999 --one-hit-kill
```

Evidence:

- Before memory write output:
- After memory write output:
- Target process suspicious-state warnings:
