#include <DHT.h>

#define DHTPIN 32
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define RAIN_SENSOR_PIN 34

#define RELAY1_PIN 16
#define RELAY2_PIN 17
#define RELAY3_PIN 5

#define FLOW1_PIN 15
#define FLOW2_PIN 2
#define FLOW3_PIN 18

#define MODE_MANUAL 0
#define MODE_AUTO 1
#define MODE_AI 2

int controlModes[3] = {MODE_MANUAL, MODE_MANUAL, MODE_MANUAL};
int relayStates[3] = {0, 0, 0};
int moistureThreshold = 3000;

int soilPins[6] = {13, 12, 14, 27, 26, 25};

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  pinMode(RELAY3_PIN, OUTPUT);

  pinMode(FLOW1_PIN, INPUT);
  pinMode(FLOW2_PIN, INPUT);
  pinMode(FLOW3_PIN, INPUT);

  pinMode(RAIN_SENSOR_PIN, INPUT);

  for (int i = 0; i < 6; i++) {
    pinMode(soilPins[i], INPUT);
  }

  digitalWrite(RELAY1_PIN, LOW);
  digitalWrite(RELAY2_PIN, LOW);
  digitalWrite(RELAY3_PIN, LOW);
}

void updateThreshold(int value) {
  if (value < 2000) value = 2000;
  else if (value > 3500) value = 3500;
  moistureThreshold = value;
}

void handleSerialCommands() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("THRESHOLD:")) {
      int val = cmd.substring(10).toInt();
      updateThreshold(val);
    }
    else if (cmd.startsWith("MODE:")) {
      int sepIndex = cmd.indexOf(':', 5);
      if (sepIndex != -1) {
        int relayIndex = cmd.substring(5, sepIndex).toInt();
        int mode = cmd.substring(sepIndex + 1).toInt();
        if (relayIndex >= 0 && relayIndex < 3) {
          controlModes[relayIndex] = mode;
        }
      }
    }
    else if (cmd.startsWith("RELAY:")) {
      int relayIndex = cmd.substring(6, 7).toInt();
      int state = cmd.substring(8).toInt();
      if (relayIndex >= 0 && relayIndex < 3) {
        relayStates[relayIndex] = state;
      }
    }
  }
}

void updateRelays(int* soilVals) {
  int relayPins[3] = {RELAY1_PIN, RELAY2_PIN, RELAY3_PIN};
  int groups[3][2] = {{0, 3}, {1, 4}, {2, 5}};

  for (int i = 0; i < 3; i++) {
    int avgMoisture = (soilVals[groups[i][0]] + soilVals[groups[i][1]]) / 2;
    int newState = LOW;

    switch (controlModes[i]) {
      case MODE_MANUAL:
        newState = relayStates[i];
        break;

      case MODE_AUTO:
        newState = (avgMoisture > moistureThreshold) ? HIGH : LOW;
        break;

      case MODE_AI:
        // AI komutlarını doğrudan işle
        if (Serial.available()) {
          String command = Serial.readStringUntil('\n');
          command.trim();

          if (command == "RELAY1_ON") {
            digitalWrite(RELAY1_PIN, LOW);
            Serial.println("RELAY1 is ON");
          }
          else if (command == "RELAY1_OFF") {
            digitalWrite(RELAY1_PIN, HIGH);
            Serial.println("RELAY1 is OFF");
          }
          else if (command == "RELAY2_ON") {
            digitalWrite(RELAY2_PIN, LOW);
            Serial.println("RELAY2 is ON");
          }
          else if (command == "RELAY2_OFF") {
            digitalWrite(RELAY2_PIN, HIGH);
            Serial.println("RELAY2 is OFF");
          }
          else if (command == "RELAY3_ON") {
            digitalWrite(RELAY3_PIN, LOW);
            Serial.println("RELAY3 is ON");
          }
          else if (command == "RELAY3_OFF") {
            digitalWrite(RELAY3_PIN, HIGH);
            Serial.println("RELAY3 is OFF");
          }
        }
        continue;  // Bu iterasyonu atla, AI komutları zaten röleleri kontrol etti
    }

    digitalWrite(relayPins[i], newState);
    relayStates[i] = newState;
  }
}

void sendSensorData() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  int soilVals[6];
  for (int i = 0; i < 6; i++) {
    soilVals[i] = analogRead(soilPins[i]);
  }

  int soil_avg1_4 = (soilVals[0] + soilVals[3]) / 2;
  int soil_avg2_5 = (soilVals[1] + soilVals[4]) / 2;
  int soil_avg3_6 = (soilVals[2] + soilVals[5]) / 2;

  updateRelays(soilVals);

  bool isRaining = digitalRead(RAIN_SENSOR_PIN) == LOW;

  int flow1 = digitalRead(FLOW1_PIN);
  int flow2 = digitalRead(FLOW2_PIN);
  int flow3 = digitalRead(FLOW3_PIN);

  Serial.print("{");
  Serial.printf("\"soil_1\":%d,", soilVals[0]);
  Serial.printf("\"soil_4\":%d,", soilVals[3]);
  Serial.printf("\"soil_avg1_4\":%d,", soil_avg1_4);

  Serial.printf("\"soil_2\":%d,", soilVals[1]);
  Serial.printf("\"soil_5\":%d,", soilVals[4]);
  Serial.printf("\"soil_avg2_5\":%d,", soil_avg2_5);

  Serial.printf("\"soil_3\":%d,", soilVals[2]);
  Serial.printf("\"soil_6\":%d,", soilVals[5]);
  Serial.printf("\"soil_avg3_6\":%d,", soil_avg3_6);

  Serial.printf("\"temp\":%.2f,", temperature);
  Serial.printf("\"humidity\":%.2f,", humidity);
  Serial.printf("\"rain\":%d,", isRaining ? 1 : 0);

  Serial.printf("\"flow1\":%d,", flow1);
  Serial.printf("\"flow2\":%d,", flow2);
  Serial.printf("\"flow3\":%d,", flow3);

  Serial.printf("\"relay1\":%d,", digitalRead(RELAY1_PIN));
  Serial.printf("\"relay2\":%d,", digitalRead(RELAY2_PIN));
  Serial.printf("\"relay3\":%d", digitalRead(RELAY3_PIN));
  Serial.println("}");
}

void loop() {
  handleSerialCommands();
  static unsigned long lastSend = 0;
  if (millis() - lastSend > 1000) {
    lastSend = millis();
    sendSensorData();
  }
}
