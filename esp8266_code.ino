#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

const char* ssid = "WIRELESS 4";
const char* password = "197319772005";

// Supabase configuration
const char* supabaseUrl = "https://your-project-ref.supabase.co";
const char* supabaseKey = "your-anon-key";
const char* supabaseEndpoint = "/rest/v1/sensor_data";

ESP8266WebServer server(80);
SoftwareSerial ArduinoSerial(D2, D3); // RX, TX

// Updated variables to match Arduino data
float beatAvg = 0;
float irValue = 0;
float humidity = 0;
float tempC = 0;
float tempF = 0;
float heatIndexC = 0;
float heatIndexF = 0;

unsigned long lastUploadTime = 0;
const unsigned long uploadInterval = 10000; // Upload every 10 seconds

void setup() {
  Serial.begin(115200);
  ArduinoSerial.begin(9600);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/data", HTTP_GET, handleGetData);
  server.begin();
}

void uploadToSupabase() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient https;
    WiFiClientSecure client;
    
    // Disable SSL certificate verification
    client.setInsecure();
    
    // Create JSON document
    DynamicJsonDocument doc(1024);
    
    // Format the data according to the table structure with 2 decimal places
    doc["beat_avg"] = round(beatAvg * 100.0) / 100.0;
    doc["ir_value"] = round(irValue * 100.0) / 100.0;
    doc["humidity"] = round(humidity * 100.0) / 100.0;
    doc["temperature_c"] = round(tempC * 100.0) / 100.0;
    doc["temperature_f"] = round(tempF * 100.0) / 100.0;
    doc["heat_index_c"] = round(heatIndexC * 100.0) / 100.0;
    doc["heat_index_f"] = round(heatIndexF * 100.0) / 100.0;

    String jsonString;
    serializeJson(doc, jsonString);

    Serial.println("\n--- Debug Info ---");
    Serial.println("JSON Payload:");
    Serial.println(jsonString);

    // Construct the full URL
    String url = String(supabaseUrl);
    if (url.endsWith("/")) {
      url = url.substring(0, url.length() - 1);
    }
    url += supabaseEndpoint;

    Serial.println("\nUploading to URL:");
    Serial.println(url);
    
    https.begin(client, url);  // Note: using https instead of http
    
    // Set headers
    https.addHeader("Content-Type", "application/json");
    https.addHeader("apikey", supabaseKey);
    https.addHeader("Authorization", "Bearer " + String(supabaseKey));
    https.addHeader("Prefer", "return=minimal");

    Serial.println("\nHeaders:");
    Serial.println("Content-Type: application/json");
    Serial.println("apikey: " + String(supabaseKey));
    Serial.println("Authorization: Bearer " + String(supabaseKey));
    Serial.println("Prefer: return=minimal");

    // Send POST request
    int httpResponseCode = https.POST(jsonString);

    Serial.println("\nResponse:");
    if (httpResponseCode > 0) {
      String response = https.getString();
      Serial.printf("HTTP Code: %d\n", httpResponseCode);
      Serial.println("Response body: " + response);
    } else {
      Serial.printf("Upload failed, error: %s\n", https.errorToString(httpResponseCode).c_str());
    }
    Serial.println("----------------\n");

    https.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void loop() {
  server.handleClient();
  
  if (ArduinoSerial.available()) {
    String payload = ArduinoSerial.readStringUntil('\n');
    payload.trim();
    
    // Debug print received data
    Serial.println("\nReceived data from Arduino:");
    Serial.println(payload);
    
    // Split the received string into values
    int index = 0;
    String values[7];
    
    while (payload.length() > 0) {
      int commaIndex = payload.indexOf(',');
      if (commaIndex >= 0) {
        values[index] = payload.substring(0, commaIndex);
        payload = payload.substring(commaIndex + 1);
      } else {
        values[index] = payload;
        payload = "";
      }
      index++;
    }
    
    if (index == 7) {
      // Debug print parsed values
      Serial.println("\nParsed values:");
      
      beatAvg = values[0].toFloat();
      Serial.println("beatAvg: " + String(beatAvg));
      
      irValue = values[1].toFloat();
      Serial.println("irValue: " + String(irValue));
      
      humidity = values[2].toFloat();
      Serial.println("humidity: " + String(humidity));
      
      tempC = values[3].toFloat();
      Serial.println("tempC: " + String(tempC));
      
      tempF = values[4].toFloat();
      Serial.println("tempF: " + String(tempF));
      
      heatIndexC = values[5].toFloat();
      Serial.println("heatIndexC: " + String(heatIndexC));
      
      heatIndexF = values[6].toFloat();
      Serial.println("heatIndexF: " + String(heatIndexF));
      
      // Upload to Supabase if enough time has passed
      if (millis() - lastUploadTime >= uploadInterval) {
        uploadToSupabase();
        lastUploadTime = millis();
      }
    } else {
      Serial.println("Error: Incorrect number of values received");
      Serial.println("Expected 7 values, got " + String(index));
    }
  }
}

void handleGetData() {
  DynamicJsonDocument doc(1024);
  
  // Updated JSON response with rounded values
  doc["beatAvg"] = round(beatAvg * 100.0) / 100.0;
  doc["irValue"] = round(irValue * 100.0) / 100.0;
  doc["humidity"] = round(humidity * 100.0) / 100.0;
  doc["temperatureC"] = round(tempC * 100.0) / 100.0;
  doc["temperatureF"] = round(tempF * 100.0) / 100.0;
  doc["heatIndexC"] = round(heatIndexC * 100.0) / 100.0;
  doc["heatIndexF"] = round(heatIndexF * 100.0) / 100.0;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
} 