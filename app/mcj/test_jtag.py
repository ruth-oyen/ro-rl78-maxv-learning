import sys
import time
import serial
from time import sleep
from crc8 import crc8
from pathlib import Path
from mcj import *


start_time = time.perf_counter()

OK = 0
NG = 1

def log(message: str):
    elapsed = time.perf_counter() - start_time
    print(f"[{elapsed:8.3f} s] {message}")


def i2c(cnt):
    return bytearray(int(cnt).to_bytes(4, "little"))


def i2b(bits, val):
    return i2c(bits) + bytearray(val.to_bytes((bits + 7) // 8, "little"))


def svf_init(ser):
    ser.write(bytearray([CMD_JTAG_FREQUENCY, 0x00]))                        # FREQUENCY 1.00E+06 HZ; //ignored in mcj v0.1.0
    ser.write(bytearray([CMD_JTAG_TRST,      CMD_JTAG_TRST_ABSEN]))         # TRST ABSENT;           //ignored in mcj v0.1.0
    ser.write(bytearray([CMD_JTAG_ENDDR,     STATE_RUN_TEST_IDLE]))         # ENDDR IDLE;
    ser.write(bytearray([CMD_JTAG_ENDIR,     STATE_PAUSE_IR]))              # ENDIR IRPAUSE;
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # STATE IDLE;
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x005))               # SIR 10 TDI (005);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # RUNTEST IDLE 
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       #              8 TCK ENDSTATE IDLE;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(240, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)) # SDR 240 TDI (FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x3FF))               # SIR 10 TDI (3FF);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(1003))                    # RUNTEST 1003 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x2CC))               # SIR 10 TDI (2CC);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(1003))                    # RUNTEST 1003 TCK;
    ser.read(1)


def svf_check_silicon_id(ser):
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0089))              # SDR 13 TDI (0089);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x205))               # SIR 10 TDI (205);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR_TDO]) + i2b(16, 0xFFFF))              # SDR 16 TDI (FFFF) TDO (8232) MASK (FFFF);
    id = f"{int.from_bytes(ser.read(2), 'little'):04x} "
    ser.write(bytearray([CMD_JTAG_SDR_TDO]) + i2b(16, 0xFFFF))              # SDR 16 TDI (FFFF) TDO (2AA2);
    id = id + f"{int.from_bytes(ser.read(2), 'little'):04x} "
    ser.write(bytearray([CMD_JTAG_SDR_TDO]) + i2b(16, 0xFFFF))              # SDR 16 TDI (FFFF) TDO (4A82);
    id = id + f"{int.from_bytes(ser.read(2), 'little'):04x} "
    ser.write(bytearray([CMD_JTAG_SDR_TDO]) + i2b(16, 0xFFFF))              # SDR 16 TDI (FFFF) TDO (8C0C);
    id = id + f"{int.from_bytes(ser.read(2), 'little'):04x} "
    ser.write(bytearray([CMD_JTAG_SDR_TDO]) + i2b(16, 0xFFFF))              # SDR 16 TDI (FFFF) TDO (0000);
    id = id + f"{int.from_bytes(ser.read(2), 'little'):04x}"
    return id


def svf_bulk_erase(ser):
    # Erase UFM sector 1
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0011))              # SDR 13 TDI (0011);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x2F2))               # SIR 10 TDI (2F2);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(500003))                  # RUNTEST 500003 TCK;
    ser.read(1)
    # Erase UFM sector 0
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0001))              # SDR 13 TDI (0001);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x2F2))               # SIR 10 TDI (2F2);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(500003))                  # RUNTEST 500003 TCK;
    ser.read(1)
    # Erase CFM sector 0
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0000))              # SDR 13 TDI (0000);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x2F2))               # SIR 10 TDI (2F2);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(500003))                  # RUNTEST 500003 TCK;
    ser.read(1)


