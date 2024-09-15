
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "secrets.h"

// P1 meter settings
#define P1_SERIAL_RX D1
#define P1_SERIAL_BAUD 115200

// MQTT settings
const char* mqtt_server = MQTT_SERVER;
const int mqtt_port = MQTT_PORT;
const char* mqtt_user = MQTT_USER;
const char* mqtt_password = MQTT_PASSWORD;
const char* mqtt_topic = "p1meter/energy_usage";

// Constants
const unsigned long WIFI_TIMEOUT = 30000; // 30 seconds
const unsigned long MQTT_RETRY_INTERVAL = 5000; // 5 seconds
const size_t MAX_BUFFER_SIZE = 1024; // Maximum size for P1 buffer

WiFiClient espClient;
PubSubClient client(espClient);
char p1_buffer[MAX_BUFFER_SIZE];
size_t buffer_index = 0;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startAttemptTime = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < WIFI_TIMEOUT) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Failed to connect to WiFi. Restarting...");
    ESP.restart();
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  unsigned long lastAttemptTime = 0;
  while (!client.connected()) {
    if (millis() - lastAttemptTime > MQTT_RETRY_INTERVAL) {
      lastAttemptTime = millis();
      Serial.print("Attempting MQTT connection...");
      if (client.connect("ESP8266Client", mqtt_user, mqtt_password)) {
        Serial.println("connected");
      } else {
        Serial.print("failed, rc=");
        Serial.print(client.state());
        Serial.println(" try again in 5 seconds");
      }
    }
    yield(); // Allow ESP8266 to handle background tasks
  }
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(P1_SERIAL_BAUD, SERIAL_8N1, SERIAL_FULL, 1, P1_SERIAL_RX);
  
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  while (Serial1.available()) {
    char c = Serial1.read();
    if (c != '
' && buffer_index < MAX_BUFFER_SIZE - 1) {
      p1_buffer[buffer_index++] = c;
    } else {
      p1_buffer[buffer_index] = ' ';
      process_p1_data(p1_buffer);
      buffer_index = 0;
    }
  }
}

void process_p1_data(const char* data) {
  if (strncmp(data, "1-0:1.7.0", 9) == 0) {
    char* start = strchr(data, '(');
    char* end = strchr(data, '*');
    if (start && end && start < end) {
      *end = ' ';
      float power = atof(start + 1);
    
      char mqtt_message[10];
      snprintf(mqtt_message, sizeof(mqtt_message), "%.2f", power);
    
      if (client.publish(mqtt_topic, mqtt_message)) {
        Serial.print("Published power usage: ");
        Serial.println(mqtt_message);
      } else {
        Serial.println("Failed to publish MQTT message");
      }
    }
  }
}
