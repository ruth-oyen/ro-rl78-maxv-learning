import crc8
import serial


PORT = "COM15"
BAUDRATE = 1_000_000
CMD_CTRL_GET_TEST = 0x01
FRAME_SIZE = 6


tx_frame = bytearray([CMD_CTRL_GET_TEST, 0x00, 0x00, 0x00, 0x00])
tx_frame += crc8.crc8(tx_frame).digest()

with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
    ser.reset_input_buffer()
    ser.write(tx_frame)
    rx_frame = ser.read(FRAME_SIZE)

if len(rx_frame) != FRAME_SIZE:
    raise RuntimeError(f"RX timeout: received {len(rx_frame)} of {FRAME_SIZE} bytes")

if rx_frame[0] != CMD_CTRL_GET_TEST:
    raise RuntimeError(f"Unexpected command echo: 0x{rx_frame[0]:02X}")

rx_crc = crc8.crc8(rx_frame[:-1]).digest()[0]
if rx_frame[-1] != rx_crc:
    raise RuntimeError(
        f"CRC error: received 0x{rx_frame[-1]:02X}, calculated 0x{rx_crc:02X}"
    )

test_value = int.from_bytes(rx_frame[1:5], byteorder="little")

print(f"TX: {tx_frame.hex(' ')}")
print(f"RX: {rx_frame.hex(' ')}")
print(f"TEST: 0x{test_value:08X}")
