import os
from tensorflow.keras.models import load_model
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import serial
import time
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import os
from watering_decision import watering_decision
from watering_decision import watering_time_expected
from BlynkLib import Blynk

model_path = 'model1.keras'

os.environ.pop("https_proxy", None)
os.environ.pop("http_proxy", None)

if os.path.exists(model_path):
    print("Eğitimli model bulundu, yükleniyor...")
    model1 = load_model(model_path)
else:
    print("Model bulunamadı, yeniden eğitiliyor...")

model_path2 = 'model2.keras'

if os.path.exists(model_path2):
    print("Eğitimli model bulundu, yükleniyor...")
    model2 = load_model(model_path2)
else:
    print("Model bulunamadı, yeniden eğitiliyor...")

model_path3 = 'model3.keras'

if os.path.exists(model_path3):
    print("Eğitimli model bulundu, yükleniyor...")
    model3 = load_model(model_path3)
else:
    print("Model bulunamadı, yeniden eğitiliyor...")

# Google Sheets API kimlik doğrulama
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("my-project2dadadada.json", scope)
client = gspread.authorize(creds)

# Google Sheets'den veri çekme
sheet = client.open("project_2").worksheet("Sheet1")
data = sheet.get_all_records()
df = pd.DataFrame(data)
# Veri ön işleme
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

df.columns = df.columns.str.strip()
df.index = pd.to_datetime(df['zaman'], format='mixed')

# Normalizasyon
df['Soil_avg_1_4'] = df[['Soil_1', 'Soil_4']].mean(axis=1)
df['Soil_avg_2_5'] = df[['Soil_2', 'Soil_5']].mean(axis=1)
df['Soil_avg_3_6'] = df[['Soil_3', 'Soil_6']].mean(axis=1)

features = df[['Sıcaklık (°C)', 'Nem (%)', 'Soil_1', 'Soil_4', 'Soil_avg_1_4']]
feature_scaler = MinMaxScaler()
scaled_features = feature_scaler.fit_transform(features)

target_scaler = MinMaxScaler()
scaled_target = target_scaler.fit_transform(df[['Soil_avg_1_4']])

def create_seq2seq_dataset(features, target, lookback=60, forecast_horizon=30):
    X, y = [], []
    for i in range(len(features) - lookback - forecast_horizon + 1):
        X.append(features[i:i+lookback])
        y.append(target[i+lookback:i+lookback+forecast_horizon].flatten())  # çoklu çıkış
    return np.array(X), np.array(y)

lookback = 60
forecast_horizon = 30
X, y = create_seq2seq_dataset(scaled_features, scaled_target, lookback, forecast_horizon)


# %70 eğitim, %15 validation, %15 test gibi düşünelim:
train_size = int(len(X) * 0.7)
val_size = int(len(X) * 0.15)

X_train = X[:train_size]
y_train = y[:train_size]

X_val = X[train_size:train_size+val_size]
y_val = y[train_size:train_size+val_size]

X_test = X[train_size+val_size:]
y_test = y[train_size+val_size:]

features2 = df[['Sıcaklık (°C)', 'Nem (%)', 'Soil_2', 'Soil_5', 'Soil_avg_2_5']]
feature_scaler2 = MinMaxScaler()
scaled_features2 = feature_scaler2.fit_transform(features2)

target_scaler2 = MinMaxScaler()
scaled_target2 = target_scaler2.fit_transform(df[['Soil_avg_2_5']])

def create_seq2seq_dataset2(features2, target, lookback=60, forecast_horizon=30):
    X_2, y_2 = [], []
    for i in range(len(features2) - lookback - forecast_horizon + 1):
        X_2.append(features2[i:i+lookback])
        y_2.append(target[i+lookback:i+lookback+forecast_horizon].flatten())  # çoklu çıkış
    return np.array(X_2), np.array(y_2)

lookback = 60
forecast_horizon = 30
X_2, y_2 = create_seq2seq_dataset2(scaled_features2, scaled_target2, lookback, forecast_horizon)

X_train2 = X_2[:train_size]
y_train2 = y_2[:train_size]
X_val2 = X_2[train_size:train_size+val_size]
y_val2 = y_2[train_size:train_size+val_size]
X_test2 = X_2[train_size+val_size:]
y_test2 = y_2[train_size+val_size:]

features3 = df[['Sıcaklık (°C)', 'Nem (%)', 'Soil_3', 'Soil_6', 'Soil_avg_3_6']]
feature_scaler3 = MinMaxScaler()
scaled_features3 = feature_scaler3.fit_transform(features3)

target_scaler3 = MinMaxScaler()
scaled_target3 = target_scaler3.fit_transform(df[['Soil_avg_3_6']])

def create_seq2seq_dataset3(features3, target, lookback=60, forecast_horizon=30):
    X_3, y_3 = [], []
    for i in range(len(features3) - lookback - forecast_horizon + 1):
        X_3.append(features3[i:i+lookback])
        y_3.append(target[i+lookback:i+lookback+forecast_horizon].flatten())  # çoklu çıkış
    return np.array(X_3), np.array(y_3)

lookback = 60
forecast_horizon = 30
X_3, y_3 = create_seq2seq_dataset3(scaled_features3, scaled_target3, lookback, forecast_horizon)

X_train3 = X_3[:train_size]
y_train3 = y_3[:train_size]
X_val3 = X_3[train_size:train_size+val_size]
y_val3 = y_3[train_size:train_size+val_size]
X_test3 = X_3[train_size+val_size:]
y_test3 = y_3[train_size+val_size:]

