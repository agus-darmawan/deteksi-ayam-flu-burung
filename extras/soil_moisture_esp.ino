#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>  // Include the ArduinoJson library

const char* ssid = "your_SSID";              // Your WiFi SSID
const char* password = "your_PASSWORD";      // Your WiFi Password
const char* serverName = "http://your-server-ip-address:5001/update_moisture";  // Python server URL

int soilMoisturePin = 34;  // Pin connected to soil moisture sensor

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  // Read soil moisture sensor
  int soilMoistureValue = analogRead(soilMoisturePin);
  Serial.print("Soil Moisture Value: ");
  Serial.println(soilMoistureValue);

  // Send data to the server
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);

    // Set HTTP headers
    http.addHeader("Content-Type", "application/json");

    // Create JSON object
    DynamicJsonDocument jsonDoc(1024);
    jsonDoc["moisture"] = soilMoistureValue;

    // Serialize JSON object to string
    String httpRequestData;
    serializeJson(jsonDoc, httpRequestData);

    int httpResponseCode = http.POST(httpRequestData);

    // Print response
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("HTTP Response Code: ");
      Serial.println(httpResponseCode);
      Serial.print("Response: ");
      Serial.println(response);
    } else {
      Serial.print("Error on HTTP request. Code: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }

  // Delay between readings
  delay(60000);  // Delay for 1 minute
}
