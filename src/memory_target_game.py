import argparse
import ctypes
import os
import time


class GameState(ctypes.Structure):
    _fields_ = [
        ("magic", ctypes.c_uint32),
        ("player_hp", ctypes.c_int32),
        ("max_player_hp", ctypes.c_int32),
        ("enemy_hp", ctypes.c_int32),
        ("max_enemy_hp", ctypes.c_int32),
        ("gold", ctypes.c_int32),
        ("energy", ctypes.c_int32),
        ("turn", ctypes.c_int32),
    ]


MAGIC = 0x68416841


def build_state():
    return GameState(
        magic=MAGIC,
        player_hp=70,
        max_player_hp=70,
        enemy_hp=45,
        max_enemy_hp=45,
        gold=99,
        energy=3,
        turn=1,
    )


def print_banner(state):
    address = ctypes.addressof(state)
    print("=== Memory Target Game ===", flush=True)
    print(f"PID                 : {os.getpid()}", flush=True)
    print(f"GameState address   : 0x{address:X}", flush=True)
    print(f"GameState size      : {ctypes.sizeof(GameState)} bytes", flush=True)
    print("Offsets:", flush=True)
    for field_name, _ in GameState._fields_:
        offset = getattr(GameState, field_name).offset
        print(f"  {field_name:14}: +0x{offset:X}", flush=True)
    print("=====================================", flush=True)
    print("Run memory_trainer_demo.py with the PID and address above.", flush=True)
    print("Press Ctrl+C to stop.\n", flush=True)


def normal_game_tick(state):
    if state.enemy_hp <= 0:
        state.gold += 20
        state.enemy_hp = state.max_enemy_hp
        state.turn += 1
        return "enemy defeated, reward granted"

    state.enemy_hp = max(0, state.enemy_hp - 3)
    if state.turn % 3 == 0:
        state.player_hp = max(0, state.player_hp - 4)
    state.turn += 1
    return "normal combat tick"


def anomaly_findings(state):
    findings = []
    if state.magic != MAGIC:
        findings.append("magic marker changed")
    if state.player_hp > state.max_player_hp:
        findings.append("player_hp exceeds max_player_hp")
    if state.enemy_hp < 0:
        findings.append("enemy_hp below zero")
    if state.gold > 300:
        findings.append("gold unexpectedly high")
    if state.energy > 3:
        findings.append("energy above normal maximum")
    return findings


def print_state(state, tick_note):
    print(
        f"turn={state.turn:03d} hp={state.player_hp}/{state.max_player_hp} "
        f"enemy={state.enemy_hp}/{state.max_enemy_hp} gold={state.gold} "
        f"energy={state.energy} note={tick_note}",
        flush=True,
    )
    findings = anomaly_findings(state)
    if findings:
        print("  monitor: suspicious state detected", flush=True)
        for finding in findings:
            print(f"  - {finding}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Controlled process-memory target for COMP6841 trainer analysis."
    )
    parser.add_argument("--no-tick", action="store_true", help="print state without normal game updates")
    parser.add_argument("--interval", type=float, default=1.0, help="seconds between state prints")
    args = parser.parse_args()

    state = build_state()
    print_banner(state)

    while True:
        note = "state display only" if args.no_tick else normal_game_tick(state)
        print_state(state, note)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
