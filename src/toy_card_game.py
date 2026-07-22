import argparse
import hashlib
import hmac
import json
import os
import random
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = PROJECT_ROOT / "runtime"
STATE_PATH = RUNTIME_DIR / "game_state.json"
SECRET = b"comp6841-controlled-demo-secret"


def canonical_state(state):
    unsigned = {k: v for k, v in state.items() if k != "integrity"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()


def sign_state(state):
    return hmac.new(SECRET, canonical_state(state), hashlib.sha256).hexdigest()


def initial_state():
    return {
        "player_hp": 70,
        "max_player_hp": 70,
        "enemy_hp": 45,
        "max_enemy_hp": 45,
        "gold": 99,
        "energy": 3,
        "turn": 1,
        "last_action": "new run",
        "events": [],
    }


def save_state(state, signed=True):
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    state = dict(state)
    if signed:
        state["integrity"] = sign_state(state)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def load_state():
    if not STATE_PATH.exists():
        state = initial_state()
        save_state(state)
        return state
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def print_state(state):
    print("\n=== Toy Card Game State ===")
    print(f"Turn      : {state['turn']}")
    print(f"Player HP : {state['player_hp']} / {state['max_player_hp']}")
    print(f"Enemy HP  : {state['enemy_hp']} / {state['max_enemy_hp']}")
    print(f"Gold      : {state['gold']}")
    print(f"Energy    : {state['energy']}")
    print(f"Last move : {state['last_action']}")
    print("===========================\n")


def add_event(state, event):
    state.setdefault("events", [])
    state["events"].append({"turn": state["turn"], "event": event, "time": int(time.time())})
    state["events"] = state["events"][-12:]


def enemy_attack(state):
    damage = random.randint(5, 11)
    state["player_hp"] = max(0, state["player_hp"] - damage)
    add_event(state, f"enemy attacked for {damage}")
    state["last_action"] = f"enemy attacked for {damage}"


def play_turn(state, action):
    if state["player_hp"] <= 0 or state["enemy_hp"] <= 0:
        return state

    if action == "strike":
        if state["energy"] < 1:
            state["last_action"] = "not enough energy"
        else:
            state["energy"] -= 1
            state["enemy_hp"] = max(0, state["enemy_hp"] - 6)
            add_event(state, "player used strike for 6")
            state["last_action"] = "player used strike"
    elif action == "bash":
        if state["energy"] < 2:
            state["last_action"] = "not enough energy"
        else:
            state["energy"] -= 2
            state["enemy_hp"] = max(0, state["enemy_hp"] - 12)
            add_event(state, "player used bash for 12")
            state["last_action"] = "player used bash"
    elif action == "end":
        enemy_attack(state)
        state["turn"] += 1
        state["energy"] = 3
    elif action == "shop":
        if state["gold"] >= 30:
            state["gold"] -= 30
            state["player_hp"] = min(state["max_player_hp"], state["player_hp"] + 10)
            add_event(state, "bought heal for 30 gold")
            state["last_action"] = "bought heal"
        else:
            state["last_action"] = "not enough gold"
    else:
        state["last_action"] = f"unknown action: {action}"

    if state["enemy_hp"] <= 0:
        reward = 20
        state["gold"] += reward
        add_event(state, f"enemy defeated, gained {reward} gold")
        state["last_action"] = "enemy defeated"
    return state


def main():
    parser = argparse.ArgumentParser(description="Controlled toy card game for COMP6841 trainer analysis.")
    parser.add_argument("--reset", action="store_true", help="reset the game state")
    parser.add_argument("--init-only", action="store_true", help="initialise state and exit without interactive play")
    parser.add_argument("--unsigned", action="store_true", help="save without integrity signature")
    args = parser.parse_args()

    if args.reset or not STATE_PATH.exists():
        save_state(initial_state(), signed=not args.unsigned)
        if args.init_only:
            print(f"Initialised toy game state at {STATE_PATH}")
            return

    print("Toy card game started. Commands: strike, bash, shop, end, state, reset, quit")
    while True:
        state = load_state()
        print_state(state)
        if state["player_hp"] <= 0:
            print("Player lost. Type reset to start again.")
        elif state["enemy_hp"] <= 0:
            print("Enemy defeated. Type reset to start again.")

        action = input("> ").strip().lower()
        if action == "quit":
            return
        if action == "state":
            continue
        if action == "reset":
            state = initial_state()
        else:
            state = play_turn(state, action)
        save_state(state, signed=not args.unsigned)


if __name__ == "__main__":
    main()
