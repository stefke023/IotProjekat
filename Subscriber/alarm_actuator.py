import paho.mqtt.client as mqtt
import json
import sys
sys.path.append(".")
from ssdp import *
from udp import *
import threading
import os

PORT = 1883
TOPIC_ALARM = "actuators/alarm/commands"
TOPIC_SHUTDOWN = "system/shutdown"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Aktuator alarm: Povezan na MQTT Broker.")
    else:
        print(f"Greška pri povezivanju sa kodom: {rc}")
        return 
    
    client.subscribe(TOPIC_ALARM)
    print(f"Pretplacen na temu: {TOPIC_ALARM}")
    client.subscribe(TOPIC_SHUTDOWN)

def on_message(client, userdata, msg):
    
    try: 
        json_message = msg.payload.decode('utf-8')
        data = json.loads(json_message)

        if msg.topic == TOPIC_SHUTDOWN: 
            print("Nisu svi uredjaji u sistemu. Pozovite administratora.")
            os._exit(1)
        
        alarm_active = data.get("aktiviraj")
        
        if alarm_active: 
            print("Alarm je aktivan. Napustite gradiliste.")
        else: 
            print("Alarm nije aktiviran. Mozete bezbedno nastaviti sa radom.")
        
    except json.JSONDecodeError:
        print(" Greška u parsiranju JSON poruke.")
        return
    except Exception as e:
        print(f"Došlo je do neočekivane greške: {e}")
        return

def main(): 
    s = "urn:iot_projekat:device:actuators:1"
    u = f"uuid:bb3ff8b2-2719-4be4-9609-cf819bc95c4a::{s}"
    ssdp_client = SSDP(st = s, usn = u)
    
    broker_address = ssdp_client.serve()
    
    if broker_address == 0:
        print("Nije nam se javio")
        return 

    if not get_activation_information(): 
        print("Nisu svi uredjaji u sistemu. Pozovite administratora.")
        return
    
    threading.Thread(target=ssdp_client.advertise, daemon=True).start()

    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_address, PORT, 60)
    client.loop_forever()
    
if __name__ == "__main__":
    main()