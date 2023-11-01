# How to put MicroPython onto the 2.4inch_ESP32-2432S024 board and get the LCD screen working.

Follow these instructions:-

## Prerequisites

* python:
  might be best not to use the store version (puts files in weird places): use: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
* ampy
`  pip install adafruit-ampy`

* esptool
`  pip install esptool`


## Flashing micropython to your board

1. Connect a serial adapter to your board, and note which COM port number it shows up as
2. press and hold the boot (lower) button, while pressing and releasing the RST button - this puts your ESP32 into program-upload mode
3. make sure you do not have any serial terminal window open - you're about to use the COM port, which only 1 thing can connect to at once:
4. run this (substitute your COM prot number instead of using mine, which is 21, below)::
* windows
`esptool --chip esp32 --port COM21 --baud 115200 write_flash -z 0x1000 ESP32_GENERIC-OTA-20231005-v1.21.0.bin `
* linux/wsl
`esptool --chip esp32 --port /dev/ttyS21 --baud 115200 write_flash -z 0x1000 ESP32_GENERIC-OTA-20231005-v1.21.0.bin ` 
6. after the upload, push the reset button again.  You can now use the micropython REPL over serial port - keep going if you want to put some useful tools on there too:
7. test that ampy is working: (use COM instead of /dev/ttyS for windows)
`ampy --port /dev/ttyS21 ls`
9. edit bin/ifup.py and boot.py and put your WiFi SSID and password in
10. upload all the required files by running all the commands inside runme.sh (either manually, or if you're using WSL or linux, fix the COM port number in there and run the program)
11. reboot one last time
12. you can now connect to your ESP32 using your web browser - e.g. http://192.168.1.123/

## To use the included POSIX shell

connect over serial and type
`import sh`

you can now run things like `ls` and `cat` and `rm` etc - type `help` for the full list

to run a python program, type `run programname.py`

## To test the LCD Display

Start the POSIX shell (see above) then:


    cd lcd
    run main.py


### Working example:-

![working example](https://raw.githubusercontent.com/NoosaHydro/2.4inch_ESP32-2432S024/main/cnd-micropython/demo_image.jpg)
