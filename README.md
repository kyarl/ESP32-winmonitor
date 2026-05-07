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

## WiFi Throughput / Theoretical Limits
At 320x170 using full RGB565 colour (16-bit), each frame is ~106 KB.  
At the current achieved ~6.45 FPS, this corresponds to roughly ~685 KB/s (~5.5 Mbit/s).  

The ESP32-C3 Seeed XIAO typically achieves around 10–30 Mbit/s WiFi throughput (~1.25–3.75 MB/s), meaning the current implementation reaches somewhere between 18–55% of the ESP32's theoretical WiFi bandwidth.  

Note that currently using TCP rather than UDP. Could theoretically go faster with UDP, however I assume there are other areas for improvement before this.

Likely bottlenecked by shite code rather than reaching actual hardware limitations here, go ahead and try to optimise/rewrite this :)

# How To Use
## Hardware Requirements
- [Seeed Studio XIAO ESP32C3 Microcontroller](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/) (other ESP32 & Wifi enabled MCUs Probably work too ! More likely if another XIAO Board)
- 320x170 LCD display (SPI), can be generic from [aliexpress](https://www.aliexpress.com/item/1005007239448040.html?). can also probably be any other resolution if you can adjust code!
- Assembly Guide Coming Soon!
- 3D Print the enclosure from MakerWorld: (link tbd)
- Wiring Diagram:<img width="4044" height="2107" alt="Wiring Diagram" src="https://github.com/user-attachments/assets/7d9f1cd0-36bd-4389-9d35-0966f3e6b1d6" />


## Software Requirements
- Python & Whatever awful modules the code needs
- Arduino IDE

## Usage
- TBD Properly
For RGB565 Mode (Default / the "main" version) then:
- Upload the RGB565 Arduino Sketch to the esp32
- Run the shortcut or the .pyw file
- Will be in the system tray, you can right click to reconnect or quit

## Troubleshooting
- TBD lol
- Check ur wiring I guess
- Also probably I fucked up the code when cleaning it up for github

## License
Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) license

"license allows users to freely share (copy/redistribute) and adapt (remix/build upon) material in any medium. Usage must be non-commercial, and proper attribution must be given to the creator."
