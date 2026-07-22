import hashlib
import hmac
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = PROJECT_ROOT / "runtime" / "game_state.json"
SECRET = b"comp6841-controlled-demo-secret"


def canonical_state(state):
    unsigned = {k: v for k, v in state.items() if k != "integrity"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()


def expected_signature(state):
    return hmac.new(SECRET, canonical_state(state), hashlib.sha256).hexdigest()


def load_state():
    if not STATE_PATH.exists():
        raise SystemExit(f"State file not found: {STATE_PATH}")
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def anomaly_checks(state):
    findings = []
    if state.get("player_hp", 0) > state.get("max_player_hp", 0):
        findings.append("player_hp is higher than max_player_hp")
    if state.get("enemy_hp", 0) > state.get("max_enemy_hp", 0):
        findings.append("enemy_hp is higher than max_enemy_hp")
    if state.get("energy", 0) > 3:
        findings.append("energy is higher than the normal turn limit")
    if state.get("gold", 0) > 300:
        findings.append("gold is unusually high for this toy scenario")
    if "trainer" in str(state.get("last_action", "")).lower():
        findings.append("last_action indicates trainer-style modification")
    return findings


def main():
    state = load_state()
    stored = state.get("integrity")
    expected = expected_signature(state)
    findings = []

    if not stored:
        findings.append("missing integrity signature")
    elif not hmac.compare_digest(stored, expected):
        findings.append("integrity signature mismatch")

    findings.extend(anomaly_checks(state))

    print("=== Defence Monitor ===")
    print(f"State file: {STATE_PATH}")
    if findings:
        print("Result: suspicious")
        for finding in findings:
            print(f"- {finding}")
    else:
        print("Result: clean")
    print("=======================")


if __name__ == "__main__":
    main()
