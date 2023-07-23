import uinput
from gpiozero import Button, MCP3008
from evdev import UInput, AbsInfo, ecodes as e



# This script is responsible for reading the values from
# components wired to the GPIO headers on the Raspberry Pi.
# Then, a virtual gamepad is created to relay those inputs
# to the host system.

# Several things to note:
# - SPI communication is required on the system. The SPI bus
#   is required to use the MCP3008-I/P circuit with a Raspberry 
#   Pi. SPI communication can be enabled through raspi-config.



### BEGIN CONFIG ###

# 1. GPIO per-pin configuration
pButtonA = 5
pButtonB = 13
pButtonX = 19
pButtonY = 26
pButtonUp = 4
pButtonDown = 14
pButtonLeft = 27
pButtonRight = 22
pButtonLeftJoystick = 2
pButtonRightJoystick = 3
pButtonSelect = 23
pButtonStart = 24
pButtonHome = 6
# NOTES
# pButtonSelect is the same as MenuA on the PCB
# pButtonStart is the same as MenuB on the PCB

# 2. MCP3008-I/P channel configuration
chLeftJoystickX = 0
chLeftJoystickY = 1
chRightJoystickX = 2
chRightJoystickY = 3
chLeftBumper = 4
chRightBumper = 5
chLeftTrigger = 6
chRightTrigger = 7
# NOTES
# On this project, triggers AND bumpers are
# analog potentiometers. This was done for customizability
# (triggers and bumpers can be swapped) and for comfort.

# 3. User Options
flBumperThreshold = 0.1
# Defines how far the bumpers need to be pushed before
# reading as "pressed" (when the bumpers are not acting as
# triggers)
flTriggerThreshold = 0.1
# Defines how far the triggers need to be pushed before
# reading as "pressed" (when the triggers are acting as
# bumpers)
bSwapBumpersAndTriggers = False
# Makes the bumpers into triggers and the triggers into 
# bumpers

### END CONFIG ###



# Class responsible for holding the "reader" objects
# used to read values from the hardware components.
class GamepadReader:
	ButtonA = Button(pButtonA)
	ButtonB = Button(pButtonB)
	ButtonX = Button(pButtonX)
	ButtonY = Button(pButtonY)
	ButtonUp = Button(pButtonUp)
	ButtonDown = Button(pButtonDown)
	ButtonLeft = Button(pButtonLeft)
	ButtonRight = Button(pButtonRight)
	ButtonLeftJoystick = Button(pButtonLeftJoystick)
	ButtonRightJoystick = Button(pButtonRightJoystick)
	ButtonSelect = Button(pButtonSelect)
	ButtonStart = Button(pButtonStart)
	ButtonHome = Button(pButtonHome)
	LeftJoystickX = MCP3008(chLeftJoystickX)
	LeftJoystickY = MCP3008(chLeftJoystickY)
	RightJoystickX = MCP3008(chRightJoystickX)
	RightJoystickY = MCP3008(chRightJoystickY)
	LeftBumper = MCP3008(chLeftBumper)
	RightBumper = MCP3008(chRightBumper)
	LeftTrigger = MCP3008(chLeftTrigger)
	RightTrigger = MCP3008(chRightTrigger)
Reader = GamepadReader()
# Class responsible for holding values to determine 
# if the virtual gamepad needs refreshed
class GamepadState:
	sButtonA = 5
	sButtonB = False
	sButtonX = False
	sButtonY = False
	sButtonUp = False
	sButtonDown = False
	sButtonLeft = False
	sButtonRight = False
	sButtonLeftJoystick = False
	sButtonRightJoystick = False
	sButtonSelect = False
	sButtonStart = False
	sButtonHome = False
	sLeftJoystickX = 0
	sLeftJoystickY = 0
	sRightJoystickX = 0
	sRightJoystickY = 0
	sLeftBumper = 0
	sRightBumper = 0
	sLeftTrigger = 0
	sRightTrigger = 0

	def __init__(self):
		self.sButtonA = Reader.ButtonA.is_pressed
		self.sButtonB = Reader.ButtonB.is_pressed
		self.sButtonX = Reader.ButtonX.is_pressed
		self.sButtonY = Reader.ButtonY.is_pressed
		self.sButtonUp = Reader.ButtonUp.is_pressed
		self.sButtonDown = Reader.ButtonDown.is_pressed
		self.sButtonLeft = Reader.ButtonLeft.is_pressed
		self.sButtonRight = Reader.ButtonRight.is_pressed
		self.sButtonLeftJoystick = Reader.ButtonLeftJoystick.is_pressed
		self.sButtonRightJoystick = Reader.ButtonRightJoystick.is_pressed
		self.sButtonSelect = Reader.ButtonSelect.is_pressed
		self.sButtonStart = Reader.ButtonStart.is_pressed
		self.sButtonHome = Reader.ButtonHome.is_pressed
		self.sLeftJoystickX = Reader.LeftJoystickX.value
		self.sLeftJoystickY = Reader.LeftJoystickY.value
		self.sRightJoystickX = Reader.RightJoystickX.value
		self.sRightJoystickY = Reader.RightJoystickY.value
		self.sLeftBumper = Reader.LeftBumper.value
		self.sRightBumper = Reader.RightBumper.value
		self.sLeftTrigger = Reader.LeftTrigger.value
		self.sRightTrigger = Reader.RightTrigger.value

