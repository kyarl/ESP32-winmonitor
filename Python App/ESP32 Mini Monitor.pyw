import time
import threading
import sys, os
from pathlib import Path

import pyautogui
from PIL import Image, ImageDraw
import mss

from win11toast import notify
import pystray
from pystray import MenuItem as item

# Module for sending image and managing connection to esp32 
# - ONLY HAVE ONE ENABLED AT A TIME
# - Uncomment the one you would like to use, and comment the other out
# - Also REQUIRES corresponding code on ESP32 side, make sure to upload the correct sketch.

from lib.esp32_tft_wifiSender_RGB565 import send_image, connect_stream      # TCP Coloured 565 or 332
#from lib.esp32_tft_wifiSender_Mono import send_image, connect_stream       # TCP Monochrome
#from lib.esp32_tft_wifiSender_Greyscale import send_image, connect_stream  # TCP Greyscale


#from esp32_tft_wifiSenderUDP import send_image, connect_stream # UDP


### ------- Achieved Framerates -------
# Monochrome = 19.5 fps
# 8 Bit greyscale = 9.6 fps
# RGB 332 = 7.9 fps
# RGB 565 = 6.45 fps

# (RGB 332 looks pretty shit, not worth including for marginal FPS gains)






# ----------------- CONFIG -----------------
ESP_IP = "esp32display.local"       # apparently IP randomly changes which is just great. so use esp32display.local to never connect to wrong thingo
PORT = 12345
WIDTH, HEIGHT = 170, 320
TARGET_FPS = 30                     # target FPS - for RGB565 usually ends up around 4.5~5.5 fps max. doesnt really hurt having this higher than what is achievable.
FRAME_INTERVAL = 1 / TARGET_FPS     # calculates the delay between frames based on FPS target

TARGET_MONITOR_SIZE = (640, 340)        # (width, height)
MONITOR_RETRY_INTERVAL = 1.0       # how long to wait if monitor missing

TRAY_ICON_PATH = Path("icon.ico")  # tray icon 

CURSOR_SPRITE_PATH = Path("cursor.png") # cursor icon 32x32
cursor_img = Image.open(CURSOR_SPRITE_PATH).convert("RGBA")

CONNECT_RETRY_BASE = 1.0           # seconds
CONNECT_RETRY_MAX = 30.0

SEND_RETRY_BASE = 1
SEND_RETRY_MAX = 5.0
# ------------------------------------------


# ------------------------------------------------------------------------------------
# Shouldnt need to modify anything beyond here but its vibecoded garbage so go for it
# ------------------------------------------------------------------------------------

running = True

def send_notification(title: str, msg: str):
    try:
        notify(title, msg)

    except Exception:
        # don't let notification failures crash the capture loop
        print("DEBUG: Failed to send win11 notify.")
        pass

def open_connection_with_retries():
    global running
    """
    Try to connect at most 3 times with exponential backoff.
    Returns a socket on success or raises after 3 failures.
    """
    attempts = 0
    backoff = CONNECT_RETRY_BASE
    while running and attempts < 3:
        try:
            print("DEBUG: Attempting esp32 connection.")
            sock = connect_stream(ESP_IP, PORT)
            print("DEBUG: Virtual Monitor", f"Connected to {ESP_IP}:{PORT}")
            return sock
        except Exception as e:
            attempts += 1
            if attempts >= 3:
                #dont need to notify here because already notifies the runtime error
                '''send_notification(
                    "Virtual Monitor",
                    f"3 attempts to connect failed, ending."
                )'''
                # signal the rest of the program to stop
                running = False
                print("DEBUG: Max 3 Connect Attempts Passed")
                raise RuntimeError("Exceeded max connection attempts")
            # notify and wait before next attempt
            send_notification(
                "Virtual Monitor",
                f"Connection failed ({attempts}/3): {e}. Retrying in {int(backoff)}s"
            )
            print(f"DEBUG: Failed ({attempts}/3) connect attempts.")
            time.sleep(backoff)
            backoff = min(backoff * 2, CONNECT_RETRY_MAX)

def safe_send_image(sock, img):
    """Send image, retrying/connect recover if send fails."""
    backoff = SEND_RETRY_BASE
    while running:
        try:
            send_image(sock, img)
            return True
        except Exception as e:
            print("DEBUG: Image send failed.")
            send_notification("Virtual Monitor", f"Send failed: {e}. Please Reconnect")
            time.sleep(backoff)

            return False

    return False

