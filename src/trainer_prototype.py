import argparse
import json
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = PROJECT_ROOT / "runtime" / "game_state.json"


def load_state():
    if not STATE_PATH.exists():
        raise SystemExit(f"State file not found: {STATE_PATH}\nRun toy_card_game.py first.")
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_tampered_state(state):
    # Intentionally does not recompute integrity. This simulates an attacker
    # changing client-owned state without knowing the defender's signing key.
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def append_tamper_event(state, reason):
    state.setdefault("events", [])
    state["events"].append(
        {
            "turn": state.get("turn", "?"),
            "event": f"tamper prototype changed state: {reason}",
            "time": int(time.time()),
        }
    )
    state["events"] = state["events"][-12:]


def main():
    parser = argparse.ArgumentParser(
        description="Controlled trainer prototype. It only modifies the toy game state file."
    )
    parser.add_argument("--gold", type=int, help="set player gold")
    parser.add_argument("--player-hp", type=int, help="set player HP")
    parser.add_argument("--enemy-hp", type=int, help="set enemy HP")
    parser.add_argument("--energy", type=int, help="set energy")
    parser.add_argument("--one-hit-kill", action="store_true", help="set enemy HP to 1")
    parser.add_argument("--reason", default="lab demonstration", help="short reason logged in events")
    args = parser.parse_args()

    state = load_state()
    before = dict(state)

    if args.gold is not None:
        state["gold"] = args.gold
    if args.player_hp is not None:
        state["player_hp"] = args.player_hp
    if args.enemy_hp is not None:
        state["enemy_hp"] = args.enemy_hp
    if args.energy is not None:
        state["energy"] = args.energy
    if args.one_hit_kill:
        state["enemy_hp"] = 1

    state["last_action"] = "state modified by controlled trainer prototype"
    append_tamper_event(state, args.reason)
    save_tampered_state(state)

    print("Toy trainer wrote modified local game state.")
    print("Before:")
    for key in ("player_hp", "enemy_hp", "gold", "energy"):
        print(f"  {key}: {before.get(key)}")
    print("After:")
    for key in ("player_hp", "enemy_hp", "gold", "energy"):
        print(f"  {key}: {state.get(key)}")
    print("\nNext check: run defence_monitor.py and compare the result.")


if __name__ == "__main__":
    main()
