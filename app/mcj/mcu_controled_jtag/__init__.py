import ctypes


BAUDRATE = 1000000  # All UART communication in this project uses 1 Mbps.
FRAME_SIZE = 10
DATA_SIZE = 8


class JTAG_STRUCT(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("length_minus_1", ctypes.c_uint8, 6),
        ("tms", ctypes.c_uint8, 1),
        ("mode", ctypes.c_uint8, 1),
        ("data", ctypes.c_uint8 * DATA_SIZE),
        ("crc", ctypes.c_uint8),
    ]


class CTRL_STRUCT(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("command", ctypes.c_uint8, 6),
        ("reserved", ctypes.c_uint8, 1),
        ("mode", ctypes.c_uint8, 1),
        ("address", ctypes.c_uint32),
        ("data", ctypes.c_uint32),
        ("crc", ctypes.c_uint8),
    ]


class COMMON_STRUCT(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("echo_back", ctypes.c_uint8, 6),
        ("error", ctypes.c_uint8, 1),
        ("mode", ctypes.c_uint8, 1),
        ("unused", ctypes.c_uint8 * DATA_SIZE),
        ("crc", ctypes.c_uint8),
    ]


class FRAME(ctypes.Union):
    _pack_ = 1
    _fields_ = [
        ("raw", ctypes.c_uint8 * FRAME_SIZE),
        ("jtag", JTAG_STRUCT),
        ("control", CTRL_STRUCT),
        ("common", COMMON_STRUCT),
    ]


def crc8(data):
    """CRC-8/SMBus: polynomial 0x07, initial value 0x00."""
    result = 0
    for byte in data:
        result ^= byte
        for _ in range(8):
            if result & 0x80:
                result = ((result << 1) ^ 0x07) & 0xFF
            else:
                result = (result << 1) & 0xFF
    return result


class JTAG_DATA:
    def __init__(self, tms, length, data):
        if not 1 <= length <= 64:
            raise ValueError("length must be from 1 to 64")

        frame = FRAME()
        frame.jtag.length_minus_1 = length - 1
        frame.jtag.tms = bool(tms)
        frame.jtag.mode = 0
        frame.jtag.data[:] = int(data).to_bytes(DATA_SIZE, "little")
        frame.jtag.crc = crc8(frame.raw[:-1])
        self.raw = bytes(frame)


class CTRL_DATA:
    def __init__(self, command, address=0, data=0):
        frame = FRAME()
        frame.control.command = command
        frame.control.reserved = 0
        frame.control.mode = 1
        frame.control.address = address
        frame.control.data = data
        frame.control.crc = crc8(frame.raw[:-1])
        self.raw = bytes(frame)


# One TCK cycle with TDI low. These CRC values are calculated only once.
JTAG_TMS_L = JTAG_DATA(tms=0, length=1, data=0).raw
JTAG_TMS_H = JTAG_DATA(tms=1, length=1, data=0).raw


class mcu_controled_jtag:
    def __init__(self, ser):
        self.ser = ser

    def jtag(self, tms, tdi=0, length=1):
        """Clock 1 to 64 JTAG bits and return the sampled TDO bits as an int."""
        if length == 1 and tdi == 0:
            tx_data = JTAG_TMS_H if tms else JTAG_TMS_L
        else:
            tx_data = JTAG_DATA(tms, length, tdi).raw

        rx_frame = self._transfer(tx_data)
        return int.from_bytes(bytes(rx_frame.jtag.data), "little")

    def control(self, command, address=0, data=0):
        tx_data = CTRL_DATA(command, address, data).raw
        rx_frame = self._transfer(tx_data)
        return rx_frame.control.address, rx_frame.control.data

    def _transfer(self, tx_data):
        self.ser.write(tx_data)
        received = self.ser.read(FRAME_SIZE)
        if len(received) != FRAME_SIZE:
            raise TimeoutError(f"received {len(received)} of {FRAME_SIZE} bytes")

        rx_frame = FRAME.from_buffer_copy(received)
        if crc8(rx_frame.raw[:-1]) != rx_frame.common.crc:
            raise ValueError("RXD CRC error")
        if rx_frame.common.error:
            raise RuntimeError("MCJ reported an error")

        return rx_frame


assert ctypes.sizeof(FRAME) == FRAME_SIZE
