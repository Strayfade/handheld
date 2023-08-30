### ***IMPORTANT***
This project is very much a **work-in-progress**! Things could change, parts could be added or removed, and documentation could change in the future! This is by **no means** a finished product.

When this project is finished, better assembly instructions will be made. Right now, this project is incomplete and should only be used as reference material.

### Caveats/Considerations
 - Add `dtoverlay=spi0-1cs,cs0_pin=8` to `/boot/config.txt` to disable the GPIO 7 Chip Select pin on the `spi0` interface.
   - This pin is disallowed from being reserved by the OS because it's necessary for reading the Left D-Pad button.
   - See https://github.com/raspberrypi/firmware/blob/master/boot/overlays/README#L3873
   - See https://raspberrypi.stackexchange.com/a/144210/156599
 - Add `display_rotate=2` and `lcd_rotate=2` to `/boot/config.txt` to rotate the display and touchscreen 180 degrees.
   - The `--screenrotate 2` argument may also be required in EmulationStations autostart config, depending on how it was installed (this is usually not required).
 - Add `avoid_warnings=1` to `/boot/config.txt` to remove the Pi's undervoltage symbol from the UI (not recommended, but necessary).

### Parts List
Required:
 - **Raspberry Pi 3 B+** (with microSD card)
 - **[Raspberry Pi Heatsink](https://www.digikey.com/en/products/detail/adafruit-industries-llc/3082/6047742)** (highly recommended)
 - **Custom PCB** ([Download design files](https://github.com/Strayfade/handheld/tree/main/pcb))
 - **[Bill of Materials (BOM)](https://github.com/Strayfade/handheld/blob/main/pcb/Handheld%20BOM.csv)**

### Links
 - **[PCB Archive](https://github.com/Strayfade/handheld/tree/main/pcb)**
 - **[Built-in Controller "Firmware"](https://github.com/Strayfade/Handheld/blob/main/firmware/Main.py)** (Python)
