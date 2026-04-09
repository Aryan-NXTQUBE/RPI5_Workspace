"""
GPIO Documentation Link
Input Devices Link -> https://gpiozero.readthedocs.io/en/stable/api_input.html
Output Devices Link -> https://gpiozero.readthedocs.io/en/stable/api_output.html
"""

from gpiozero import *
from time import sleep
from datetime import time
from signal import pause

# gpio zero library uses the Broadcom i.e. BCM Pin Numbering

button = DigitalInputDevice(17, pull_up=True)
state = button.value
print(state)

led = DigitalOutputDevice(19, active_high=True, initial_value=False)
led.on()
print(led.value)
sleep(1.0)
led.off()
sleep(1.0)
print(led.value)

led.blink(on_time=0.5, off_time=0.5, n=2, background=False)

led2 = PWMOutputDevice(13, active_high=True, initial_value=0, frequency=100)
led2.blink(on_time=1, off_time=1, fade_in_time=1, fade_out_time=1, n=2, background=False)

led3 = OutputDevice(6, active_high=True, initial_value=False)
for i in range(4):
    led3.toggle()
    sleep(0.5)

# Internal Device Classes
cpu = CPUTemperature(min_temp=35, max_temp=90)
print(f'Initial temperature: {cpu.temperature}C')

# tod = TimeOfDay(start_time=time(15), end_time=time(16), utc=False)
# tod.when_activated = led.on
# tod.when_deactivated = led.off

google = PingServer('google.com')
print(google)
google.when_activated = led.on
google.when_deactivated = led.off

la = LoadAverage(min_load_average=0, max_load_average=1)
print(la)

disk = DiskUsage()
print(f'Current disk usage: {disk.usage}%')