def svf_program_cfm(ser, filename):
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0000))              # SDR 13 TDI (0000);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x2F4))               # SIR 10 TDI (2F4);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    with open(filename, "rb") as f:
        for i in range(3328):
            if len(write_data := f.read(2)) != 2:
                raise ValueError("Odd number of bytes")
            value = int.from_bytes(write_data, byteorder="little")
            ser.write(bytearray([CMD_JTAG_SDR])     + i2b(16, value))       # SDR 16 TDI (****);
            ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE])) # sticky STATE IDLE from previous RUNTEST IDLE
            ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(100))             # RUNTEST 100 TCK;
            ser.read(1)


def svf_program_ufm(ser, filename):
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0001))              # SDR 13 TDI (0001);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x2F4))               # SIR 10 TDI (2F4);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    with open(filename, "rb") as f:
        for i in range(512):
            if len(write_data := f.read(2)) != 2:
                raise ValueError("Odd number of bytes")
            value = int.from_bytes(write_data, byteorder="little")
            ser.write(bytearray([CMD_JTAG_SDR])     + i2b(16, value))       # SDR 16 TDI (****);
            ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE])) # sticky STATE IDLE from previous RUNTEST IDLE
            ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(100))             # RUNTEST 100 TCK;
            ser.read(1)


def svf_verify_cfm(ser, filename):
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0000))              # SDR 13 TDI (0000);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x205))               # SIR 10 TDI (205);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    with open(filename, "rb") as f:
        for i in range(3328):
            if len(verify_data := f.read(2)) != 2:
                raise ValueError("Odd number of bytes")
            ser.write(bytearray([CMD_JTAG_SDR_TDO])     + i2b(16, 0xFFFF))  # SDR 16 TDI (FFFF) TDO (****) MASK (FFFF);
            read_data = ser.read(2)
            if verify_data != read_data:                                  #                         
                print(f"i={i}:len(verify_data)={len(verify_data)}, len(read_data)={len(read_data.hex())}")
                print(f"i={i}:verify_data={verify_data.hex()}, read_data={read_data.hex()}")
                return NG
    return OK


def svf_verify_ufm(ser, filename):
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0001))              # SDR 13 TDI (0001);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x205))               # SIR 10 TDI (205);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    with open(filename, "rb") as f:
        for i in range(512):
            if len(verify_data := f.read(2)) != 2:
                raise ValueError("Odd number of bytes")
            ser.write(bytearray([CMD_JTAG_SDR_TDO])     + i2b(16, 0xFFFF))  # SDR 16 TDI (FFFF) TDO (****) MASK (FFFF);
            if verify_data != ser.read(2):                                  #                         
                return NG
    return OK


def svf_finalize(ser, filename):
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x203))               # SIR 10 TDI (203);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SDR])     + i2b(13, 0x0000))              # SDR 13 TDI (0000);
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x2F4))               # SIR 10 TDI (2F4);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(8))                       # RUNTEST 8 TCK;
    ser.read(1)

    with open(filename, "rb") as f:
        finalize_data = f.read(2)
        value = int.from_bytes(finalize_data, byteorder="little") & 0xFBFF
        ser.write(bytearray([CMD_JTAG_SDR])     + i2b(16, value))           # SDR 16 TDI (7BFF);
        ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))     # sticky STATE IDLE from previous RUNTEST IDLE
        ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(100))                 # RUNTEST 100 TCK;
        ser.read(1)

        finalize_data = f.read(2)
        value = int.from_bytes(finalize_data, byteorder="little")
        ser.write(bytearray([CMD_JTAG_SDR])     + i2b(16, value))           # SDR 16 TDI (FFFF);
        ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))     # sticky STATE IDLE from previous RUNTEST IDLE
        ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(100))                 # RUNTEST 100 TCK;
        ser.read(1)

        finalize_data = f.read(2)
        value = int.from_bytes(finalize_data, byteorder="little")
        ser.write(bytearray([CMD_JTAG_SDR])     + i2b(16, value))           #  SDR 16 TDI (BFFC);
        ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))     # sticky STATE IDLE from previous RUNTEST IDLE
        ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(100))                 # RUNTEST 100 TCK;
        ser.read(1)

        finalize_data = f.read(2)
        value = int.from_bytes(finalize_data, byteorder="little")
        ser.write(bytearray([CMD_JTAG_SDR])     + i2b(16, value))           # SDR 16 TDI (FFE7);
        ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))     # sticky STATE IDLE from previous RUNTEST IDLE
        ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(100))                 # RUNTEST 100 TCK;
        ser.read(1)

    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x201))               # SIR 10 TDI (201);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(1003))                    # RUNTEST 1003 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_SIR])     + i2b(10, 0x3FF))               # SIR 10 TDI (3FF);
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # sticky STATE IDLE from previous RUNTEST IDLE
    ser.write(bytearray([CMD_JTAG_RUNTEST]) + i2c(1000))                    # RUNTEST 1000 TCK;
    ser.read(1)
    ser.write(bytearray([CMD_JTAG_STATE,     STATE_RUN_TEST_IDLE]))         # STATE IDLE;

    ser.flush()

