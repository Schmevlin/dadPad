import storage
import board, digitalio

import random
print(f"boot.py loading: {random.randrange(1,100)}")

# If not pressed, the key will be at +V (due to the pull-up).
# https://learn.adafruit.com/customizing-usb-devices-in-circuitpython/circuitpy-midi-serial#circuitpy-mass-storage-device-3096583-4
button = digitalio.DigitalInOut(board.GP2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

print(f"checking button. Its value is {button.value}")

# Disable devices only if button is not pressed.
if button.value:
    print(f"boot: rotary button not pressed, disabling drive")
    storage.disable_usb_drive()
    
