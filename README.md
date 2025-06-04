# Smart Irrigation System – ESP32 & LSTM

This project is an IoT-based smart irrigation system that utilizes an ESP32 microcontroller and various sensors to collect environmental data (such as soil moisture, temperature, and humidity), predicts future moisture levels using an LSTM (Long Short-Term Memory) model, and automatically controls watering based on these predictions to conserve water.

## 🔧 Hardware Components

- ESP32 Dev Kit v1
- 6 x Soil Moisture Sensors
- 1 x Rain Sensor
- 1 x DHT11 (Temperature & Humidity)
- 3 x Water Flow Sensors
- 3 x 12V Solenoid Valves

## 🧠 Software Features

- ESP32 programmed with Arduino IDE
- Data logging to Google Sheets
- LSTM model for moisture prediction
- Python-based model training
- Automated irrigation decision based on model output

## ⚙️ System Architecture

ESP32 <---> Sensors
Sensor data <--> Python 
Google Sheets <--> Python(LSTM)
Model output --> ESP32 --> Irrigation control


## 🧪 Model Performance

- Dataset: 14440 samples (1-minute intervals)(10 days)
- Train/Validation split: 70% / 30% (training, test and validation sets)


## 📦 Setup Instructions

### 1. ESP32 Setup

```bash
Install the ESP32 board in the Arduino IDE.
Upload the provided code and connect all sensors accordingly.

## 📊** Visuals**
![image](https://github.com/user-attachments/assets/f23be9af-b8ba-4f47-9dab-e242f2aa8942)
![Ekran görüntüsü 2025-06-03 221739](https://github.com/user-attachments/assets/8b71488a-06eb-4b86-84fc-957e8747d511)
![Figure_n1](https://github.com/user-attachments/assets/1cff2abd-3b0b-47b5-a91c-66684c55d088)
![Figure_5](https://github.com/user-attachments/assets/5d349db9-a841-4542-b1c6-0d0256a50734)


## 👤 **Developer**
Name: Yunus Emre KUNT

University: Mugla Sitki Kocman University – Electrical and Electronics Engineering

LinkedIn: https://www.linkedin.com/in/yunusemrekunt/
