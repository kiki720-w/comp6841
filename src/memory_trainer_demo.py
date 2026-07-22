import argparse
import ctypes
import struct


PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_INFORMATION = 0x0400

MAGIC = 0x68416841

FIELDS = {
    "magic": (0x00, "I"),
    "player_hp": (0x04, "i"),
    "max_player_hp": (0x08, "i"),
    "enemy_hp": (0x0C, "i"),
    "max_enemy_hp": (0x10, "i"),
    "gold": (0x14, "i"),
    "energy": (0x18, "i"),
    "turn": (0x1C, "i"),
}


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
kernel32.OpenProcess.restype = ctypes.c_void_p
kernel32.ReadProcessMemory.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.ReadProcessMemory.restype = ctypes.c_int
kernel32.WriteProcessMemory.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.WriteProcessMemory.restype = ctypes.c_int
kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
kernel32.CloseHandle.restype = ctypes.c_int


def parse_address(value):
    return int(value, 16) if str(value).lower().startswith("0x") else int(value)


def windows_error(message):
    error = ctypes.get_last_error()
    return OSError(error, f"{message}: Windows error {error}")


def open_process(pid):
    access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION
    handle = kernel32.OpenProcess(access, False, pid)
    if not handle:
        raise windows_error("OpenProcess failed")
    return handle


def read_bytes(handle, address, size):
    buffer = ctypes.create_string_buffer(size)
    bytes_read = ctypes.c_size_t()
    ok = kernel32.ReadProcessMemory(
        handle,
        ctypes.c_void_p(address),
        buffer,
        size,
        ctypes.byref(bytes_read),
    )
    if not ok or bytes_read.value != size:
        raise windows_error("ReadProcessMemory failed")
    return buffer.raw


def write_bytes(handle, address, data):
    buffer = ctypes.create_string_buffer(data)
    bytes_written = ctypes.c_size_t()
    ok = kernel32.WriteProcessMemory(
        handle,
        ctypes.c_void_p(address),
        buffer,
        len(data),
        ctypes.byref(bytes_written),
    )
    if not ok or bytes_written.value != len(data):
        raise windows_error("WriteProcessMemory failed")


def read_field(handle, base_address, field):
    offset, fmt = FIELDS[field]
    data = read_bytes(handle, base_address + offset, struct.calcsize(fmt))
    return struct.unpack("<" + fmt, data)[0]


def write_field(handle, base_address, field, value):
    offset, fmt = FIELDS[field]
    data = struct.pack("<" + fmt, value)
    write_bytes(handle, base_address + offset, data)


def read_state(handle, base_address):
    return {field: read_field(handle, base_address, field) for field in FIELDS}


def print_state(title, state):
    print(title)
    for key in ("magic", "player_hp", "max_player_hp", "enemy_hp", "max_enemy_hp", "gold", "energy", "turn"):
        value = state[key]
        if key == "magic":
            print(f"  {key:14}: 0x{value:08X}")
        else:
            print(f"  {key:14}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="Controlled memory trainer. Requires PID/address printed by memory_target_game.py."
    )
    parser.add_argument("--pid", type=int, required=True, help="PID of memory_target_game.py")
    parser.add_argument("--address", required=True, help="GameState base address printed by target, e.g. 0x1234ABCD")
    parser.add_argument("--gold", type=int, help="set gold")
    parser.add_argument("--player-hp", type=int, help="set player HP")
    parser.add_argument("--enemy-hp", type=int, help="set enemy HP")
    parser.add_argument("--energy", type=int, help="set energy")
    parser.add_argument("--one-hit-kill", action="store_true", help="set enemy HP to 1")
    args = parser.parse_args()

    base_address = parse_address(args.address)
    handle = open_process(args.pid)
    try:
        before = read_state(handle, base_address)
        if before["magic"] != MAGIC:
            raise SystemExit(
                "Magic marker did not match the controlled target. "
                "Refusing to write because the PID/address may be wrong."
            )

        print_state("Before memory write:", before)

        requested = {
            "gold": args.gold,
            "player_hp": args.player_hp,
            "enemy_hp": args.enemy_hp,
            "energy": args.energy,
        }
        if args.one_hit_kill:
            requested["enemy_hp"] = 1

        for field, value in requested.items():
            if value is not None:
                write_field(handle, base_address, field, value)

        after = read_state(handle, base_address)
        print_state("After memory write:", after)
        print("\nAPI path used: OpenProcess -> ReadProcessMemory -> WriteProcessMemory")
    finally:
        kernel32.CloseHandle(handle)


if __name__ == "__main__":
    main()
