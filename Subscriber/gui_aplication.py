import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
import time
import threading
import json
import sys 
sys.path.append(".")
from ssdp import *
from udp import *
import os


#---------------------------------------GLOBAL DEFINE-----------------------------------------

ventilation_data = {"title" : "OFF", "color" : "red"}
alarm_data = {"title" : "OFF", "color" : "red"}
lock_data = {"title" : "OFF", "color" :  "red"}
moisture_level_data = {"value" : 0,  "color" : "red"}
rain_level_data  = {"value" : 0, "color" : "red"}
lightning_data = {"value" : 0, "color" : "red"}

PORT = 1883

DANGEROUS_MOISTURE_LEVEL = 80.0
DANGEROUS_RAIN_LEVEL = 50.0

RAIN_STYLE = "rain.Horizontal.TProgressbar"
MOISTURE_STYLE = "moisture.Horizontal.TProgressbar"
LIGHTNING_STYLE = "lightingn.Horizontal.TProgressbar"

VENTILATION_POS = 80
ALARM_POS = 230
LOCK_POS = 400

canvas = None
rain_level_bar = None
moisture_level_bar = None
lightning_bar = None
style = None
root = None

TOPIC_SYSTEM = "system/status/info"
TOPIC_SHUTDOWN = "system/shutdown"



#--------------------------------------UI FUNCTIONS---------------------------------------
def update_ui():
    global root
    make_circle(ventilation_data["color"], ventilation_data["title"], VENTILATION_POS)
    make_circle(alarm_data["color"], alarm_data["title"], ALARM_POS)
    make_circle(lock_data["color"], lock_data["title"], LOCK_POS)
    
    fill_progress_bar(moisture_level_bar, moisture_level_data["color"], moisture_level_data["value"], RAIN_STYLE)
    fill_progress_bar(rain_level_bar, rain_level_data["color"], rain_level_data["value"], MOISTURE_STYLE)
    fill_progress_bar(lightning_bar, lightning_data["color"], lightning_data["value"], MOISTURE_STYLE)
    
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
    global canvas, rain_level_bar, moisture_level_bar,  style, root, lightning_bar
    
    root = tk.Tk()
    root.title("Monitoring sistema")
    root.geometry("600x400")
    root.configure(bg="white")

    label_rain = tk.Label(root, text="Nivo kise: ", bg="white", font=("Arial", 10))
    label_rain.pack(anchor="w", padx=20, pady=(20, 5))

    style = ttk.Style()
    style.theme_use('default')
    style.configure(RAIN_STYLE, foreground='red', background='red')
    style.configure(MOISTURE_STYLE, foreground='yellow', background='yellow')
    style.configure(LIGHTNING_STYLE, foreground = 'red', background = 'red')
    
    rain_level_bar = ttk.Progressbar(root, style = RAIN_STYLE, length=600, maximum=100)
    rain_level_bar.pack(padx=20)

    label_moisture = tk.Label(root, text="Nivo vlaznosti: ", bg="white", font=("Arial", 10))
    label_moisture.pack(anchor="w", padx=20, pady=(20, 5))

    moisture_level_bar = ttk.Progressbar(root, style = MOISTURE_STYLE, length=600, maximum=100)
    moisture_level_bar.pack(padx=20)

    label_lighting = tk.Label(root, text="Udar groma: ", bg="white", font=("Arial", 10))
    label_lighting.pack(anchor="w", padx=20, pady=(20, 5))

    lightning_bar = ttk.Progressbar(root, style = LIGHTNING_STYLE, length=600, maximum=100)
    lightning_bar.pack(padx=20)

    canvas = tk.Canvas(root, width=600, height=120, bg="white", highlightthickness=0)
    canvas.pack(pady=20)
    
    canvas.create_text(80, 100, text="Ventilacija", font=("Arial", 10))
    canvas.create_text(230, 100, text="Alarm", font=("Arial", 10))
    canvas.create_text(400, 100, text="Zakljucan", font=("Arial", 10))


#----------------------------MQTT FUNCTIONS-------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Aktuator alarm: Povezan na MQTT Broker.")
    else:
        print(f"Greška pri povezivanju sa kodom: {rc}")
        return 
    
    client.subscribe(TOPIC_SYSTEM)
    print(f"Pretplacen na temu: {TOPIC_SYSTEM}")
    client.subscribe(TOPIC_SHUTDOWN)
    
def on_message(client, userdata, msg):
    try: 
        json_message = msg.payload.decode('utf-8')
        data = json.loads(json_message)

        if msg.topic == TOPIC_SHUTDOWN: 
            print("Nisu svi uredjaji u sistemu. Pozovite administratora.")
            os._exit(1)
        
        alarm_active = data.get("alarm aktivan")
        ventilation_active = data.get("ventilation aktivan")
        lock_active = data.get("zona zakljucana")
        moisture_level = data.get("nivo vlaznosti")
        rain_level = data.get("nivo kise")
        is_lightning = data.get("udar groma")
        
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

        if lock_active:
            lock_data["color"] = "green"
            lock_data["title"] = "ON"
        else:
            lock_data["color"] = "red"
            lock_data["title"] = "OFF"
        
        moisture_level_data["value"] = moisture_level
        rain_level_data["value"] = rain_level

        if is_lightning == "True":
            lightning_data["value"] = 100
            lightning_data["color"] = "red"
        else:
            lightning_data["value"] = 0
            lightning_data["color"] = "green"

        if moisture_level > DANGEROUS_MOISTURE_LEVEL:
            moisture_level_data["color"] = "red"
        else:
            moisture_level_data["color"] = "green"
            
        if rain_level > DANGEROUS_RAIN_LEVEL:
            rain_level_data["color"] = "red"
        else:
            rain_level_data["color"] = "green"
        
        
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
        print("Na pocetnoj proveri nemamo sve potrebne elemente za nas sistem. Proverite konekcije.")
        os._exit(1)
    
    threading.Thread(target=ssdp_client.advertise, daemon=True).start()
    
    
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
    