#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

Adafruit_BME280 bme; // I2C

const char* ssid = "S21 Ultra";  // Replace with your hotspot's SSID
const char* password = "seneD7811!";  // Replace with your hotspot's password

const int ledPin = 23;  // Use GPIO 23 for the LED

void setup() {
    Serial.begin(115200);
    pinMode(ledPin, OUTPUT);
    // Initialize the BME280 sensor
    if (!bme.begin(0x76)) {
        Serial.println("Could not find a valid BME280 sensor, check wiring!");
        while (1);
    }
    // Connect to WiFi
    Serial.println("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected.");
}

void sendSensorData() {
  if(WiFi.status() == WL_CONNECTED) { // Check if we're connected to the Wi-Fi
    HTTPClient http;
    http.begin("http://192.168.169.33:5000/sensor-data"); // Your server's URL
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;  // Increased size for safety
    // Format the sensor data to one decimal place for temperature and humidity, no decimals for pressure and altitude
    doc["temperature"] = String(bme.readTemperature(), 1);
    doc["humidity"] = String(bme.readHumidity(), 1);
    doc["pressure"] = String(bme.readPressure() / 100.0F, 0);  // Convert Pa to hPa and round
    doc["altitude"] = String(bme.readAltitude(1013.25), 1);  // Assuming sea-level standard pressure in hPa

    String requestBody;
    serializeJson(doc, requestBody);

    int httpResponseCode = http.POST(requestBody);
    if(httpResponseCode == 200) {
      String response = http.getString(); // Get the response
      if(response.equals("reset")) {
        resetDevice(); // Call the reset function if the server response is "reset"
      }
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }

    http.end(); //Close connection
  } else {
    Serial.println("WiFi not connected");
  }
  
  delay(1000); // Delay for 1 seconds before sending the next data
}


void resetDevice() {
  Serial.println("Resetting device...");
  ESP.restart();
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        digitalWrite(ledPin, HIGH); // LED on if not connected
        WiFi.reconnect();
    } else {
        digitalWrite(ledPin, LOW);
    }

    // Read and print sensor data
    Serial.print("Temperature = ");
    Serial.print(bme.readTemperature());
    Serial.println(" °C");
    Serial.print("Pressure = ");
    Serial.print(bme.readPressure() / 100.0F);
    Serial.println(" hPa");
    Serial.print("Humidity = ");
    Serial.print(bme.readHumidity());
    Serial.println(" %");
    Serial.print("Altitude = ");
    Serial.print(bme.readAltitude(1013.25));
    Serial.println(" meters");

    sendSensorData();  // Send data to the server
}
