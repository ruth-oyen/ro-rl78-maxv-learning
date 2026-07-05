import crc8
import serial


PORT = "COM15"
BAUDRATE = 1_000_000
CMD_CTRL_GET_VERSION = 0x02


frame = bytearray([CMD_CTRL_GET_VERSION, 0x00, 0x00, 0x00, 0x00])
frame += crc8.crc8(frame).digest()

with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
    for i in range(100):
        ser.write(frame)
    for i in range(100):
        response = ser.read(6)

version = int.from_bytes(response[1:5], byteorder="little")
print(f"Version: 0x{version:08X}")