def capture_loop():
    global running
    sock = None
    fatal_errors = 0

    while running:
        try:
            # initial connect
            print("DEBUG: Start initial connection to esp32.")
            sock = open_connection_with_retries()

            print("DEBUG: ESP32 Socket connection opened.")

            send_notification("Virtual Monitor", "Stream starting...")

            MONITOR_CHECK_INTERVAL = 2.0  # seconds between monitor presence checks
            _last_monitor_check = 0.0
            _last_num_monitors = 0
            target = None

            sct = mss.mss()  # initial instance
            try:
                while running:
                    now = time.time()
                    # Refresh monitor list periodically
                    if now - _last_monitor_check > MONITOR_CHECK_INTERVAL:
                        # Close old instance and recreate to get updated monitors
                        sct.close()
                        sct = mss.mss()

                        monitors = sct.monitors[1:]  # skip "all"

                        if len(monitors) != _last_num_monitors:
                            print("DEBUG: Number of Monitors changed from", _last_num_monitors, "to", len(monitors))
                            _last_num_monitors = len(monitors)
                            target = None  # force re-search

                        # Search for desired monitor
                        for m in monitors:
                            if TARGET_MONITOR_SIZE and (m["width"], m["height"]) == TARGET_MONITOR_SIZE:
                                if target != m:
                                    target = m
                                    print("DEBUG: Found desired monitor.")
                                    break

                        # If not found, retry a few times
                        if not target:
                            send_notification("Virtual Monitor", "Desired monitor not found. Waiting…")
                            attempts = 0
                            while running and not target and attempts < 3:
                                time.sleep(MONITOR_RETRY_INTERVAL)
                                attempts += 1
                                monitors = sct.monitors[1:]
                                for m in monitors:
                                    if TARGET_MONITOR_SIZE and (m["width"], m["height"]) == TARGET_MONITOR_SIZE:
                                        if target != m:
                                            target = m
                                            print("DEBUG: Found desired monitor.")
                                            break

                                if not target and running:
                                    send_notification(
                                        "Virtual Monitor",
                                        f"Attempt {attempts}/3: Still waiting for desired monitor…"
                                    )
                                    time.sleep(2)

                            if not target:
                                send_notification(
                                    "Virtual Monitor",
                                    "3 attempts to find desired monitor failed. Exiting…"
                                )
                                running = False
                                break

                        _last_monitor_check = now


                    # New grab frame (adds cursor position)
                    try:
                        sct_img = sct.grab(target)
                    except Exception as e:
                            send_notification("Virtual Monitor", f"Screenshot failed: {e}. Retrying...")
                            time.sleep(0.5)
                            continue

                    # Convert to PIL image
                    img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

                    # Get absolute cursor position and monitor origin
                    cursor_x, cursor_y = pyautogui.position()
                    origin_x, origin_y, _, _ = target["left"], target["top"], target["width"], target["height"]

                    # Translate to coordinates relative to the grabbed monitor
                    rel_x = cursor_x - origin_x
                    rel_y = cursor_y - origin_y

                    img.paste(cursor_img, (rel_x, rel_y), cursor_img)  # last arg is the mask

                    # Resize/rotate and send
                    #img = img.resize((320, 170), Image.LANCZOS)  # better quality but slower
                    #img = img.resize((320, 170), Image.BILINEAR) # bad quality, faster
                    img = img.reduce(2)  # fast and decent quality
                    
                    img = img.rotate(90, expand=True)
                    if not safe_send_image(sock, img):
                        time.sleep(SEND_RETRY_BASE)
                        print("DEBUG: Breaking Capture Loop.")
                        break
                        
                    time.sleep(FRAME_INTERVAL*0.9)  # pace a bit under target to compensate for processing time

            finally:
                sct.close()

                    #end of monitor send frames thingo

        except KeyboardInterrupt:
            send_notification("Virtual Monitor", "Manual stop requested")

        except Exception as e:
            # Catch-all - notify & try graceful shutdown
            fatal_errors += 1
            send_notification("Virtual Monitor", f"Fatal error: {e}")
            print(f"DEBUG: Fatal error in capture_loop: {e}")
            time.sleep(2.0)
            if fatal_errors >= 3:
                break
            

        finally:
            # best-effort send black frame to clear display
            try:
                black = Image.new("RGB", (320, 170), (0, 0, 0)).rotate(90, expand=True)
                if sock:
                    try:
                        send_image(sock, black)
                        time.sleep(0.3)
                    except Exception:
                        pass
            except Exception:
                pass

            # close socket
            try:
                if sock:
                    sock.close()
            except Exception:
                send_notification("Virtual Monitor", f"Couldnt Close Socket: {e}")
                pass

            print("DEBUG: Exiting capture_loop()")

            if not running:
                send_notification("Virtual Monitor", "Stream Exiting...")

def on_quit(icon, _):
    global running
    running = False
    icon.stop()

def on_restart(icon, _):
    global running
    global t
    running = False

    time.sleep(0.5)  # give threads time to exit
    print("DEBUG: Restarting capture loop...")
    
    #end existing thread if running
    if t.is_alive():
        t.join()
        print("DEBUG: Previous thread joined successfully.")
    else:
        print("DEBUG: Previous thread was not alive.")

    running = True
    time.sleep(0.5)  # ensure fully stopped
    
    start_mini_monitor()
    

def start_mini_monitor():
    global t
    t = threading.Thread(target=capture_loop, daemon=True)
    t.start()
    print("DEBUG: Threading started successfully.")

def main():
    global t
    start_mini_monitor()

    # tray icon
    try:
        tray_img = Image.open(TRAY_ICON_PATH)
        print("DEBUG: Successfully loaded tray icon")
    except Exception:
        tray_img = None


    menu = (item("Reconnect", on_restart),
            item("Quit", on_quit))
    
    icon = pystray.Icon("vmon", tray_img, "Virtual Monitor", menu)

    print("DEBUG: System tray process start.")

    icon.run()      # blocks until Quit selected
    t.join()

    print("DEBUG: Reached end of main().")

    sys.exit()

if __name__ == "__main__":
    print("DEBUG: Starting")
    main()
