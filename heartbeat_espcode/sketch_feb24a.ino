#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Wire.h>
#include "MAX30105.h"           
#include "heartRate.h"        

const char* ssid = "";
const char* password = "";

#define I2C_SDA 21
#define I2C_SCL 22

AsyncWebServer server(80);
MAX30105 particleSensor;

const byte RATE_SIZE = 10;
byte rates[RATE_SIZE]; 
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg;

String fingerStatus = "Initializing...";
unsigned long lastWiFiCheckTime = 0;
const unsigned long wifiCheckInterval = 10000;

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BPM Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: white; text-align: center; padding: 20px; }
        .card { background: #1a1a1a; border: 2px solid #333; padding: 40px; border-radius: 20px; display: inline-block; min-width: 250px; }
        .bpm-val { font-size: 6rem; font-weight: 800; color: #ff3e3e; margin: 10px 0; }
        .label { color: #888; text-transform: uppercase; letter-spacing: 2px; font-size: 0.9rem; }
        .status { margin-top: 20px; font-style: italic; color: #00ff88; }
        .heart { display: inline-block; color: #ff3e3e; animation: pulse 0.8s infinite; }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }
    </style>
</head>
<body>
    <div class="card">
        <div class="label"><span class="heart">♥</span> Heart Rate</div>
        <div class="bpm-val" id="bpm">0</div>
        <div class="label">AVG BPM</div>
        <div id="status" class="status">Loading...</div>
    </div>
    <script>
        setInterval(() => {
            fetch('/data').then(r => r.json()).then(data => {
                document.getElementById('bpm').innerText = data.bpm;
                const statusEl = document.getElementById('status');
                statusEl.innerText = data.status;
                statusEl.style.color = (data.status === "Reading...") ? "#00ff88" : "#ff9800";
            }).catch(e => { document.getElementById('status').innerText = "Offline"; });
        }, 1000);
    </script>
</body>
</html>
)rawliteral";

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n\n--- MAX30102 Optimized Setup ---");

    Wire.begin(I2C_SDA, I2C_SCL, 100000);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
    Serial.println("\nConnected! IP: " + WiFi.localIP().toString());

    if (!particleSensor.begin(Wire, 100000)) { 
        Serial.println("MAX30102 not found.");
        fingerStatus = "Sensor Not Found";
    } else {
        Serial.println("Sensor Detected.");
        byte ledBrightness = 60;
        byte sampleAverage = 4;
        byte ledMode = 2;
        int sampleRate = 100;
        int pulseWidth = 411;
        int adcRange = 4096;
        particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); 
        fingerStatus = "Ready - Place Finger";
    }

    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send_P(200, "text/html", index_html);
    });

    server.on("/data", HTTP_GET, [](AsyncWebServerRequest *request){
        String json = "{\"bpm\":" + String(beatAvg) + ",\"status\":\"" + fingerStatus + "\"}";
        request->send(200, "application/json", json);
    });
    server.begin();
}

void loop() {
    if (fingerStatus == "Sensor Not Found") return;
    long irValue = particleSensor.getIR();

    if (irValue < 50000) {
        fingerStatus = "No finger detected";
        beatAvg = 0;
        for (byte x = 0 ; x < RATE_SIZE ; x++) rates[x] = 0;
    } else {
        fingerStatus = "Reading...";
        
        if (checkForBeat(irValue) == true) {
            long delta = millis() - lastBeat;
            lastBeat = millis();
            beatsPerMinute = 60 / (delta / 1000.0);
            if (beatsPerMinute < 200 && beatsPerMinute > 45) {
                rates[rateSpot++] = (byte)beatsPerMinute; 
                rateSpot %= RATE_SIZE; 
                beatAvg = 0;
                int validReadings = 0;
                for (byte x = 0 ; x < RATE_SIZE ; x++) {
                  if(rates[x] > 0) {
                    beatAvg += rates[x];
                    validReadings++;
                  }
                }
                if(validReadings > 0) beatAvg /= validReadings;
                Serial.print("BPM: ");
                Serial.print(beatsPerMinute);
                Serial.print(" | Avg: ");
                Serial.println(beatAvg);
            }
        }
    }
    if (WiFi.status() != WL_CONNECTED && millis() - lastWiFiCheckTime > wifiCheckInterval) {
        WiFi.reconnect();
        lastWiFiCheckTime = millis();
    }
}