def svf_idcode(ser):
    ser.write(bytearray([CMD_JTAG_STATE, STATE_SHIFT_DR]))
    ser.write(bytearray([CMD_JTAG_SDR_TDO]) + i2b(32, 0x00000000))
    return int.from_bytes(ser.read(4), 'little')


BAUDRATE = 1_000_000 # All UART communication in this project uses 1[Mbps]


def fw_get_status(ser):
    tx = bytearray([CMD_CTRL_GET_STATUS, 0, 0, 0, 0])
    tx.append(crc8(tx).digest()[0])

    ser.write(tx)
    rx = ser.read(6)

    if len(rx) != 6:
        print(f"GET_STATUS no response: {rx.hex()}")
        return None

    status = int.from_bytes(rx[1:5], "little")
    print(f"FW STATUS = 0x{status:08x}")
    return status


if __name__ == "__main__":
    if(len(sys.argv)!=2):
        print(f"Usage: {sys.argv[0]} <COMn or /dev/tty*>");
        sys.exit(2) #os.EX_USAGE

    com_num = sys.argv[1]

    cfm_filename = "./base3.cfm"
    ufm_filename = "./base3.ufm"

    with serial.Serial(com_num, BAUDRATE, timeout=6) as ser:

        ser.write(bytearray([CMD_JTAG_TRST, CMD_JTAG_TRST_FORCE])) 
        log("Force the TAP controller reset by applying five TCK cycles with TMS High")

        idcode = svf_idcode(ser)
        log(f"IDCODE     = 0x{idcode:08x} (OK)")
        if idcode != 0x020a50dd:
            log("IDCODE does not 0x020A50DD(MAXV 5M40Z, 5M80Z, 5M160Z)")
            sys.exit(1)

        svf_init(ser)
        silicon_id = svf_check_silicon_id(ser)
        if silicon_id == "8232 2aa2 4a82 8c0c 0000":
            log(f"SILICON ID = {silicon_id} (OK)")
        else:
            log(f"SILICON ID = {silicon_id} (This value should be '8232 2aa2 4a82 8c0c 0000'")
            sys.exit(1)

        if Path(cfm_filename).stat().st_size != 6656:
            log("Invalid CFM file size")
            sys.exit(1)

        if Path(ufm_filename).stat().st_size != 1024:
            log("Invalid UFM file size")
            sys.exit(1)

        log("Erase UFM and CFM start")
        svf_bulk_erase(ser)
        log("Erase UFM and CFM end")

        log("Program CFM start")
        svf_program_cfm(ser, cfm_filename)
        log("Program CFM end")

        log("Program UFM start")
        svf_program_ufm(ser, ufm_filename)
        log("Program UFM end")

        log("Verify CFM start")
        if svf_verify_cfm(ser, cfm_filename) == OK:
            log("Verify CFM end")
        else:
            log("Verify CFM failed")
            sys.exit(1)

        log("Verify UFM start")
        if svf_verify_ufm(ser, ufm_filename) == OK:
            log("Verify UFM end")
        else:
            log("Verify UFM failed")
            sys.exit(1)

        log("Finalize start")
        svf_finalize(ser, cfm_filename)
        log("Finalize end")