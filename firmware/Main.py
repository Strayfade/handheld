import uinput
from gpiozero import Button, MCP3008
from evdev import UInput, AbsInfo, ecodes as e
import alsaaudio

# Firmware v3.0

# This script is responsible for reading the values from
# components wired to the GPIO headers on the Raspberry Pi.
# Then, a virtual gamepad is created to relay those inputs
# to the host system.

# Several things to note:
# - SPI communication is required on the system. The SPI bus
#   is required to use the MCP3008-I/P circuit with a Raspberry
#   Pi. SPI communication can be enabled through raspi-config.
# - Some commands are required (on SOME systems) to enable
#   writing to /dev/uinput. Run the following command as root:
#   "sudo modprobe uinput && sudo chmod a+r+w /dev/uinput"
# - The following packages are required:
#   sudo python3 -m pip install evdev gpiozero python-uinput pyalsaaudio

# CONFIGURATION 1. Button GPIO pins
# Note that these pins are labeled by their GPIO pin number, not
# their *actual* pin number.
pButtonA = 16
pButtonB = 18
pButtonX = 15
pButtonY = 14
pButtonUp = 0
pButtonDown = 24
pButtonLeft = 7
pButtonRight = 25
pButtonLeftBumper = 5
pButtonRightBumper = 23
pButtonLeftTrigger = 4
pButtonRightTrigger = 17
pButtonLeftJoystick = 2
pButtonRightJoystick = 3
pButtonSelect = 22
pButtonStart = 13
pButtonHomeLeft = 27
pButtonHomeRight = 6
pButtonVolumeUp = 1
pButtonVolumeDown = 12

# CONFIGURATION 2. MCP3008-I/P channels
# The MCP3008-I/P is an 8-channel analog-to-digital
# converter (ADC).
chLeftJoystickX = 0
chLeftJoystickY = 1
chRightJoystickX = 2
chRightJoystickY = 3

# CONFIGURATION 3. Miscellaneous
flVolumeStepSizePercent = 10 # Percent to adjust volume up/down with each buttonpress

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
    ButtonLeftBumper = Button(pButtonLeftBumper)
    ButtonRightBumper = Button(pButtonRightBumper)
    ButtonLeftTrigger = Button(pButtonLeftTrigger)
    ButtonRightTrigger = Button(pButtonRightTrigger)
    ButtonLeftJoystick = Button(pButtonLeftJoystick)
    ButtonRightJoystick = Button(pButtonRightJoystick)
    ButtonSelect = Button(pButtonSelect)
    ButtonStart = Button(pButtonStart)
    ButtonHomeLeft = Button(pButtonHomeLeft)
    ButtonHomeRight = Button(pButtonHomeRight)
    LeftJoystickX = MCP3008(chLeftJoystickX)
    LeftJoystickY = MCP3008(chLeftJoystickY)
    RightJoystickX = MCP3008(chRightJoystickX)
    RightJoystickY = MCP3008(chRightJoystickY)
    ButtonVolumeUp = Button(pButtonVolumeUp)
    ButtonVolumeDown = Button(pButtonVolumeDown)