y_pred1 = model1.predict(X_test)
y_pred2 = model2.predict(X_test2)
y_pred3 = model3.predict(X_test3)

# Ters transform
y_pred1_inv = target_scaler.inverse_transform(y_pred1)
y_val1_inv = target_scaler.inverse_transform(y_test)

y_pred2_inv = target_scaler2.inverse_transform(y_pred2)
y_val2_inv = target_scaler2.inverse_transform(y_test2)

y_pred3_inv = target_scaler3.inverse_transform(y_pred3)
y_val3_inv = target_scaler3.inverse_transform(y_test3)

mae1 = mean_absolute_error(y_val1_inv.flatten(), y_pred1_inv.flatten())
mae2 = mean_absolute_error(y_val2_inv.flatten(), y_pred2_inv.flatten())
mae3 = mean_absolute_error(y_val3_inv.flatten(), y_pred3_inv.flatten())
print(f"Model 1 MAE: {mae1/4095:.3f}")
print(f"Model 2 MAE: {mae2/4095:.3f}")
print(f"Model 3 MAE: {mae3/4095:.3f}")

forecast_soil = y_pred1_inv[0]
print(forecast_soil)

forecast_soil2 = y_pred2_inv[0]
print(forecast_soil2)

forecast_soil3 = y_pred3_inv[0]
print(forecast_soil3)

#ser = serial.Serial('COM3', 115200, timeout=1)

# Blynk olaylarını kontrol et (loop içinde)
BLYNK_AUTH = 'awkBH3npyMUQK3caHvCWGynfEZn4ZlDi'
blynk = Blynk(BLYNK_AUTH)

sulama_yapildi_1= False
sulama_yapildi_2= False
sulama_yapildi_3= False


relay1_state= 0
relay2_state= 0
relay3_state= 0

current_mode= 1

relay1_state_controller = 0
relay2_state_controller = 0
relay3_state_controller = 0 

@blynk.on("V5")
def v5_write_handler(value):
    global relay1_state_controller
    relay1_state_controller = int(value[0])
    print('Relay_state_1 {}'.format(value[0]))

@blynk.on("V6")
def v6_write_handler(value):
    global relay2_state_controller
    relay2_state_controller = int(value[0])
    print('Relay_state_2 {}'.format(value[0]))

@blynk.on("V7")
def v7_write_handler(value):
    global relay3_state_controller
    relay3_state_controller = int(value[0])
    print('Relay_state_3 {}'.format(value[0]))

@blynk.on("V9")
def v9_write_handler(value):
    global current_mode
    current_mode = int(value[0])
    


def set_mode_on_esp(ser, mode):
    for i in range(3):
        cmd = f"MODE:{i}:{mode}\n"
        ser.write(cmd.encode())
        time.sleep(0.05)

def run_ai_mode():
    global sulama_yapildi_1, sulama_yapildi_2, sulama_yapildi_3, ser
            
    if watering_decision(forecast_soil, threshold=2260, rate=0.5):
        watering_time = watering_time_expected(forecast_soil, threshold=2250, interval_second=15)
        print(f"Watering decision for pot_1: Yes, time: {watering_time} second(s)")
        sulama_yapildi_1 = True    
    else:
        print("Decision pot_1: NO")


    
       
    
    # Saksı 2
    if watering_decision(y_pred2_inv[0], threshold=2930, rate=0.5):
        watering_time = watering_time_expected(y_pred2_inv[0], threshold=2260, interval_second=15)
        print(f"Watering decision for pot_2: Yes, time: {watering_time} second(s)")
        sulama_yapildi_2 = True

        

    else:
        print("Decision pot_2: NO")

        # Röle 3 - Soil_avg_3_6
    # Saksı 3
    if watering_decision(y_pred3_inv[0], threshold=2500, rate=0.5):
        watering_time = watering_time_expected(y_pred3_inv[0], threshold=2500, interval_second=15)
        print(f"Watering decision for pot_3: Yes, time: {watering_time} second(s)")
        sulama_yapildi_3 = True
    else:
        print("Decision pot_3: NO")

def run_auto_mode():
    print("Auto mode aktive")
        
    
        
        

    if df['Soil_avg_2_5'].iloc[-1] > 3000:
        global relay2_state
        ser.write(b'RELAY2_ON\n')
        relay2_state=1
        ser.write(b'RELAY2_OFF\n')
        relay2_state= relay2_state
    else:
        relay2_state=0
        

    if df['Soil_avg_3_6'].iloc[-1] > 3000:
        global relay3_state
        ser.write(b'RELAY3_ON\n')
        relay3_state=1
        ser.write(b'RELAY3_OFF\n')
        relay3_state=relay3_state
    else:
        relay3_state=0
        

def run_manual_mode():
    
    global relay1_state_controller, relay1_state
    global relay2_state_controller, relay2_state
    global relay3_state_controller, relay3_state

    print("Manual mode aktive ")
    # örnek: blynk V31 pininden gelen değeri kontrol et
        
    if relay1_state_controller == 1:
        print('Valve 1 Active')
        relay1_state = 1
    else:
        print('Valve 1 Terminated')
        relay1_state=0
    
    
    if relay2_state_controller == 1:
        print('Valve 2 Active')
        relay2_state=1
    else:
        print('Valve 2 Terminated')
        relay2_state= 0
    
    
    if relay3_state_controller == 1:
        print('Valve 3 Active')
        relay3_state=1
    else:
        print('Valve 3 Terminated')
        relay3_state=0
     



