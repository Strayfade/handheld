import time
import uinput
import math
from evdev import UInput, AbsInfo, ecodes as e



# This file tests the virtual gamepad created
# to run on emulators.
# I recommend going to a gamepad testing website
# such as https://hardwaretester.com/gamepad and 
# running this test script. If everything works,
# all of the values shown should either be on
# (1.00) or changing, EXCEPT for B2, B5, B8,
# B9, and B12. These could possibly be reserved
# values.

if __name__ == "__main__":

	# These values were dumped from the Xbox One S 
	# wireless controller
	Capabilities = {
		e.EV_SYN: [],
		e.EV_KEY: [
			e.KEY_BACK,
			e.KEY_HOMEPAGE,
			e.BTN_SOUTH,
			e.BTN_EAST,
			e.BTN_C,
			e.BTN_NORTH,
			e.BTN_WEST,
			e.BTN_Z,
			e.BTN_TL,
			e.BTN_TR,
			e.BTN_TL2,
			e.BTN_TR2,
			e.BTN_SELECT,
			e.BTN_START,
			e.BTN_MODE,
			e.BTN_THUMBL,
			e.BTN_THUMBR
		],
		e.EV_ABS: [
			(e.ABS_X, AbsInfo(min=0, max=65535, value=36768, fuzz=255, flat=4095, resolution=0)),      # Left joystick (X-axis)
			(e.ABS_Y, AbsInfo(min=0, max=65535, value=36768, fuzz=255, flat=4095, resolution=0)),      # Left joystick (Y-axis)
			(e.ABS_Z, AbsInfo(min=0, max=65535, value=36768, fuzz=255, flat=4095, resolution=0)),      # Right joystick (X-axis)
			(e.ABS_RZ, AbsInfo(min=0, max=65535, value=36768, fuzz=255, flat=4095, resolution=0)),     # Right joystick (Y-axis)
			(e.ABS_GAS, AbsInfo(min=0, max=1023, value=512, fuzz=3, flat=63, resolution=0)),  # Left trigger
			(e.ABS_BRAKE, AbsInfo(min=0, max=1023, value=512, fuzz=3, flat=63, resolution=0)),    # Right trigger
			(e.ABS_HAT0X, AbsInfo(min=-1, max=1, value=0, fuzz=0, flat=0, resolution=0)),   # D-pad (X-axis)
			(e.ABS_HAT0Y, AbsInfo(min=-1, max=1, value=0, fuzz=0, flat=0, resolution=0))   # D-pad (Y-axis)
		]
	}

	# Create device
	device = uinput.Device([uinput.KEY_E])
	ui = UInput(events=Capabilities, name="Built-in Gamepad", vendor=0x045e, product=0x02fd, version=0x903, bustype=0x5)

	while True:
		RunningTime = time.time()
		c1 = (math.sin(RunningTime) + 1) / 2
		c2 = (math.cos(RunningTime) + 1) / 2
		
		# Face buttons
		ui.write(e.EV_KEY, e.BTN_A, 1)
		ui.write(e.EV_KEY, e.BTN_B, 1)
		ui.write(e.EV_KEY, e.BTN_X, 1)
		ui.write(e.EV_KEY, e.BTN_Y, 1)

		# Bumpers
		ui.write(e.EV_KEY, e.BTN_TL, 1)
		ui.write(e.EV_KEY, e.BTN_TR, 1)

		# Joystick Buttons
		ui.write(e.EV_KEY, e.BTN_THUMBL, 1)
		ui.write(e.EV_KEY, e.BTN_THUMBR, 1)

		# Start/Select/Home Buttons
		ui.write(e.EV_KEY, e.BTN_START, 1)
		ui.write(e.EV_KEY, e.BTN_SELECT, 1)
		ui.write(e.EV_KEY, e.KEY_HOMEPAGE, 1)

		# Joysticks
		ui.write(e.EV_ABS, e.ABS_X, int(c1 * 65535))
		ui.write(e.EV_ABS, e.ABS_Y, int(c2 * 65535))
		ui.write(e.EV_ABS, e.ABS_Z, int(c1 * 65535))
		ui.write(e.EV_ABS, e.ABS_RZ, int(c2 * 65535))

		# Analog Triggers
		ui.write(e.EV_ABS, e.ABS_GAS, int(c1 * 1023))
		ui.write(e.EV_ABS, e.ABS_BRAKE, int(c2 * 1023))

		# Directional pad
		ui.write(e.EV_ABS, e.ABS_HAT0X, int(c1 * 4 - 2))
		ui.write(e.EV_ABS, e.ABS_HAT0Y, int(c2 * 4 - 2))

		# Sync gamepad state
		ui.syn()