GlobalReader = GamepadReader()

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
    sButtonLeftBumper = False
    sButtonRightBumper = False
    sButtonLeftTrigger = False
    sButtonRightTrigger = False
    sButtonLeftJoystick = False
    sButtonRightJoystick = False
    sButtonSelect = False
    sButtonStart = False
    sButtonHomeLeft = False
    sButtonHomeRight = False
    sLeftJoystickX = 0
    sLeftJoystickY = 0
    sRightJoystickX = 0
    sRightJoystickY = 0
    sButtonVolumeUp = False
    sButtonVolumeDown = False

    def __init__(self):
        self.sButtonA = GlobalReader.ButtonA.is_pressed
        self.sButtonB = GlobalReader.ButtonB.is_pressed
        self.sButtonX = GlobalReader.ButtonX.is_pressed
        self.sButtonY = GlobalReader.ButtonY.is_pressed
        self.sButtonUp = GlobalReader.ButtonUp.is_pressed
        self.sButtonDown = GlobalReader.ButtonDown.is_pressed
        self.sButtonLeft = GlobalReader.ButtonLeft.is_pressed
        self.sButtonRight = GlobalReader.ButtonRight.is_pressed
        self.sButtonLeftBumper = GlobalReader.ButtonLeftBumper.is_pressed
        self.sButtonRightBumper = GlobalReader.ButtonRightBumper.is_pressed
        self.sButtonLeftTrigger = GlobalReader.ButtonLeftTrigger.is_pressed
        self.sButtonRightTrigger = GlobalReader.ButtonRightTrigger.is_pressed
        self.sButtonLeftJoystick = GlobalReader.ButtonLeftJoystick.is_pressed
        self.sButtonRightJoystick = GlobalReader.ButtonRightJoystick.is_pressed
        self.sButtonSelect = GlobalReader.ButtonSelect.is_pressed
        self.sButtonStart = GlobalReader.ButtonStart.is_pressed
        self.sButtonHomeLeft = GlobalReader.ButtonHomeLeft.is_pressed
        self.sButtonHomeRight = GlobalReader.ButtonHomeRight.is_pressed
        self.sLeftJoystickX = GlobalReader.LeftJoystickX.value
        self.sLeftJoystickY = GlobalReader.LeftJoystickY.value
        self.sRightJoystickX = GlobalReader.RightJoystickX.value
        self.sRightJoystickY = GlobalReader.RightJoystickY.value
        self.sButtonVolumeUp = GlobalReader.ButtonVolumeUp.is_pressed
        self.sButtonVolumeDown = GlobalReader.ButtonVolumeDown.is_pressed

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
                (e.ABS_X, AbsInfo(min=0, max=65535, value=36768, fuzz=255,
                 flat=4095, resolution=0)),      # Left joystick (X-axis)
                (e.ABS_Y, AbsInfo(min=0, max=65535, value=36768, fuzz=255,
                 flat=4095, resolution=0)),      # Left joystick (Y-axis)
                (e.ABS_Z, AbsInfo(min=0, max=65535, value=36768, fuzz=255,
                 flat=4095, resolution=0)),      # Right joystick (X-axis)
                (e.ABS_RZ, AbsInfo(min=0, max=65535, value=36768, fuzz=255,
                 flat=4095, resolution=0)),     # Right joystick (Y-axis)
                (e.ABS_GAS, AbsInfo(min=0, max=1023, value=512,
                 fuzz=3, flat=63, resolution=0)),  # Left trigger
                (e.ABS_BRAKE, AbsInfo(min=0, max=1023, value=512,
                 fuzz=3, flat=63, resolution=0)),    # Right trigger
                (e.ABS_HAT0X, AbsInfo(min=-1, max=1, value=0,
                 fuzz=0, flat=0, resolution=0)),   # D-pad (X-axis)
                (e.ABS_HAT0Y, AbsInfo(min=-1, max=1, value=0,
                 fuzz=0, flat=0, resolution=0))   # D-pad (Y-axis)
            ]
        }
        DeviceCapabilities = [uinput.KEY_BACK, uinput.KEY_HOMEPAGE, uinput.BTN_SOUTH, uinput.BTN_EAST, uinput.BTN_C,
                              uinput.BTN_NORTH, uinput.BTN_WEST, uinput.BTN_Z, uinput.BTN_TL, uinput.BTN_TR, uinput.BTN_TL2, uinput.BTN_TR2]
        DeviceCapabilities2 = [uinput.BTN_SELECT, uinput.BTN_START, uinput.BTN_MODE, uinput.BTN_THUMBL, uinput.BTN_THUMBR,
                               uinput.ABS_X, uinput.ABS_Y, uinput.ABS_Z, uinput.ABS_RZ, uinput.ABS_GAS, uinput.ABS_BRAKE, uinput.ABS_HAT0X, uinput.ABS_HAT0Y]
        DeviceCapabilities = DeviceCapabilities + DeviceCapabilities2

        # Values dumped from Xbox One S controller
        VendorInfo = 0x45e
        ProductInfo = 0x02fd
        VersionInfo = 0x903
        BusTypeInfo = 0x5
        # self.device = uinput.Device(DeviceCapabilities)
        self.ui = UInput(events=Capabilities, name=deviceName, vendor=VendorInfo,
                         product=ProductInfo, version=VersionInfo, bustype=BusTypeInfo)

    def DigitalWrite(self, Event, Value):
        self.ui.write(e.EV_KEY, Event, int(Value))

    def AnalogWrite(self, Event, Value, Multiplier=65535):
        self.ui.write(e.EV_ABS, Event, int(Value * Multiplier))


