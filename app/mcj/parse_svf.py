"""Minimal SVF player for the RO-RL78-MAXV-LEARNING MCJ firmware.

The parser intentionally supports only the commands used by sample.svf.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO, Iterator


BAUDRATE = 1_000_000

CMD_CTRL_GET_STATUS = 0x03
CMD_CTRL_SET_STATUS = 0x13
CMD_JTAG_FREQUENCY = 0x80
CMD_JTAG_TRST = 0x81
CMD_JTAG_STATE = 0x82
CMD_JTAG_ENDDR = 0x83
CMD_JTAG_ENDIR = 0x84
CMD_JTAG_RUNTEST = 0x85
CMD_JTAG_SDR = 0x86
CMD_JTAG_SIR = 0x87

STATE = {
    "RESET": 0x00,
    "IDLE": 0x01,
    "DRSELECT": 0x02,
    "DRCAPTURE": 0x03,
    "DRSHIFT": 0x04,
    "DREXIT1": 0x05,
    "DRPAUSE": 0x06,
    "DREXIT2": 0x07,
    "DRUPDATE": 0x08,
    "IRSELECT": 0x09,
    "IRCAPTURE": 0x0A,
    "IRSHIFT": 0x0B,
    "IREXIT1": 0x0C,
    "IRPAUSE": 0x0D,
    "IREXIT2": 0x0E,
    "IRUPDATE": 0x0F,
}

TOKEN_RE = re.compile(
    r"\s*(\([0-9A-Fa-f\s]+\)|[A-Za-z_][A-Za-z0-9_]*|"
    r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)"
)
SCAN_KEYS = {"TDI", "TDO", "MASK", "SMASK"}


class SvfError(ValueError):
    pass


@dataclass(frozen=True)
class Command:
    name: str
    args: tuple[object, ...]
    line: int


@dataclass
class Stats:
    commands: int = 0
    counts: dict[str, int] = field(default_factory=dict)
    tdo_checks: int = 0
    shifted_bits: int = 0

    def add(self, command: Command) -> None:
        self.commands += 1
        self.counts[command.name] = self.counts.get(command.name, 0) + 1
        if command.name in ("SIR", "SDR"):
            bits, values = command.args
            self.shifted_bits += bits
            self.tdo_checks += "TDO" in values


def statements(path: Path) -> Iterator[tuple[int, str]]:
    """Yield semicolon-terminated statements while removing SVF line comments."""
    pending = ""
    start_line = 1
    with path.open("r", encoding="ascii") as source:
        for line_number, raw in enumerate(source, 1):
            clean = re.split(r"!|//", raw, maxsplit=1)[0]
            if not pending and clean.strip():
                start_line = line_number
            pending += clean
            while ";" in pending:
                statement, pending = pending.split(";", 1)
                if statement.strip():
                    yield start_line, statement.strip()
                start_line = line_number
    if pending.strip():
        raise SvfError(f"line {start_line}: statement is missing ';'")


def tokens(text: str, line: int) -> list[str]:
    result = []
    pos = 0
    while pos < len(text):
        match = TOKEN_RE.match(text, pos)
        if not match:
            raise SvfError(f"line {line}: invalid token near {text[pos:pos + 24]!r}")
        result.append(match.group(1))
        pos = match.end()
    return result


def _state(value: str, line: int) -> int:
    try:
        return STATE[value.upper()]
    except KeyError as exc:
        raise SvfError(f"line {line}: unsupported TAP state {value!r}") from exc


def _hex(value: str, bits: int, line: int) -> bytes:
    digits = "".join(value[1:-1].split())
    number = int(digits, 16)
    if number.bit_length() > bits:
        raise SvfError(f"line {line}: value {value} does not fit in {bits} bits")
    return number.to_bytes((bits + 7) // 8, "little")


def parse_statement(text: str, line: int) -> Command:
    item = tokens(text, line)
    if not item:
        raise SvfError(f"line {line}: empty statement")
    name = item.pop(0).upper()

    if name == "FREQUENCY":
        if len(item) != 2 or item[1].upper() != "HZ":
            raise SvfError(f"line {line}: expected FREQUENCY <number> HZ")
        return Command(name, (float(item[0]),), line)

    if name == "TRST":
        if len(item) != 1 or item[0].upper() != "ABSENT":
            raise SvfError(f"line {line}: sample player only supports TRST ABSENT")
        return Command(name, ("ABSENT",), line)

    if name in ("ENDDR", "ENDIR"):
        if len(item) != 1:
            raise SvfError(f"line {line}: expected {name} <state>")
        return Command(name, (_state(item[0], line),), line)

    if name == "STATE":
        if not item:
            raise SvfError(f"line {line}: STATE requires at least one state")
        return Command(name, tuple(_state(value, line) for value in item), line)

    if name == "RUNTEST":
        run_state = None
        end_state = None
        if item and item[0].upper() in STATE:
            run_state = _state(item.pop(0), line)
        if len(item) < 2 or item[1].upper() != "TCK":
            raise SvfError(f"line {line}: expected RUNTEST [state] <count> TCK")
        count = int(item.pop(0), 10)
        item.pop(0)
        if item:
            if len(item) != 2 or item[0].upper() != "ENDSTATE":
                raise SvfError(f"line {line}: unsupported RUNTEST option")
            end_state = _state(item[1], line)
        return Command(name, (count, run_state, end_state), line)

    if name in ("SIR", "SDR"):
        if not item:
            raise SvfError(f"line {line}: {name} requires a bit length")
        bits = int(item.pop(0), 10)
        if bits <= 0:
            raise SvfError(f"line {line}: {name} bit length must be positive")
        values: dict[str, bytes] = {}
        while item:
            key = item.pop(0).upper()
            if key not in SCAN_KEYS or not item:
                raise SvfError(f"line {line}: unsupported {name} option {key!r}")
            values[key] = _hex(item.pop(0), bits, line)
        if "TDI" not in values:
            raise SvfError(f"line {line}: {name} without TDI is not supported")
        return Command(name, (bits, values), line)

    raise SvfError(f"line {line}: unsupported command {name!r}")


def parse(path: Path) -> Iterator[Command]:
    for line, statement in statements(path):
        yield parse_statement(statement, line)


def crc8(data: bytes) -> int:
    value = 0
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = ((value << 1) ^ 0x07) & 0xFF if value & 0x80 else value << 1
    return value


class McjPlayer:
    def __init__(self, serial_port: BinaryIO):
        self.serial = serial_port

    def _write(self, command: int, payload: bytes = b"") -> None:
        self.serial.write(bytes((command,)) + payload)

    def control(self, command: int, value: int = 0) -> int:
        frame = bytes((command,)) + struct.pack("<I", value)
        self.serial.write(frame + bytes((crc8(frame),)))
        reply = self.serial.read(6)
        if len(reply) != 6:
            raise RuntimeError(f"timeout waiting for control reply 0x{command:02X}")
        if crc8(reply[:-1]) != reply[-1]:
            raise RuntimeError("bad CRC8 in control reply")
        if reply[0] != command:
            raise RuntimeError("unexpected control reply")
        return struct.unpack("<I", reply[1:5])[0]

    def sync(self) -> None:
        status = self.control(CMD_CTRL_GET_STATUS)
        if status:
            raise RuntimeError(f"MCJ firmware status error: 0x{status:08X}")

    def execute(self, command: Command) -> None:
        name = command.name
        if name == "FREQUENCY":
            # V0.1.0 accepts CMD_JTAG_FREQUENCY with no payload and ignores it.
            self._write(CMD_JTAG_FREQUENCY)
        elif name == "TRST":
            # TRST ABSENT is a declaration, not a request to pulse reset.
            return
        elif name in ("ENDDR", "ENDIR"):
            self._write(CMD_JTAG_ENDDR if name == "ENDDR" else CMD_JTAG_ENDIR,
                        bytes((command.args[0],)))
        elif name == "STATE":
            for state in command.args:
                self._write(CMD_JTAG_STATE, bytes((state,)))
        elif name == "RUNTEST":
            count, run_state, end_state = command.args
            if run_state is not None:
                self._write(CMD_JTAG_STATE, bytes((run_state,)))
            self._write(CMD_JTAG_RUNTEST, struct.pack("<I", count))
            if end_state is not None and end_state != run_state:
                self._write(CMD_JTAG_STATE, bytes((end_state,)))
        elif name in ("SIR", "SDR"):
            bits, values = command.args
            code = CMD_JTAG_SIR if name == "SIR" else CMD_JTAG_SDR
            self._write(code, struct.pack("<I", bits) + values["TDI"])
            received = self.serial.read((bits + 7) // 8)
            if len(received) != (bits + 7) // 8:
                raise RuntimeError(f"line {command.line}: timeout waiting for {name} TDO")
            if "TDO" in values:
                mask = values.get("MASK", b"\xFF" * len(received))
                mismatch = bytes((a ^ b) & m for a, b, m in zip(received, values["TDO"], mask))
                if any(mismatch):
                    raise RuntimeError(
                        f"line {command.line}: {name} TDO mismatch: "
                        f"actual={int.from_bytes(received, 'little'):X}, "
                        f"expected={int.from_bytes(values['TDO'], 'little'):X}"
                    )
        else:
            raise AssertionError(name)


def dry_run(path: Path) -> Stats:
    stats = Stats()
    for command in parse(path):
        stats.add(command)
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Play the Quartus sample SVF through MCJ firmware")
    parser.add_argument("svf", type=Path)
    parser.add_argument("port", nargs="?", help="COM port; omit for parser-only dry run")
    parser.add_argument("--baudrate", type=int, default=BAUDRATE)
    parser.add_argument("--sync-every", type=int, default=64,
                        help="query firmware status after this many SVF commands")
    args = parser.parse_args(argv)

    if not args.port:
        stats = dry_run(args.svf)
        print(f"OK: {stats.commands} commands, {stats.shifted_bits} shifted bits, "
              f"{stats.tdo_checks} TDO checks")
        for name in sorted(stats.counts):
            print(f"  {name:9s} {stats.counts[name]:5d}")
        return 0

    try:
        import serial
    except ImportError:
        parser.error("pyserial is required when a COM port is specified")

    with serial.Serial(args.port, args.baudrate, timeout=2, write_timeout=2) as port:
        player = McjPlayer(port)
        player.control(CMD_CTRL_SET_STATUS, 0xFFFFFFFF)
        # Establish a known TAP state because TRST ABSENT does not drive a pin.
        player._write(CMD_JTAG_TRST)
        for index, command in enumerate(parse(args.svf), 1):
            player.execute(command)
            if args.sync_every and index % args.sync_every == 0:
                player.sync()
            if index % 1000 == 0:
                print(f"{index} commands", file=sys.stderr)
        player.sync()
    print("SVF completed successfully")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, SvfError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
