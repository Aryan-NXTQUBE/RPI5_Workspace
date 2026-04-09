#!/usr/bin/env python3

import serial
import time

UARTS = [
    ("/dev/ttyAMA0", "UART0"),
    ("/dev/ttyAMA1", "UART1"),
    ("/dev/ttyAMA2", "UART2"),
    ("/dev/ttyAMA3", "UART3"),
]

BAUDRATE = 115200
DELAY_BETWEEN_UARTS = 1   # delay between each UART transmission
DELAY_BETWEEN_CYCLES = 5  # delay after full cycle


def open_uarts():
    serial_ports = []
    for dev, name in UARTS:
        try:
            ser = serial.Serial(dev, baudrate=BAUDRATE, timeout=1)
            serial_ports.append((ser, name))
            print(f"✅ Opened {name} ({dev})")
        except Exception as e:
            print(f"❌ Failed to open {name} ({dev}): {e}")
    return serial_ports


def main():
    print("==== UART SEQUENTIAL TX TEST ====")
    print("Sequence: UART0 → UART1 → UART2 → UART3\n")

    ports = open_uarts()

    counter = 0

    try:
        while True:
            for ser, name in ports:
                msg = f"{name} TX TEST {counter}\n"
                ser.write(msg.encode())

                print(f"➡️  Sent on {name}: {msg.strip()}")

                time.sleep(DELAY_BETWEEN_UARTS)

            counter += 1
            print("---- Cycle Complete ----\n")
            time.sleep(DELAY_BETWEEN_CYCLES)

    except KeyboardInterrupt:
        print("\n🛑 Stopping test...")

    finally:
        for ser, name in ports:
            ser.close()
        print("🔌 All UARTs closed")


if __name__ == "__main__":
    main()
