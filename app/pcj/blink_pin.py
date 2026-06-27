import serial
import sys
import time
from MAXV_5M40ZE64 import DR_LENGTH, CONTROL, OUTPUT
from pcj.set_pin import H, L, jtag, set_pin

BAUDRATE = 1000000 # All UART communication in this project uses 1[Mbps]


if __name__ == "__main__":
    if(len(sys.argv)!=3):
       print(f"Usage: {sys.argv[0]} <COMn or /dev/tty*> <IOn>");
       sys.exit(2) #os.EX_USAGE

    com_num = sys.argv[1]
    io_num  = sys.argv[2]

    boundary_bits = [L] * DR_LENGTH["EXTEST"]
    for bit_number in CONTROL.values():
        boundary_bits[bit_number] = H
    boundary_bits[OUTPUT[io_num]] = H
    boundary_bits[CONTROL[io_num]] = L

    with serial.Serial(com_num, BAUDRATE, timeout=0.1) as ser:
        set_pin(ser, io_num, H)

        try:
            while True:
                for output_value in (L, H):
                    time.sleep(0.5)
                    boundary_bits[OUTPUT[io_num]] = output_value

                    jtag(ser, H, L)                # to Select-DR-Scan
                    jtag(ser, L, L)                # to Capture-DR
                    jtag(ser, L, L)                # to Shift-DR
                    for bit in boundary_bits[:-1]:
                        jtag(ser, L, bit)           # Shift-DR
                    jtag(ser, H, boundary_bits[-1]) # to Exit1-DR (last 1 bit)
                    jtag(ser, H, L)                 # to Update-DR
                    jtag(ser, L, L)                 # to Run-Test/Idle
        except KeyboardInterrupt:
            for _ in range(5):
                jtag(ser, H, L)                    # to Test-Logic-Reset
