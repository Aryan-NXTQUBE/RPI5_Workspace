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
READ_TIMEOUT = 1
DELAY_AFTER_TX = 0.2
DELAY_BETWEEN_UARTS = 1
DELAY_BETWEEN_CYCLES = 5.0


def open_uarts():
    serial_ports = []
    for dev, name in UARTS:
        try:
            ser = serial.Serial(dev, baudrate=BAUDRATE, timeout=READ_TIMEOUT)
            serial_ports.append((ser, name))
            print(f"✅ Opened {name} ({dev})")
        except Exception as e:
            print(f"❌ Failed to open {name} ({dev}): {e}")
    return serial_ports


def test_uart(ser, name, counter):
    msg = f"{name} TXRX TEST {counter}\n"
    tx_data = msg.encode()

    # Flush buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Transmit
    ser.write(tx_data)
    print(f"➡️  Sent on {name}: {msg.strip()}")

    # Wait for data to come back
    time.sleep(DELAY_AFTER_TX)

    # Read response
    rx_data = ser.read(len(tx_data))

    if rx_data == tx_data:
        print(f"✅ {name} LOOPBACK PASS")
    else:
        print(f"❌ {name} LOOPBACK FAIL")
        print(f"   Expected: {tx_data}")
        print(f"   Received: {rx_data}")


def main():
    print("==== UART SEQUENTIAL TX + RX TEST ====")
    print("⚠️  Ensure TX and RX are shorted for each UART\n")

    ports = open_uarts()
    counter = 0

    try:
        while True:
            for ser, name in ports:
                test_uart(ser, name, counter)
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
