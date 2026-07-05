import sys
import serial
from time import sleep
from crc8 import crc8


BAUDRATE = 1_000_000 # All UART communication in this project uses 1[Mbps]

H=1
L=0

TEST_LOGIC_RESET = 0x00
RUN_TEST_IDLE    = 0x01

SELECT_DR_SCAN   = 0x02
CAPTURE_DR       = 0x03
SHIFT_DR         = 0x04
EXIT1_DR         = 0x05
PAUSE_DR         = 0x06
EXIT2_DR         = 0x07
UPDATE_DR        = 0x08

SELECT_IR_SCAN   = 0x09
CAPTURE_IR       = 0x0A
SHIFT_IR         = 0x0B
EXIT1_IR         = 0x0C
PAUSE_IR         = 0x0D
EXIT2_IR         = 0x0E
UPDATE_IR        = 0x0F

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




if __name__ == "__main__":
    if(len(sys.argv)!=2):
        print(f"Usage: {sys.argv[0]} <COMn or /dev/tty*>");
        sys.exit(2) #os.EX_USAGE

    com_num = sys.argv[1]

    with serial.Serial(com_num, BAUDRATE, timeout=0.1) as ser:
        ser.write( bytearray([ CMD_JTAG_TRST]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, TEST_LOGIC_RESET]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, RUN_TEST_IDLE]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, SELECT_DR_SCAN]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, CAPTURE_DR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, SHIFT_DR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, EXIT1_DR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, PAUSE_DR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, EXIT2_DR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, UPDATE_DR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, SELECT_IR_SCAN]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, CAPTURE_IR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, SHIFT_IR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, EXIT1_IR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, PAUSE_IR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, EXIT2_IR]))
        sleep(0.5)
        ser.write( bytearray([ CMD_JTAG_TRST, CMD_JTAG_STATE, UPDATE_IR]))
        sleep(0.5)

