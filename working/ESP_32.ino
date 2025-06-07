#include <ArduinoJson.h>
#include "DHT.h"

#define DHTPIN 36
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// Pin tanımları
const int soilMoisturePins[] = {13, 12, 14, 27, 26, 25};
const int flowSensorPins[] = {15, 2, 4};
const int relayPins[] = {16, 17, 5};
const int rainSensorPin = 34;

// Mod tanımları
#define MODE_AI 1
#define MODE_AUTO 2
#define MODE_MANUAL 3

int controlModes[3] = {MODE_MANUAL, MODE_MANUAL, MODE_MANUAL};
int relayStates[3] = {0, 0, 0};

int threshold = 3000;

unsigned long lastSendTime = 0;
unsigned long sendInterval = 1000;

void setup() {
  Serial.begin(115200);
  dht.begin();

  for (int i = 0; i < 6; i++) pinMode(soilMoisturePins[i], INPUT);
  for (int i = 0; i < 3; i++) pinMode(flowSensorPins[i], INPUT);
  for (int i = 0; i < 3; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH); // Röleler başlangıçta kapalı
  }
  pinMode(rainSensorPin, INPUT);
}

void loop() {
  handleSerialCommands();    // Her döngüde seri komutları kontrol et
  updateRelays();            // Röleleri kontrol et

  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= sendInterval) {
    lastSendTime = currentTime;
    sendSensorData();        // Verileri gönder
  }
}

void updateRelays() {
  for (int i = 0; i < 3; i++) {
    if (controlModes[i] == MODE_AUTO) {
      int sensorIndex1 = i;
      int sensorIndex2 = i + 3;
      int avgMoisture = (analogRead(soilMoisturePins[sensorIndex1]) + analogRead(soilMoisturePins[sensorIndex2])) / 2;

      if (avgMoisture > threshold) {
        digitalWrite(relayPins[i], LOW);  // Röleyi aç
        relayStates[i] = 0;
      } else {
        digitalWrite(relayPins[i], HIGH); // Röleyi kapat
        relayStates[i] = 1;
      }
    }
    // AI ve MANUAL modlarda işlem `handleSerialCommands()` ile yapılır
  }
}

void handleSerialCommands() {
  while (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("THRESHOLD:")) {
      threshold = input.substring(10).toInt();
    }
    else if (input.startsWith("MODE:")) {
      int firstColon = input.indexOf(':');
      int secondColon = input.indexOf(':', firstColon + 1);
      int relayIndex = input.substring(firstColon + 1, secondColon).toInt();
      int mode = input.substring(secondColon + 1).toInt();
      if (relayIndex >= 0 && relayIndex < 3) {
        controlModes[relayIndex] = mode;
      }
    }
    else if (input.startsWith("RELAY:")) {
      int firstColon = input.indexOf(':');
      int secondColon = input.indexOf(':', firstColon + 1);
      int relayIndex = input.substring(firstColon + 1, secondColon).toInt();
      int state = input.substring(secondColon + 1).toInt();
      if (relayIndex >= 0 && relayIndex < 3 && controlModes[relayIndex] == MODE_MANUAL) {
        digitalWrite(relayPins[relayIndex], state == 0 ? LOW : HIGH);
        relayStates[relayIndex] = state;
      }
    }
    else if (input == "RELAY1_ON") {
      digitalWrite(relayPins[0], LOW);
      relayStates[0] = 0;
    }
    else if (input == "RELAY1_OFF") {
      digitalWrite(relayPins[0], HIGH);
      relayStates[0] = 1;
    }
    else if (input == "RELAY2_ON") {
      digitalWrite(relayPins[1], LOW);
      relayStates[1] = 0;
    }
    else if (input == "RELAY2_OFF") {
      digitalWrite(relayPins[1], HIGH);
      relayStates[1] = 1;
    }
    else if (input == "RELAY3_ON") {
      digitalWrite(relayPins[2], LOW);
      relayStates[2] = 0;
    }
    else if (input == "RELAY3_OFF") {
      digitalWrite(relayPins[2], HIGH);
      relayStates[2] = 1;
    }
  }
}

void sendSensorData() {
  StaticJsonDocument<512> doc;

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int rain = digitalRead(rainSensorPin);

  doc["temp"] = isnan(temperature) ? -1 : temperature;
  doc["hum"] = isnan(humidity) ? -1 : humidity;
  doc["rain"] = rain;

  for (int i = 0; i < 6; i++) {
    doc["soil" + String(i + 1)] = analogRead(soilMoisturePins[i]);
  }
  for (int i = 0; i < 3; i++) {
    doc["flow" + String(i + 1)] = digitalRead(flowSensorPins[i]);
    doc["relay" + String(i + 1)] = relayStates[i];
    doc["mode" + String(i + 1)] = controlModes[i];
  }

  serializeJson(doc, Serial);
  Serial.println();
}
