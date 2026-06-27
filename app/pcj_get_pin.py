import serial
import ctypes
import sys
import time
from MAXV_5M40ZE64 import OPCODE, DR_LENGTH, INPUT

H=1
L=0


class XxD_STRUCT(ctypes.LittleEndianStructure):
    """Bit layout of one UART byte: TMS/TCK/TDI out, TDO in."""
    _fields_ = [
        ("tms_out", ctypes.c_uint8, 1),
        ("tck_out", ctypes.c_uint8, 1),
        ("tdi_out", ctypes.c_uint8, 1),
        ("tdo_in",  ctypes.c_uint8, 1),
        ("dummy",   ctypes.c_uint8, 4),
    ]


class XxD(ctypes.Union):
    """Union: access the UART byte as bit fields or as raw uint8."""
    _fields_ = [("bits", XxD_STRUCT), ("raw", ctypes.c_uint8)]


def jtag(ser, tms, tdi):
    """TCK cycle: shift one bit in/out. Returns the TDO bit."""
    txd = XxD()
    rxd = XxD()
    txd.bits.tms_out = tms
    txd.bits.tdi_out = tdi
    txd.bits.tck_out = H
    ser.write(bytes(txd))
    rxd.raw=bytes(ser.read(1))[0]
    tdo = rxd.bits.tdo_in
    txd.bits.tck_out = L
    ser.write(bytes(txd))
    rxd.raw=bytes(ser.read(1))[0]
    return tdo


def get_sample(ser):
    # Set SAMPLE OPCODE
    bits = list(reversed(OPCODE["SAMPLE"]))
    for _ in range(5):
        jtag(ser, H, L)                                                   # to Test-Logic-Reset
    jtag(ser, L, L)                                                       # to Run-Test/Idle
    jtag(ser, H, L)                                                       # to Select-DR-Scan
    jtag(ser, H, L)                                                       # to Select-IR-Scan
    jtag(ser, L, L)                                                       # to Capture-IR
    jtag(ser, L, L)                                                       # to Shift-IR
    for bit in bits[:-1]:
        jtag(ser, L, bit == "1")                                          # Shift-IR
    jtag(ser, H, bits[-1] == "1")                                         # to Exit1-IR (last 1 bit)
    jtag(ser, H, L)                                                       # to Update-IR
    jtag(ser, L, L)                                                       # to Run-Test/Idle

    # Get SAMPLE Data
    jtag(ser, H, L)                                                       # to Select-DR-Scan
    jtag(ser, L, L)                                                       # to Capture-DR
    jtag(ser, L, L)                                                       # to Shift-DR
    sample_bits = [jtag(ser, L, L) for _ in range(DR_LENGTH["SAMPLE"]-1)] # Shift-DR (1 bit left)
    sample_bits.append(jtag(ser, H, L))                                   # to Exit1 (last 1 bit)
    jtag(ser, H, L)                                                       # to Update-DR
    jtag(ser, L, L)                                                       # to Run-Test/Idle
    return sample_bits


if __name__ == "__main__":
    if(len(sys.argv)!=3):
       print(f"Usage: {sys.argv[0]} <COMn or /dev/tty*> <IOn>");
       sys.exit(2) #os.EX_USAGE

    com_num = sys.argv[1]
    io_num  = sys.argv[2]

    with serial.Serial(com_num, 1000000, timeout=0.1) as ser:
        sample = get_sample(ser)

    print(f"SAMPLE({io_num}):{sample[INPUT[io_num]]}")