import time
 
import board
import digitalio
import usb_hid
import rotaryio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

keyboard = Keyboard(usb_hid.devices)

outPin = board.GP11
inPins = [board.GP6, board.GP7, board.GP8, board.GP9, board.GP10]
encoderButtonPin = board.GP2
encoderPin1 = board.GP3
encoderPin2 = board.GP4

grnd = digitalio.DigitalInOut(outPin)
grnd.direction = digitalio.Direction.OUTPUT
grnd.value = 0

buttons = [digitalio.DigitalInOut(pin) for pin in inPins]
buttons.insert(0, digitalio.DigitalInOut(encoderButtonPin))
for button in buttons:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

encoder = rotaryio.IncrementalEncoder(board.GP3, board.GP4)

cc = ConsumerControl(usb_hid.devices)

# Constants defined for common multimedia keys:
#
# reference:
# https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode

multimedia_keys = [
    ConsumerControlCode.BRIGHTNESS_DECREMENT,
    ConsumerControlCode.BRIGHTNESS_INCREMENT,
    ConsumerControlCode.EJECT,
    ConsumerControlCode.FAST_FORWARD,
    ConsumerControlCode.MUTE,
    ConsumerControlCode.PLAY_PAUSE,
    ConsumerControlCode.RECORD,
    ConsumerControlCode.REWIND,
    ConsumerControlCode.SCAN_NEXT_TRACK,
    ConsumerControlCode.SCAN_PREVIOUS_TRACK,
    ConsumerControlCode.STOP,
    ConsumerControlCode.VOLUME_DECREMENT,
    ConsumerControlCode.VOLUME_INCREMENT,
]

# examples for other key combinations
# [Keycode.CONTROL, Keycode.C],
# [Keycode.CONTROL, Keycode.V],
# [Keycode.SHIFT, Keycode.CONTROL, Keycode.ALT, Keycode.M],
#     [Keycode.COMMAND, Keycode.SHIFT, Keycode.M],

#if you set one of these to control+c NEVER press it while in the console, 
#it will cause a neverending control+c loop because the program will stop before 'releasing' the buttons

keyCombos = [
    [ConsumerControlCode.MUTE],  # wheel
    [ConsumerControlCode.PLAY_PAUSE],
    [ConsumerControlCode.SCAN_NEXT_TRACK],
    [ConsumerControlCode.SCAN_PREVIOUS_TRACK],
    [],
    [Keycode.SHIFT, Keycode.F1],
]

state = [1 for _ in range(6)]
lastState = [i for i in state]
last_position = encoder.position

while True:
    # find current button states
    for i in range(len(buttons)):
        state[i] = buttons[i].value

    # Handle wheel turning
    # encoder code i copied from the internet
    current_position = encoder.position
    position_change = current_position - last_position
    if position_change > 0:
        for _ in range(position_change):
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        print(current_position)
    elif position_change < 0:
        for _ in range(-position_change):
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        print(current_position)
    last_position = current_position

    # button logic
    for i in range(len(buttons)):
        if state[i] != lastState[i]:
            # when button is push
            if not state[i]:  # logic is reversed bc reasons
                print("Button %d pressed" % i)
                for i in keyCombos[i]:
                    if i in multimedia_keys:
                        cc.send(i)
                    else:
                        keyboard.press(i)
                time.sleep(0.005)
            # when button is not push
            else:
                print("Button %d released" % i)
                for i in keyCombos[i]:
                    keyboard.release(i)

    lastState = [i for i in state]
    time.sleep(0.005)
