import paho.mqtt.client as mqtt
import json
import time
import os
import sys
sys.path.append(".")
from ssdp import *
from udp import *

# MQTT podešavanja
TOPIC_MOISTURE = "sensors/soil/moisture"
DATA_FILE = "moisture_level.txt"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Senzor nivoa vlaznosti: Povezan na MQTT Broker.")
    else:
        print(f"Greška pri povezivanju sa kodom: {rc}")

def send_data_from_file(client, data_file, topic):
    curr_dir = os.getcwd() + "/Publisher/" 
    data_path = os.path.join(curr_dir, data_file)
    try:
        with open(data_path, 'r') as f:
            for line in f:
                try:
                    moisture_level = float(line.strip())
                    data = {
                        "nivo vlaznosti": moisture_level
                    }
                    json_message = json.dumps(data)
                    client.publish(topic, json_message)
                    print(f"Poslao poruku na temu '{topic}': {json_message}")
                    time.sleep(15)
                
                except ValueError:
                    print(f"Preskačem nevalidnu liniju: '{line.strip()}'")
                    continue

    except FileNotFoundError:
        print(f"Greška: Fajl '{data_path}' nije pronađen.")
    except Exception as e:
        print(f"Došlo je do neočekivane greške: {e}")

def main():
    s = "urn:iot_projekat:device:sensors:1"
    u = f"uuid:7c2f4b91-9e6a-4f4e-b0c8-2d8a7e3b9c14::{s}"
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

    try:
        client.connect(broker_address, PORT, 60)
    except Exception as e:
        print(f"Greška pri povezivanju na broker: {e}")
        return

    client.loop_start()

    send_data_from_file(client, DATA_FILE, TOPIC_MOISTURE)

    client.loop_stop()
    client.disconnect()
    print("Završeno slanje svih podataka iz fajla.")

if __name__ == "__main__":
    main()
