import sys
import ctypes
import serial
from crc8 import crc8

CMD_CTRL_GET_TEST	 = 0x01
CMD_CTRL_GET_VERSION = 0x02
CMD_CTRL_GET_STATUS	 = 0x03
CMD_CTRL_GET_CRC16	 = 0x04
CMD_CTRL_GET_FLOW	 = 0x05
CMD_CTRL_SET_TEST	 = 0x08
CMD_CTRL_SET_STATUS  = 0x0B
CMD_CTRL_SET_CRC16	 = 0x0C
CMD_CTRL_SET_FLOW	 = 0x0D

CMD_JTAG_FREQUENCY	 = 0x80
CMD_JTAG_TRST		 = 0x81
CMD_JTAG_STATE		 = 0x82
CMD_JTAG_ENDDR		 = 0x83
CMD_JTAG_ENDIR		 = 0x84
CMD_JTAG_RUNTEST	 = 0x85
CMD_JTAG_SDR		 = 0x86
CMD_JTAG_SIR		 = 0x87

CMD_IS_JTAG          = 0x80

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
        test_data = 0x01234567
        wr_tx_frame = CTRL_FRAME(cmd=CMD_CTRL_SET_TEST, data=DATA(dword=test_data))
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
        if rd_tx_frame.data.dword == 0x00000000:
            ok_count = ok_count + 1
            print(f"  Test Result(OK)\n")
        else:
            print(f"  Test Result(NG)\n")

        print(f"test_count = {test_count}")
        print(f"ok_count   = {ok_count}")

        ############################################################################
        print("Test 014: reads CRC after write")
        test_count = test_count + 1
        test_data1 = 0x0123
        test_data2 = 0x0123
        wr_tx_frame = CTRL_FRAME(cmd=CMD_CTRL_SET_TEST, data=DATA(dword=test_data))
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


#    print(f"IDCODE:           0x{idcode.raw:08X}")
#    print(f"LSB(should be 1): 0x{idcode.bits.lsb:02X}")
#    print(f"Manufacture ID:   0x{idcode.bits.manufacture_id:04X}")
#    print(f"Part Number:      0x{idcode.bits.part_number:04X}")
#    print(f"Version:          0x{idcode.bits.version:02X}")




#    print(f"IDCODE:           0x{idcode.raw:08X}")
#    print(f"LSB(should be 1): 0x{idcode.bits.lsb:02X}")
#    print(f"Manufacture ID:   0x{idcode.bits.manufacture_id:04X}")
#    print(f"Part Number:      0x{idcode.bits.part_number:04X}")
#    print(f"Version:          0x{idcode.bits.version:02X}")
