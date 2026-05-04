# ESP32-winmonitor
Uses a python app to grab frames of a windows monitor an streams them over wifi to an ESP32 with an 320x170 LCD Screen connected over SPI

Able to achieve around 5-6 fps when using full RGB565 colours, alternatively can reach higher framerates using either greyscale, or purely B&W colour. Using different colour specs requires completely different Arduino sketches to be uploaded to the ESP32
