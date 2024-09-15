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

WiFiClient espClient;
PubSubClient client(espClient);
String p1_buffer = "";

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client", mqtt_user, mqtt_password)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(P1_SERIAL_BAUD, SERIAL_8N1, SERIAL_FULL, 1, P1_SERIAL_RX);
  
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (Serial1.available()) {
    char c = Serial1.read();
    if (c != '\n') {
      p1_buffer += c;
    } else {
      process_p1_data(p1_buffer);
      p1_buffer = "";
    }
  }
}

void process_p1_data(String data) {
  if (data.startsWith("1-0:1.7.0")) {
    int start = data.indexOf('(') + 1;
    int end = data.indexOf('*');
    float power = data.substring(start, end).toFloat();
    
    char mqtt_message[10];
    dtostrf(power, 4, 2, mqtt_message);
    
    client.publish(mqtt_topic, mqtt_message);
    Serial.print("Published power usage: ");
    Serial.println(mqtt_message);
  }
}
