import socket
import struct
from PIL import Image


ESP_IP = "10.0.0.28"   # your ESP32 IP (not required - currently using mDNS)
PORT   = 12345

#old "faster" conversion. supposedly results in the darker/less accurate colours tho.
def rgb888_to_rgb565_old(r, g, b):
    """Convert 8-bit per channel RGB to 16-bit RGB565"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)



# you can try this one but its kind of buns to be honest
# is the "newer version with gamma correction to make colours more vibrant"
def rgb888_to_rgb565_vibrant(r, g, b, gamma=0.9):
    """
    Convert 8-bit RGB to RGB565 with gamma/brightness compensation.
    gamma < 1 → boosts midtones / makes colors more vibrant.
    """
    # Apply gamma correction
    r_corr = int(255 * ((r / 255) ** gamma))
    g_corr = int(255 * ((g / 255) ** gamma))
    b_corr = int(255 * ((b / 255) ** gamma))
    
    # Then round-scale to 565
    r5 = (r_corr * 31 + 127) // 255
    g6 = (g_corr * 63 + 127) // 255
    b5 = (b_corr * 31 + 127) // 255
    
    return (r5 << 11) | (g6 << 5) | b5


def connect_stream(ip, port):
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    return s

frames_sent = 0
last_time = -1

is_testing = False

def send_image(socket, image_or_path):
    # debug stuff
    global is_testing
    global frames_sent
    global last_time

    ### pixels definitions for RGB565 Based conversion
    if isinstance(image_or_path, str):
        img = Image.open(image_or_path).convert("RGB")
    else:
        img = image_or_path.convert("RGB")

    data = bytearray()
    pixels = list(img.getdata())
    

    # FINAL -- RGB565 Conversion
    for r, g, b in pixels:
        #color = rgb888_to_rgb565_vibrant(r, g, b)
        color = rgb888_to_rgb565_old(r, g, b)
        data += struct.pack("<H", color) # Note for me when fucking around with arduino code (not relevant for you): <H is little endian. need to swap to >H if using old code (big endian)
    


    # TEST -- code does half new colours and half old colours if you want to compare
    '''half = len(pixels) // 2
    for i, (r, g, b) in enumerate(pixels):
        if i < half:
            color = rgb888_to_rgb565_channel_boost(r, g, b)       # first half -> right side
        else:
            color = rgb888_to_rgb565(r, g, b)   # second half -> left side
        data += struct.pack(">H", color)'''
    

    # disable sending packets to test if bottleneck is on the ESP32 side or Python side
    if not is_testing:
        socket.sendall(data)
    
    ### disable for normal use
    #calculate the FPS every 300 frames = ~10 seconds at 30FPS, ~20 seconds at 15FPS, ~30 seconds at 10FPS, etc
    '''frames_sent += 1

    if frames_sent % 150 == 0:
        if last_time < 0:
            last_time = time.time()
        else:
            timeInterval = time.time() - last_time
            last_time = time.time()
            fps = 150 / timeInterval
            print(f"FPS: {fps:.2f}")'''
        

