import socket
from PIL import Image


ESP_IP = "10.0.0.28"   # your ESP32 IP
PORT   = 12345


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

    ### pixels definitions for monochronme Based conversion

    if isinstance(image_or_path, str):
        img = Image.open(image_or_path).convert("1")
    else:
        img = image_or_path.convert("1")

    width, height = img.size
    pixels = img.load()

    data = bytearray()
    byte = 0
    bit_count = 0

    
    # Code for monochrome frames
    for y in range(height):
        for x in range(width):
            bit = 1 if pixels[x, y] else 0

            # MSB first
            byte = (byte << 1) | bit
            bit_count += 1

            if bit_count == 8:
                data.append(byte)
                byte = 0
                bit_count = 0

    # pad final frame byte only once
    if bit_count != 0:
        byte <<= (8 - bit_count)
        data.append(byte)
    
    ### END OF CONVERSION CODE


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
            print(f"FPS: {fps:.2f}")
        '''

