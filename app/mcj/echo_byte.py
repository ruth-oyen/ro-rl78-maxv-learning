import serial


PORT = "COM15"
BAUDRATE = 1_000_000
TEST_DATA = b"\x55"


with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
    ser.reset_input_buffer()
    ser.write(TEST_DATA)
    received = ser.read(1)

print(f"TX: 0x{TEST_DATA[0]:02X}")

if received:
    print(f"RX: 0x{received[0]:02X}")
else:
    print("RX: timeout")
