import time
import lgpio

# =============================
# CONFIG
# =============================
GPIO_PIN = 25 #27       # Change this to any BCM pin
TOGGLE_DELAY = 1.0  # seconds

# LEDS -> 6, 17, 18, 24, 27

# =============================
# INIT
# =============================
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, GPIO_PIN, 0)


print(f"Toggling GPIO {GPIO_PIN}... (Ctrl+C to stop)")

try:
    state = 0

    # while(1):
    #     lgpio.gpio_write(h, GPIO_PIN, 1)

    
    while True:
        state ^= 1  # toggle 0 <-> 1

        lgpio.gpio_write(h, GPIO_PIN, state)

        print(f"GPIO {GPIO_PIN} -> {'HIGH' if state else 'LOW'}")

        time.sleep(TOGGLE_DELAY)
    
except KeyboardInterrupt:
    print("\nStopped")

finally:
    lgpio.gpio_write(h, GPIO_PIN, 0)  # safe LOW
    lgpio.gpiochip_close(h)