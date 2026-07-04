import ctypes
import serial
import sys

from MAXV_5M40ZE64 import DR_LENGTH
from mcj.mcu_controled_jtag import BAUDRATE, mcu_controled_jtag


H = 1
L = 0


class IDCODE_STRUCT(ctypes.LittleEndianStructure):
    _fields_ = [
        ("lsb", ctypes.c_uint32, 1),
        ("manufacture_id", ctypes.c_uint32, 11),
        ("part_number", ctypes.c_uint32, 16),
        ("version", ctypes.c_uint32, 4),
    ]


class IDCODE(ctypes.Union):
    _fields_ = [
        ("bits", IDCODE_STRUCT),
        ("raw", ctypes.c_uint32),
    ]


def get_idcode(jtag):
    for _ in range(5):
        jtag.jtag(H)                                   # to Test-Logic-Reset
    jtag.jtag(L)                                       # to Run-Test/Idle
    jtag.jtag(H)                                       # to Select-DR-Scan
    jtag.jtag(L)                                       # to Capture-DR
    jtag.jtag(L)                                       # to Shift-DR
    idcode = jtag.jtag(H, length=DR_LENGTH["IDCODE"]) # to Exit1-DR
    jtag.jtag(H)                                       # to Update-DR
    jtag.jtag(L)                                       # to Run-Test/Idle
    return IDCODE(raw=idcode)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <COMn or /dev/tty*>")
        sys.exit(2)

    com_num = sys.argv[1]

    with serial.Serial(com_num, BAUDRATE, timeout=0.01) as ser:
        jtag = mcu_controled_jtag(ser)
        idcode = get_idcode(jtag)

    print(f"IDCODE:           0x{idcode.raw:08X}")
    print(f"LSB(should be 1): 0x{idcode.bits.lsb:02X}")
    print(f"Manufacture ID:   0x{idcode.bits.manufacture_id:04X}")
    print(f"Part Number:      0x{idcode.bits.part_number:04X}")
    print(f"Version:          0x{idcode.bits.version:02X}")
