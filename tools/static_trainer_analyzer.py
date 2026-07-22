import argparse
import hashlib
import json
import re
import struct
import tempfile
import zipfile
from pathlib import Path


SUSPICIOUS_KEYWORDS = [
    "OpenProcess",
    "ReadProcessMemory",
    "WriteProcessMemory",
    "VirtualAlloc",
    "VirtualProtect",
    "CreateRemoteThread",
    "GetAsyncKeyState",
    "aobscan",
    "aobscanregion",
    "mono",
    "getmonostruct",
    "trainer",
    "cheat",
    "SlayTheSpire2.exe",
    "GameAssembly",
]


def sha256(data):
    return hashlib.sha256(data).hexdigest().upper()


def extract_candidate(path):
    path = Path(path)
    if path.suffix.lower() != ".zip":
        return path, path.read_bytes()

    with zipfile.ZipFile(path, "r") as zf:
        exe_names = [name for name in zf.namelist() if name.lower().endswith(".exe")]
        if not exe_names:
            raise SystemExit("No .exe found in zip archive.")
        name = exe_names[0]
        data = zf.read(name)
        return Path(name), data


def parse_pe(data):
    result = {
        "is_mz": data[:2] == b"MZ",
        "is_pe": False,
        "machine": None,
        "sections": [],
    }
    if len(data) < 0x40 or not result["is_mz"]:
        return result

    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if pe_offset + 24 >= len(data) or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        return result

    result["is_pe"] = True
    machine, section_count, timestamp, _, _, optional_size, characteristics = struct.unpack_from(
        "<HHIIIHH", data, pe_offset + 4
    )
    result["machine"] = hex(machine)
    result["section_count"] = section_count
    result["timestamp"] = timestamp
    result["characteristics"] = hex(characteristics)

    section_table = pe_offset + 24 + optional_size
    for index in range(section_count):
        offset = section_table + index * 40
        if offset + 40 > len(data):
            break
        raw_name = data[offset : offset + 8].split(b"\0", 1)[0]
        name = raw_name.decode("ascii", errors="replace")
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", data, offset + 8)
        result["sections"].append(
            {
                "name": name,
                "virtual_address": hex(virtual_address),
                "virtual_size": virtual_size,
                "raw_size": raw_size,
                "raw_pointer": raw_pointer,
            }
        )
    return result


def extract_strings(data, min_len=5):
    ascii_strings = [s.decode("latin1", errors="ignore") for s in re.findall(rb"[ -~]{%d,}" % min_len, data)]
    wide_pattern = rb"(?:[ -~]\x00){%d,}" % min_len
    wide_strings = [s.decode("utf-16le", errors="ignore") for s in re.findall(wide_pattern, data)]
    return ascii_strings + wide_strings


def keyword_hits(strings):
    hits = {}
    for keyword in SUSPICIOUS_KEYWORDS:
        matched = [s for s in strings if keyword.lower() in s.lower()]
        if matched:
            hits[keyword] = matched[:10]
    return hits


def main():
    parser = argparse.ArgumentParser(description="Static analysis helper for a trainer-like PE sample.")
    parser.add_argument("sample", help="path to .exe or .zip containing .exe")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args()

    candidate_name, data = extract_candidate(args.sample)
    strings = extract_strings(data)
    report = {
        "sample_argument": str(args.sample),
        "analysed_file": str(candidate_name),
        "size_bytes": len(data),
        "sha256": sha256(data),
        "pe": parse_pe(data),
        "keyword_hits": keyword_hits(strings),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("=== Trainer Static Notes ===")
    print(f"Input          : {args.sample}")
    print(f"Analysed file  : {candidate_name}")
    print(f"Size           : {len(data)} bytes")
    print(f"SHA256         : {report['sha256']}")
    print(f"MZ/PE          : {report['pe']['is_mz']} / {report['pe']['is_pe']}")
    if report["pe"]["is_pe"]:
        print(f"Machine        : {report['pe']['machine']}")
        print(f"Sections       : {report['pe']['section_count']}")
        for section in report["pe"]["sections"]:
            print(
                f"  {section['name']:8} raw={section['raw_size']:8} "
                f"vsize={section['virtual_size']:8} va={section['virtual_address']}"
            )
    print("\nSuspicious / relevant string indicators:")
    for keyword, matches in report["keyword_hits"].items():
        print(f"- {keyword}: {len(matches)} sample hit(s)")
        for match in matches[:3]:
            print(f"    {match[:160]}")
    print("\nNote: this tool does not execute the sample.")


if __name__ == "__main__":
    main()