if __name__ == "__main__":
    # Create a virtual (emulated) gamepad with the name "Built-in Gamepad"
    Gamepad = VirtualGamepad("Built-in Gamepad")

    # Create a mixer control
    Mixer = alsaaudio.Mixer()

    # Create gamepad state for updating
    PreviousState = GamepadState()
    FirstRun = True
    while True:
        try:
            # Get the current gamepad state
            NewState = GamepadState()

            # Refresh Buttons
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
            if ((NewState.sButtonHomeLeft != PreviousState.sButtonHomeLeft) or (NewState.sButtonHomeRight != PreviousState.sButtonHomeRight)) or FirstRun:
                Gamepad.DigitalWrite(e.KEY_HOMEPAGE, NewState.sButtonHomeLeft or NewState.sButtonHomeRight)

            # Refresh Joysticks
            if (NewState.sLeftJoystickX != PreviousState.sLeftJoystickX) or FirstRun:
                Gamepad.AnalogWrite(e.ABS_X, NewState.sLeftJoystickX)
            if (NewState.sLeftJoystickY != PreviousState.sLeftJoystickY) or FirstRun:
                Gamepad.AnalogWrite(e.ABS_Y, NewState.sLeftJoystickY)
            if (NewState.sRightJoystickX != PreviousState.sRightJoystickX) or FirstRun:
                Gamepad.AnalogWrite(e.ABS_Z, NewState.sRightJoystickX)
            if (NewState.sRightJoystickY != PreviousState.sRightJoystickY) or FirstRun:
                Gamepad.AnalogWrite(e.ABS_RZ, NewState.sRightJoystickY)

            # Refresh bumpers and triggers
            if (NewState.sButtonLeftTrigger != PreviousState.sButtonLeftTrigger) or FirstRun:
                Gamepad.AnalogWrite(e.ABS_BRAKE, NewState.sButtonLeftTrigger, 1023)
            if (NewState.sButtonRightTrigger != PreviousState.sButtonRightTrigger) or FirstRun:
                Gamepad.AnalogWrite(e.ABS_GAS, NewState.sButtonRightTrigger, 1023)
            if (NewState.sButtonLeftBumper != PreviousState.sButtonLeftBumper) or FirstRun:
                Gamepad.DigitalWrite(e.BTN_TL, NewState.sButtonLeftBumper)
            if (NewState.sButtonRightBumper != PreviousState.sButtonRightBumper) or FirstRun:
                Gamepad.DigitalWrite(e.BTN_TL, NewState.sButtonRightBumper)

            # Refresh directional pad
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

            # Refresh volume controls
            if ((NewState.sButtonVolumeUp != PreviousState.sButtonVolumeUp) and NewState.sButtonVolumeUp):
                AlsaCurrentVolume = Mixer.getvolume()[0]
                AlsaNewVolume = min(100, AlsaCurrentVolume + flVolumeStepSizePercent)
                Mixer.setvolume(AlsaNewVolume)
            if ((NewState.sButtonVolumeDown != PreviousState.sButtonVolumeDown) and NewState.sButtonVolumeDown):
                AlsaCurrentVolume = Mixer.getvolume()[0]
                AlsaNewVolume = max(0, AlsaCurrentVolume - flVolumeStepSizePercent)
                Mixer.setvolume(AlsaNewVolume)

            # Resync
            Gamepad.ui.syn()

            # Cleanup
            PreviousState = NewState
            if FirstRun:
                print(" ")
                print(" ")
                print(" ")
                print("Initialized controller firmware!")
                print("Active version: 3.0")
                print(" ")
                print(" ")
                print(" ")
                print(" ")
            FirstRun = False

        except KeyboardInterrupt:
            exit()

        except Exception as e:
            # Catch errors
            print("Error: ", end="")
            print(e)
            pass
