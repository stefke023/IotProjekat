import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
import time
import threading
import json
import sys 
sys.path.append("..")
from ssdp import *
from udp import *

#---------------------------------------GLOBAL DEFINE-----------------------------------------

DANGEROUS_DUST_LEVEL = 20.0
SUSPICIOUS_DUST_LEVEL = 10.0
DANGEROUS_GAS_LEVEL = 30.0
SUSPICIOS_GAS_LEVEL = 15.0

ventilation_data = {"title" : "ON", "color" : "green"}
alarm_data = {"title" : "OFF", "color" : "green"}
dust_level_data = {"value" : 0,  "color" : "green"}
gas_level_data  = {"value" : 0, "color" : "green"}


PORT = 1883

GAS_STYLE = "gas.Horizontal.TProgressbar"
DUST_STYLE = "dust.Horizontal.TProgressbar"
VENTILATION_POS = 80
ALARM_POS = 230

canvas = None
gas_level_bar = None
dust_level_bar = None
style = None
root = None

THEME_SYSTEM = "sistem/status/obavestenje"


#--------------------------------------UI FUNCTIONS---------------------------------------
def update_ui():
    global root
    make_circle(ventilation_data["color"], ventilation_data["title"], VENTILATION_POS)
    make_circle(alarm_data["color"], alarm_data["title"], ALARM_POS)
    
    fill_progress_bar(dust_level_bar, dust_level_data["color"], dust_level_data["value"], DUST_STYLE)
    fill_progress_bar(gas_level_bar, gas_level_data["color"], gas_level_data["value"], GAS_STYLE)
    
    root.after(500, update_ui)

def make_circle(color, title, pos):
    global canvas
    canvas.create_oval(pos - 30, 20, pos + 30, 80, fill=color)
    canvas.create_text(pos, 50, text=title, fill="white", font=("Arial", 12, "bold"))
    
def fill_progress_bar(progress_bar, color, value, style_name):
    global style
    progress_bar["value"] = value
    style.configure(style_name, foreground=color, background=color)
    
def configure_screen():
    global canvas, gas_level_bar, dust_level_bar,  style, root
    
    root = tk.Tk()
    root.title("Monitoring sistema")
    root.geometry("500x300")
    root.configure(bg="white")

    label_gas = tk.Label(root, text="Nivo štetnih gasova:", bg="white", font=("Arial", 10))
    label_gas.pack(anchor="w", padx=20, pady=(20, 5))

    style = ttk.Style()
    style.theme_use('default')
    style.configure(GAS_STYLE, foreground='red', background='red')
    style.configure(DUST_STYLE, foreground='yellow', background='yellow')
    
    gas_level_bar = ttk.Progressbar(root, style = GAS_STYLE, length=400, maximum=50)
    gas_level_bar.pack(padx=20)

    label_dust = tk.Label(root, text="Nivo prašine:", bg="white", font=("Arial", 10))
    label_dust.pack(anchor="w", padx=20, pady=(20, 5))

    dust_level_bar = ttk.Progressbar(root, style = DUST_STYLE, length=400, maximum=40)
    dust_level_bar.pack(padx=20)

    canvas = tk.Canvas(root, width=400, height=120, bg="white", highlightthickness=0)
    canvas.pack(pady=20)
    
    canvas.create_text(80, 100, text="Ventilacija", font=("Arial", 10))
    canvas.create_text(230, 100, text="Alarm", font=("Arial", 10))

#----------------------------MQTT FUNCTIONS-------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Aktuator alarm: Povezan na MQTT Broker.")
    else:
        print(f"Greška pri povezivanju sa kodom: {rc}")
        return 
    
    client.subscribe(THEME_SYSTEM)
    print(f"Pretplacen na temu: {THEME_SYSTEM}")
    
def on_message(client, userdata, msg):
    try: 
        json_message = msg.payload.decode('utf-8')
        data = json.loads(json_message)
        
        alarm_active = data.get("alarm aktivan")
        ventilation_active = data.get("ventilation aktivan")
        dust_level = data.get("nivo prasine")
        gas_level = data.get("nivo opasnih gasova")
        
        
        
        if alarm_active: 
            alarm_data["color"] = "green"
            alarm_data["title"] = "ON"
        else: 
            alarm_data["color"] = "red"
            alarm_data["title"] = "OFF"
            
        if ventilation_active:
            ventilation_data["color"] = "green"
            ventilation_data["title"] = "ON"
        else:
            ventilation_data["color"] = "red"
            ventilation_data["title"] = "OFF" 
        
        dust_level_data["value"] = dust_level
        gas_level_data["value"] = gas_level
        
        if dust_level > DANGEROUS_DUST_LEVEL:
            dust_level_data["color"] = "red"
        elif dust_level > SUSPICIOUS_DUST_LEVEL:
            dust_level_data["color"] = "yellow"
        else:
            dust_level_data["color"] = "green"
            
        if gas_level > DANGEROUS_GAS_LEVEL:
            gas_level_data["color"] = "red"
        elif gas_level > SUSPICIOS_GAS_LEVEL:
            gas_level_data["color"] = "yellow"
        else:
            gas_level_data["color"] = "green"
        
    except json.JSONDecodeError:
        print(" Greška u parsiranju JSON poruke.")
        return
    except Exception as e:
        print(f"Došlo je do neočekivane greške: {e}")
        return


def mqtt_thread():
    s = "urn:iot_projekat:device:gui:1"
    u = f"uuid:41b96678-08b9-4f7b-82a7-d6c09919095f::{s}"
    ssdp_client = SSDP(st = s, usn = u)
    
    broker_address = ssdp_client.serve()
    
    if broker_address == 0:
        print("Nije nam se javio")
        return 
    
    if not get_activation_information(): 
        print("Nisu svi uredjaji u sistemu. Pozovite administratora.")
        return
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_address, PORT, 120)
    client.loop_forever()
    


if __name__ == "__main__":
    configure_screen()
    update_ui()
    threading.Thread(target=mqtt_thread, daemon=True).start()
    
    root.mainloop()
    