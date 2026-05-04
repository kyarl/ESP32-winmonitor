# ESP32-winmonitor
Uses a python app to grab frames of a windows monitor an streams them over wifi to an ESP32 with an 320x170 LCD Screen connected over SPI

Fairwarning this is vibecoded garbage but that is ok because it works! Feel free to optimise this theres probably lots of room to make it faster.

Able to achieve around 5-6 fps when using full RGB565 colours, alternatively can reach higher framerates using either greyscale, or purely B&W colour. Using different colour specs requires completely different Arduino sketches to be uploaded to the ESP32

## Achievable Framerates
In my experience, your results may vary:
- Monochrome = 19.5 fps
- 8 Bit greyscale = 9.6 fps
- RGB 332 = 7.9 fps
- RGB 565 = 6.45 fps

(RGB 332 looks pretty shit, hence not worth including in the code base due to marginal FPS gains over RGB565 which looks much better)

# How To Use
## Hardware Requirements
- [Seeed Studio XIAO ESP32C3 Microcontroller](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/) (other ESP32 & Wifi enabled MCUs Probably work too ! More likely if another XIAO Board)
- 320x170 LCD display (SPI), can be generic from [aliexpress](https://www.aliexpress.com/item/1005007239448040.html?). can also probably be any other resolution if you can adjust code!
- Wiring Diagram:<img width="2107" height="4044" alt="Wiring Diagram" src="https://github.com/user-attachments/assets/bcea3817-a9b8-4690-91e1-419bc28f2af2" />
- 3D Print the enclosure from MakerWorld: (link tbd)


## Software Requirements
- Python & Whatever awful modules the code needs
- Arduino IDE

## Installation
- TBD !

## Usage
- TBD Properly
For RGB565 Mode (Default / the "main" version) then:
- Upload the RGB565 Arduino Sketch to the esp32
- Run the shortcut or the .pyw file
- Will be in the system tray, you can right click to reconnect or quit

## Project Structure
- TBD

## Troubleshooting
- TBD lol
- Check ur wiring I guess
- Also probably I fucked up the code when cleaning it up for github

## License
Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) license

"license allows users to freely share (copy/redistribute) and adapt (remix/build upon) material in any medium. Usage must be non-commercial, and proper attribution must be given to the creator."
