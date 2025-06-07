import BlynkLib
import serial
import time
from functions import run_ai_mode, run_auto_mode, run_manual_mode, set_mode_on_esp

BLYNK_AUTH = 'sBoYyvmB8lUN-eItZEX9M1GdnEaPdkOq'


# initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)
ser = serial.Serial('COM3', 115200, timeout=1)

current_mode = 0
last_mode = -1  # Başlangıçta farklı bir değer

relay1_state=0
relay2_state=0
relay3_state=0

relay1_state_controller = 0
relay2_state_controller = 0
relay3_state_controller = 0

@blynk.on("V9")
def v9_write_handler(value):
    global current_mode
    current_mode = int(value[0])


@blynk.on("V7")
def v7_write_handler(value):
    global relay3_state
    relay3_state = int(value[0])
    ser.write(f"RELAY:0:{relay1_state}\n".encode())
    
@blynk.on("V6")
def v6_write_handler(value):
    global relay2_state
    relay2_state = int(value[0])
    ser.write(f"RELAY:0:{relay1_state}\n".encode())

@blynk.on("V5")
def v5_write_handler(value):
    global relay1_state
    relay1_state = int(value[0])
    ser.write(f"RELAY:0:{relay1_state}\n".encode())
    

last_mode = -1  # Başlangıçta farklı olsun ki ilk seferde yazsın


while True:
    
    blynk.run()

    if current_mode != last_mode:
        if current_mode == 1:
            blynk.virtual_write(10, 'AI mode active' )
            set_mode_on_esp(ser, 2)
            run_ai_mode()
           
        elif current_mode == 2:
            blynk.virtual_write(10, 'Auto mode active' )
            set_mode_on_esp(ser, 1)
            run_auto_mode()
           
        elif current_mode == 3:
            blynk.virtual_write(10, 'Manual mode active' )
            set_mode_on_esp(ser, 0)
            run_manual_mode()
            
            
        else:
            print("Current mode:", current_mode)
        
        last_mode = current_mode
    
        