# Class responsible for emulating a game controller
class VirtualGamepad:
	def __init__(self, deviceName):
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
		# Values dumped from Xbox One S controller
		VendorInfo = 0x45e
		ProductInfo = 0x02fd
		VersionInfo = 0x903
		BusTypeInfo = 0x5
		self.device = uinput.Device([uinput.KEY_E])
		self.ui = UInput(events=Capabilities, name=deviceName, vendor=VendorInfo, product=ProductInfo, version=VersionInfo, bustype=BusTypeInfo)

	def DigitalWrite(self, Event, Value):
		self.ui.write(e.EV_KEY, Event, int(Value))
		self.ui.syn()
	
	def AnalogWrite(self, Event, Value, Multiplier = 65535):
		self.ui.write(e.EV_ABS, Event, int(Value * Multiplier))
		self.ui.syn()

if __name__ == "__main__":
	# Create a virtual (emulated) gamepad
	Gamepad = VirtualGamepad("Built-in Gamepad")

	# Create state
	PreviousState = GamepadState()
	FirstRun = True
	while True:
		try:
			NewState = GamepadState()

			# Check Buttons
			if (NewState.sButtonA != PreviousState.sButtonA) or FirstRun:
				Gamepad.DigitalWrite(e.BTN_A, NewState.sButtonA)
			if (NewState.sButtonB != PreviousState.sButtonB) or FirstRun:
				Gamepad.DigitalWrite(e.BTN_B, NewState.sButtonB)
			if (NewState.sButtonX != PreviousState.sButtonX) or FirstRun:
				Gamepad.DigitalWrite(e.BTN_X, NewState.sButtonX)
			if (NewState.sButtonY != PreviousState.sButtonY) or FirstRun:
				Gamepad.DigitalWrite(e.BTN_Y, NewState.sButtonY)
			if (NewState.sButtonLeftJoystick != PreviousState.sButtonLeftJoystick) or FirstRun:
				Gamepad.DigitalWrite(e.BTN_THUMBL, NewState.sButtonLeftJoystick)
			if (NewState.sButtonRightJoystick != PreviousState.sButtonRightJoystick) or FirstRun:
				Gamepad.DigitalWrite(e.BTN_THUMBR, NewState.sButtonRightJoystick)
			if (NewState.sButtonSelect != PreviousState.sButtonSelect) or FirstRun:
				Gamepad.DigitalWrite(e.BTN_SELECT, NewState.sButtonSelect)
			if (NewState.sButtonStart != PreviousState.sButtonStart) or FirstRun:
				Gamepad.DigitalWrite(e.BTN_START, NewState.sButtonStart)
			if (NewState.sButtonHome != PreviousState.sButtonHome) or FirstRun:
				Gamepad.DigitalWrite(e.KEY_HOMEPAGE, NewState.sButtonHome)

			# Check Joysticks
			if (NewState.sLeftJoystickX != PreviousState.sLeftJoystickX) or FirstRun:
				Gamepad.AnalogWrite(e.ABS_X, NewState.sLeftJoystickX)
			if (NewState.sLeftJoystickY != PreviousState.sLeftJoystickY) or FirstRun:
				Gamepad.AnalogWrite(e.ABS_Y, NewState.sLeftJoystickY)
			if (NewState.sRightJoystickX != PreviousState.sRightJoystickX) or FirstRun:
				Gamepad.AnalogWrite(e.ABS_Z, NewState.sRightJoystickX)
			if (NewState.sRightJoystickY != PreviousState.sRightJoystickY) or FirstRun:
				Gamepad.AnalogWrite(e.ABS_RZ, NewState.sRightJoystickY)

			# Check Bumpers and Triggers
			if bSwapBumpersAndTriggers:
				# Bumpers
				if (NewState.sLeftBumper != PreviousState.sLeftBumper) or FirstRun:
					Gamepad.AnalogWrite(e.ABS_BRAKE, NewState.sLeftBumper, 1023)
				if (NewState.sRightBumper != PreviousState.sRightBumper) or FirstRun:
					Gamepad.AnalogWrite(e.ABS_GAS, NewState.sRightBumper, 1023)

				# Triggers
				if (NewState.sLeftTrigger != PreviousState.sLeftTrigger) or FirstRun:
					Gamepad.DigitalWrite(e.BTN_TL, NewState.sLeftTrigger > flTriggerThreshold)
				if (NewState.sRightTrigger != PreviousState.sRightTrigger) or FirstRun:
					Gamepad.DigitalWrite(e.BTN_TR, NewState.sRightTrigger > flTriggerThreshold)
			else:
				# Bumpers
				if (NewState.sLeftBumper != PreviousState.sLeftBumper) or FirstRun:
					Gamepad.DigitalWrite(e.BTN_TL, NewState.sLeftBumper > flBumperThreshold)
				if (NewState.sRightBumper != PreviousState.sRightBumper) or FirstRun:
					Gamepad.DigitalWrite(e.BTN_TR, NewState.sRightBumper > flBumperThreshold)

				# Triggers
				if (NewState.sLeftTrigger != PreviousState.sLeftTrigger) or FirstRun:
					Gamepad.AnalogWrite(e.ABS_BRAKE, NewState.sLeftTrigger, 1023)
				if (NewState.sRightTrigger != PreviousState.sRightTrigger) or FirstRun:
					Gamepad.AnalogWrite(e.ABS_GAS, NewState.sRightTrigger, 1023)

			# Check Directional Pad
			dX = 0
			dY = 0
			if NewState.sButtonUp:
				dY -= 1
			if NewState.sButtonDown:
				dY += 1
			if NewState.sButtonLeft:
				dX -= 1
			if NewState.sButtonRight:
				dX += 1
			Gamepad.AnalogWrite(e.ABS_HAT0X, dX, 1)
			Gamepad.AnalogWrite(e.ABS_HAT0Y, dY, 1)

			# Cleanup
			PreviousState = NewState
			FirstRun = False

		except KeyboardInterrupt:
			exit()

		except Exception as e:
			# Catch errors
			print("Error: ", end="")
			print(e)
			pass
