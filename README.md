# ESP32-winmonitor
Uses a python app to grab frames of a windows monitor an streams them over wifi to an ESP32 with an 320x170 LCD Screen connected over SPI

Fairwarning this is vibecoded garbage but that is ok because it works! Feel free to optimise this theres probably lots of room to make it faster (Some suggestions below, but more knowledgeable people will have better ideas).
If you haven't read everything here **(especially things in BOLD)**, then don't complain when it doesnt work!

**ONLY TESTED WITH/COMPATABLE WITH WINDOWS.**

(Optional) But **RECCOMENDED to use VDD** (Virtual Display Driver: https://github.com/VirtualDrivers/Virtual-Display-Driver), Instead of just streaming your main full sized monitor.

Able to achieve around 5-6 fps when using full RGB565 colours, alternatively can reach higher framerates using either greyscale, or purely B&W colour. Using different colour specs requires completely different Arduino sketches to be uploaded to the ESP32.
Acceptable framerate for some basic GIFs, or more appropriately, for rainmeter widgets, etc. Not really for a "functional monitor" for watching youtube videos, etc.

## Achievable Framerates
In my experience with an ESP32 C3 XIAO, your results may vary: (Similar for S3 Single Core/Same Code)*
- Monochrome = 19.5 fps
- 8 Bit greyscale = 9.6 fps
- RGB 332 = 7.9 fps
- RGB 565 = 6.45 fps

(RGB 332 looks pretty crap, hence not worth including in the codebase due to marginal FPS gains over RGB565 which looks much better)

*These framerates can likely be increased by making use of the ESP32 S3 Supermini's additional core, which would allow parallelising recieving and displaying of frames. Alternatively also might be able to make use of usb CDC to remove the reliance on WiFi streaming, but I haven't looked into this.

# How To Use
## Hardware Requirements
- EITHER [Seeed Studio XIAO ESP32C3 Microcontroller](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/) (other ESP32 & Wifi enabled MCUs Probably work too!)
- OR [ESP32 S3 Supermini](https://www.espboards.dev/esp32/esp32-s3-super-mini/) (Hopefully someone can offer up some code to parallelise receiving and displaying frames with the S3's second core.)  
- 320x170 LCD display (SPI), can be generic from [aliexpress](https://www.aliexpress.com/item/1005007239448040.html?). can also probably be any other resolution if you can adjust code!
- Some short female to female dupont jumpers. (Technically dont have to be short, but easier to deal fit in enclosure)
- Assembly Guide Coming Soon!
- 3D Print the enclosure from MakerWorld (For appropriate MCU Above): (link tbd)
- Wiring Diagrams XIAO ESP32 C3 & ESP32 S3 Supermini:
  
<img width="45%" alt="Wiring Diagram" src="https://raw.githubusercontent.com/kyarl/ESP32-winmonitor/refs/heads/main/misc/Wiring%20Diagram.png" /> <img width="45%" alt="Wiring Diagram" src="https://raw.githubusercontent.com/kyarl/ESP32-winmonitor/refs/heads/main/misc/s3%20wiring%20diagram.png"  />

Wiring diagrams are pretty yucky so I will probably end up making a schematic at some point. For now just use the code & comments as a quick reference.


## Software Requirements
- **IMPORTANT: The python code is set up to look for a monitor of resolution 640 x 340 Pixels "TARGET_MONITOR_SIZE".** This should be adjusted to ther resolution of one of your monitors, or if you want this to act as a dedicated screen, you must setup a virtual display using: https://github.com/VirtualDrivers/Virtual-Display-Driver
- Python & Whatever awful modules the code needs
- Arduino IDE to upload the code to the ESP32. Google how to make Arduino IDE Compatible with ESP32 Boards if you haven't done this already.

## Usage
- TBD Properly
For RGB565 Mode (Default / the "main" version) then:
- If you are using S3 Supermini, edit pin definitions.
- Upload the RGB565 Arduino Sketch to the esp32
- Run the shortcut or the .pyw file
- Will be in the system tray, you can right click to reconnect or quit
- If you want, add the shortcut to your startup apps folder.

## Troubleshooting
- TBD lol
- Check ur wiring I guess as a first step. Also check your pinout if you got a non-XIAO board.
- Also probably I messed up the code when cleaning it up for github/removing PII.

## License
Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) license

"license allows users to freely share (copy/redistribute) and adapt (remix/build upon) material in any medium. Usage must be non-commercial, and proper attribution must be given to the creator."
