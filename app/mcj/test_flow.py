import sys
import time
import serial
from time import sleep
from crc8 import crc8
from pathlib import Path
from mcj import *


start_time = time.perf_counter()

def log(message: str):
    elapsed = time.perf_counter() - start_time
    print(f"[{elapsed:8.3f} s] {message}")



BAUDRATE = 1_000_000 # All UART communication in this project uses 1[Mbps]

CTS_GO      = True
CTS_STOP    = False

def i2c(cnt):
    return bytearray(int(cnt).to_bytes(4, "little"))

if __name__ == "__main__":
    if(len(sys.argv)!=2):
        print(f"Usage: {sys.argv[0]} <COMn or /dev/tty*>");
        sys.exit(2) #os.EX_USAGE

    com_num = sys.argv[1]

    with serial.Serial(com_num, BAUDRATE, timeout=1, rtscts=False) as ser:
        # Ignored commands never be full
        #print("CTS_STOP" if ser.cts == CTS_STOP else "CTS_GO")
        #ser.write(bytearray([CMD_JTAG_FREQUENCY, 0x00]) * 350)
        #print("CTS_STOP" if ser.cts == CTS_STOP else "CTS_GO")

        ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))
        print("CTS_STOP" if ser.cts == CTS_STOP else "CTS_GO")
        ser.write((bytearray([CMD_JTAG_RUNTEST]) + i2c(1000000)) * 20)
        print("CTS_STOP" if ser.cts == CTS_STOP else "CTS_GO")