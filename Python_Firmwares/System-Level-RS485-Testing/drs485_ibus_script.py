import serial
import time
import lgpio

# =============================
# CONFIG
# =============================

# AMA0 [IBUS DRS485] , AMA2 [EXBUS DRS485], AMA4 [EXP DRS485]

COM_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200
TIMEOUT = 2

# 18 [IBUS DRS485], 17 [EX BUS DRS485], 6 [EXP DRS485]

RS485_DE_PIN = 18

SRC_ADDR = 0x01
SEQ_ID   = 0x01
TYPE_REQ = 0x01
STATUS   = 0x00

# =============================
# GPIO INIT (RPI5)
# =============================
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, RS485_DE_PIN, 0)  # RX mode

# =============================
# COMMANDS (FULL)
# =============================
COMMANDS = {
    1:  ("Enclosure Open",      0x02, 0x02, [0x01]),
    2:  ("Enclosure Close",     0x02, 0x02, [0x00]),
    3:  ("Positioner Open",     0x02, 0x03, [0x01]),
    4:  ("Positioner Close",    0x02, 0x03, [0x00]),
    5:  ("Door Lock",           0x02, 0x01, [0x00]),
    6:  ("Door Unlock",         0x02, 0x01, [0x01]),

    7:  ("Drone Power ON",      0x04, 0x02, [0x01]),
    8:  ("Drone Power OFF",     0x04, 0x02, [0x00]),
    9:  ("Charging ON",         0x04, 0x01, [0x01]),
    10: ("Charging OFF",        0x04, 0x01, [0x00]),

    11: ("Flap Open",           0x04, 0x03, [0x01]),
    12: ("Flap Close",          0x04, 0x03, [0x00]),
    13: ("Rods Engage",         0x04, 0x04, [0x01]),
    14: ("Rods Disengage",      0x04, 0x04, [0x00]),

    15: ("ESTOP Trigger",       0xFE, 0x70, [0x01]),
    16: ("ESTOP Release",       0xFE, 0x70, [0x00]),

    17: ("DMCU RESET",          0x02, 0x05, [0x00]),
    18: ("UAV RESET",           0x04, 0x05, [0x00]),
    19: ("ICC RESET",           0x03, 0x05, [0x00]),
    20: ("HVAC RESET",          0x05, 0x05, [0x00]),

    21: ("Platform Light ON",   0x03, 0x01, [0x01]),
    22: ("Platform Light OFF",  0x03, 0x01, [0x00]),
    23: ("LED: BOOT",           0x03, 0x02, [0x00]),
    24: ("LED: READY",          0x03, 0x02, [0x01]),
    25: ("LED: CHARGING",       0x03, 0x02, [0x02]),
    26: ("LED: DRONE PWR",      0x03, 0x02, [0x03]),
    27: ("LED: RC PWR",         0x03, 0x02, [0x04]),
    28: ("LED: HVAC PWR",       0x03, 0x02, [0x05]),
    29: ("LED: ENCLOSURE",      0x03, 0x02, [0x06]),
    30: ("LED: POSITIONER",     0x03, 0x02, [0x07]),
    31: ("LED: ESTOP",          0x03, 0x02, [0x08]),
    32: ("LED: ERROR",          0x03, 0x02, [0x09]),
    33: ("LED: MISSION",        0x03, 0x02, [0x0A]),
    34: ("LED: OFF",            0x03, 0x02, [0x0B]),

    35: ("Cooling OFF",         0x05, 0x01, [0x00]),
    36: ("Cooling ON",          0x05, 0x01, [0x01]),
    37: ("Heating OFF",         0x05, 0x01, [0x02]),
    38: ("Heating ON",          0x05, 0x01, [0x03]),
}


# =============================
# CRC16
# =============================
def crc16_ccitt_false(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc


# =============================
# FRAME BUILDER
# =============================
def build_frame(dest, src, seq, typ, cmd, status, payload):

    frame = bytearray([0xA5, 0x5A])

    tag = [dest, src, seq, typ, cmd, status]
    length = len(payload)

    frame.extend(tag)
    frame.append(length)
    frame.extend(payload)

    crc_input = tag + [length] + list(payload)
    crc = crc16_ccitt_false(crc_input)

    frame.append((crc >> 8) & 0xFF)
    frame.append(crc & 0xFF)

    return bytes(frame)


# =============================
# SEND + RECEIVE
# =============================
def send_dptlv(ser, dest, cmd, payload):

    tx = build_frame(dest, SRC_ADDR, SEQ_ID, TYPE_REQ, cmd, STATUS, payload)

    print("\n========== TX FRAME ==========")
    print(" ".join(f"{b:02X}" for b in tx))

    # TX MODE
    lgpio.gpio_write(h, RS485_DE_PIN, 1)
    time.sleep(0.01)

    ser.write(tx)
    ser.flush()

    time.sleep(0.01)

    # RX MODE
    lgpio.gpio_write(h, RS485_DE_PIN, 0)

    print("Waiting for response...")

    header = ser.read(9)
    if len(header) < 9:
        print("Timeout")
        return

    length = header[8]

    payload_rx = ser.read(length)
    if len(payload_rx) < length:
        print("Payload timeout")
        return

    crc_rx_bytes = ser.read(2)
    if len(crc_rx_bytes) < 2:
        print("CRC timeout")
        return

    rx = header + payload_rx + crc_rx_bytes

    print("\n========== RX FRAME ==========")
    print(" ".join(f"{b:02X}" for b in rx))

    rx_list = list(rx)

    crc_input = rx_list[2:9+length]
    crc_calc = crc16_ccitt_false(crc_input)

    crc_rx = (rx_list[-2] << 8) | rx_list[-1]

    print(f"\nCRC RX   : 0x{crc_rx:04X}")
    print(f"CRC CALC : 0x{crc_calc:04X}")

    if crc_rx == crc_calc:
        print("CRC CHECK : PASS")
    else:
        print("CRC CHECK : FAIL")


# =============================
# MENU
# =============================
def print_menu():

    print("\n========= COMMAND MENU =========\n")

    for k in COMMANDS:
        desc = COMMANDS[k][0]
        print(f"{k:02d} - {desc}")

    print("\n00 - Exit")


# =============================
# MAIN
# =============================
def main():

    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"Opened {COM_PORT}")

        while True:

            print_menu()

            try:
                choice = int(input("\nEnter Command ID: "))
            except:
                print("Invalid input")
                continue

            if choice == 0:
                break

            if choice not in COMMANDS:
                print("Invalid command")
                continue

            desc, addr, cmd, payload = COMMANDS[choice]

            print(f"\n>>> {desc}")

            send_dptlv(ser, addr, cmd, payload)

        ser.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        lgpio.gpiochip_close(h)


if __name__ == "__main__":
    main()