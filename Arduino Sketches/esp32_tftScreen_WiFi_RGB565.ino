#include <WiFi.h>
#include <ESPmDNS.h> 
#include <HTTPClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

// Pinouts:
// - Note, you dont need to define the pins for SPI, unless you use non-default ones.

// GENERIC ESP32 S3 Supermini (NOT C3).
// Check YOUR board's silkscreen; SuperMini variants differ.
//
// BLK (LED)  = GPIO 3
// CS         = GPIO 10
// DC         = GPIO  4
// RST        = GPIO  5
// SDA/MOSI   = GPIO 11  (SPI MOSI default)
// SCL/SCK    = GPIO 12  (SPI SCK  default)

// XIAO ESP32C3:
// mosi / sda connected to D10 (GPIO10 default xiao)
// miso NC (not connected)
// scl / sck connected to D8 (GPIO8 default xiao)
#define TFT_CS   6 // GPIO6 (D4)
#define TFT_DC   2 // GPIO2 (D0)
#define TFT_RST  3 // GPIO3 (D1)
#define TFT_BLK  7 // GPIO7 (D5)


#define WIDTH    170
#define HEIGHT   320
#define PORT     12345


// for idle display screen
unsigned long lastStatusUpdate = 0;
unsigned long startTime = millis();
bool statusScreenDrawn = false;


Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);
uint16_t frameBuffer[WIDTH * HEIGHT] = {};


// WIFI Credentials
const char* ssid = "your wifi name";
const char* password = "password";

WiFiServer server(PORT);

void setup() {
  Serial.begin(115200);

  pinMode(TFT_BLK, OUTPUT);
  digitalWrite(TFT_BLK, HIGH);
  
  SPI.begin();
  SPI.setFrequency(40000000);

  tft.init(WIDTH, HEIGHT);
  tft.setRotation(0);
  tft.fillScreen(ST77XX_BLACK);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (millis() - start > 10000) {          // 10-second timeout
      Serial.println("\nWi-Fi connect failed, rebooting...");
      ESP.restart();                         // soft reset
    }
  }

  String mDNSMessage = "";

  if (MDNS.begin("esp32display")) {
    Serial.println("mDNS responder started");
    mDNSMessage = "mDNS Successful, @esp32display.local";
  } else {
    Serial.println("mDNS responder failed to start");
    mDNSMessage = "mDNS failed to start, reboot or use IP instead";
  }

  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  server.begin();
  server.setNoDelay(true); // Disable Nagle's algorithm

  Serial.println("TCP server started");
}

void loop() {
  WiFiClient client = server.available();
  if (!client) {
    if (!statusScreenDrawn) {
      drawStatusStatic();
    }

    if (millis() - lastStatusUpdate > 1000) {
      updateStatusDynamic();
      lastStatusUpdate = millis();
    }

    return;
  }
  
  
  Serial.println("Client connected");
  tft.setRotation(0);
  statusScreenDrawn = false;

  client.setNoDelay(true);
  client.setTimeout(100);

  uint8_t buffer[2048];
  size_t totalBytes = WIDTH * HEIGHT * 2;

  while (client.connected()) {
    size_t receivedBytes = 0;
    unsigned long frameStart = millis();

    // Start display write ONCE per frame
    tft.startWrite();
    tft.setAddrWindow(0, 0, WIDTH, HEIGHT);

    while (receivedBytes < totalBytes) {
      // Check connection more frequently
      if (!client.connected()) break;

      int available = client.available();
      if (available > 0) {
        size_t remaining = totalBytes - receivedBytes;
        size_t chunkSize = min((size_t)2048, remaining);
        chunkSize = min(chunkSize, (size_t)available); // Don't read more than available
        
        int len = client.readBytes(buffer, chunkSize);
        if (len <= 0) break;

        // Write directly to display
        tft.writePixels((uint16_t*)buffer, len / 2, true, false);
        
        receivedBytes += len;
        frameStart = millis(); // Reset timeout on each successful read
      }
      else {
        // Allow time for more data to arrive, but don't block forever
        if (millis() - frameStart > 2000) { // 2 second timeout per frame
          Serial.println("Frame timeout");
          break;
        }
        delay(1); // Small delay to prevent tight polling
      }
    }
    
    tft.endWrite();
    
    // If we didn't get a complete frame, disconnect
    if (receivedBytes < totalBytes) {
      Serial.printf("Incomplete frame: %d/%d bytes\n", receivedBytes, totalBytes);
      client.stop();
      break;
    }
  }

  Serial.println("Client disconnected");
  tft.fillScreen(ST77XX_BLACK);
}



void drawStatusStatic() {
  tft.setRotation(3);   // landscape for status screen

  tft.fillScreen(ST77XX_BLACK);

  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(2);

  tft.setCursor(10,10);
  tft.println("Waiting for client...");
  tft.println();

  tft.print("IP: ");
  tft.println(WiFi.localIP());

  tft.print("SSID: ");
  tft.println(WiFi.SSID());

  tft.println();
  tft.println("Uptime:      Temp:");
  tft.println();

  statusScreenDrawn = true;
}

void updateStatusDynamic() {

  tft.setTextColor(ST77XX_WHITE, ST77XX_BLACK); // overwrite cleanly
  tft.setCursor(10, 120);

  tft.print((millis() - startTime)/1000);
  tft.print(" s   "); // extra spaces clears old digits

  float ESPtemperature = round(temperatureRead());
  tft.setCursor(160, 120);
  tft.print(ESPtemperature);
  tft.println("C");
}
