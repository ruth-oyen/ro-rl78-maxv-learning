import sys
import ctypes
import serial
from crc8 import crc8
from mcj import *

BAUDRATE = 1_000_000 # All UART communication in this project uses 1[Mbps]

H=1
L=0


class BYTES(ctypes.LittleEndianStructure):
    _fields_ = [
        ("b0", ctypes.c_uint8),
        ("b1", ctypes.c_uint8),
        ("b2", ctypes.c_uint8),
        ("b3", ctypes.c_uint8),
    ]


class WORDS(ctypes.LittleEndianStructure):
    _fields_ = [
        ("w0", ctypes.c_uint16,),
        ("w1", ctypes.c_uint16,),
    ]


class DATA(ctypes.Union):
    _fields_ = [
        ("bytes", BYTES),
        ("words", WORDS),
        ("dword", ctypes.c_uint32),
    ]


class CTRL_FRAME(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("cmd", ctypes.c_uint8),
        ("data", DATA),
        ("crc", ctypes.c_uint8),
    ]


def send_rciv_frame(frame):
        frame.crc = crc8(bytearray(frame)[:-1]).digest()[0]
        ser.write(bytearray(frame))
        return CTRL_FRAME.from_buffer_copy(ser.read(ctypes.sizeof(CTRL_FRAME)))


if __name__ == "__main__":
    if(len(sys.argv)!=2):
        print(f"Usage: {sys.argv[0]} <COMn or /dev/tty*>");
        sys.exit(2) #os.EX_USAGE

    com_num = sys.argv[1]

    with serial.Serial(com_num, BAUDRATE, timeout=0.1) as ser:
        test_count = 0
        ok_count = 0

        ############################################################################
        print("Test 01 : reads TEST after write")
        test_count = test_count + 1
        test_data = DATA(dword=0x01234567)
        wr_tx_frame = CTRL_FRAME(cmd=CMD_CTRL_SET_TEST, data=test_data)
        wr_rx_frame = send_rciv_frame(wr_tx_frame)
        print(f"  CMD_CTRL_SET_TEST:    Write = 0x{wr_tx_frame.data.dword:08X}")
        rd_tx_frame = CTRL_FRAME(cmd=CMD_CTRL_GET_TEST)
        rd_rx_frame = send_rciv_frame(rd_tx_frame)
        print(f"  CMD_CTRL_GET_TEST:    Read  = 0x{rd_rx_frame.data.dword:08X}")
        if wr_tx_frame.data.dword == rd_rx_frame.data.dword:
            ok_count = ok_count + 1
            print(f"  Test Result(OK)\n")
        else:
            print(f"  Test Result(NG)\n")

        ############################################################################
        print("Test 02 : reads version")
        test_count = test_count + 1
        rd_tx_frame = CTRL_FRAME(cmd=CMD_CTRL_GET_VERSION)
        rd_rx_frame = send_rciv_frame(rd_tx_frame)
        print(f"  CMD_CTRL_GET_VERSION: Read  = 0x{rd_rx_frame.data.dword:08X}")
        if rd_rx_frame.data.dword == 0x00000100:
            ok_count = ok_count + 1
            print(f"  Test Result(OK)\n")
        else:
            print(f"  Test Result(NG)\n")

        ############################################################################
        print("Test 03 : reads status")
        test_count = test_count + 1
        rd_tx_frame = CTRL_FRAME(cmd=CMD_CTRL_GET_STATUS)
        rd_rx_frame = send_rciv_frame(rd_tx_frame)
        print(f"  CMD_CTRL_GET_STATUS:  Read  = 0x{rd_rx_frame.data.dword:08X}")
        if rd_rx_frame.data.dword == 0x00000000:
            ok_count = ok_count + 1
            print(f"  Test Result(OK)\n")
        else:
            print(f"  Test Result(NG)\n")

        ############################################################################
        print("Test 04: reads CRC after write")
        test_count = test_count + 1
        test_data = DATA(words=WORDS(w0=0xCDEF, w1=0x89AB))
        wr_tx_frame = CTRL_FRAME(cmd=CMD_CTRL_SET_CRC16, data=test_data)
        wr_rx_frame = send_rciv_frame(wr_tx_frame)
        print(f"  CMD_CTRL_SET_CRC16:   Write = 0x{wr_tx_frame.data.dword:08X}")
        rd_tx_frame = CTRL_FRAME(cmd=CMD_CTRL_GET_CRC16)
        rd_rx_frame = send_rciv_frame(rd_tx_frame)
        print(f"  CMD_CTRL_GET_CRC16:   Read  = 0x{rd_rx_frame.data.dword:08X}")
        if wr_tx_frame.data.dword == rd_rx_frame.data.dword:
            ok_count = ok_count + 1
            print(f"  Test Result(OK)\n")
        else:
            print(f"  Test Result(NG)\n")

        print(f"test_count = {test_count}")
        print(f"ok_count   = {ok_count}")
