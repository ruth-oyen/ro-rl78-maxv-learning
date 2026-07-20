"""Extract CFM and UFM programming words from the PROGRAM block of an SVF file."""

import argparse
import re
import struct
from pathlib import Path


ADDRESS_RE = re.compile(r"^SDR\s+13\s+TDI\s+\(([0-9A-Fa-f]+)\)\s*;")
DATA_RE = re.compile(r"^SDR\s+16\s+TDI\s+\(([0-9A-Fa-f]+)\)\s*;")


def extract_program_data(path: Path) -> tuple[bytes, bytes]:
    data = {0: bytearray(), 1: bytearray()}
    in_program = False
    address = None

    with path.open("r", encoding="ascii") as source:
        for raw_line in source:
            line = raw_line.strip()

            if line == "!PROGRAM":
                in_program = True
                continue
            if in_program and line == "!VERIFY":
                break
            if not in_program:
                continue

            match = ADDRESS_RE.match(line)
            if match:
                address = int(match.group(1), 16)
                continue

            match = DATA_RE.match(line)
            if match and address in data:
                value = int(match.group(1), 16)
                data[address] += struct.pack("<H", value)

    return bytes(data[0]), bytes(data[1])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract CFM and UFM data from an SVF PROGRAM block"
    )
    parser.add_argument("svf", type=Path)
    args = parser.parse_args()

    cmf, ufm = extract_program_data(args.svf)
    cmf_path = args.svf.with_suffix(".cfm")
    ufm_path = args.svf.with_suffix(".ufm")
    cmf_path.write_bytes(cmf)
    ufm_path.write_bytes(ufm)

    print(f"{cmf_path}: {len(cmf) // 2} words")
    print(f"{ufm_path}: {len(ufm) // 2} words")


if __name__ == "__main__":
    main()
