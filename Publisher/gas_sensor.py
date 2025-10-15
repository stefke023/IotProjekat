import paho.mqtt.client as mqtt
import json
import time
import os
import sys
sys.path.append("..")
from ssdp import *
from udp import *

PORT = 1883
TOPIC_GAS = "senzori/gas/nivo"
DATA_FILE = "gas_level.txt"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Senzor opasnih gasova: Povezan na MQTT Broker.")
    else:
        print(f"Greška pri povezivanju sa kodom: {rc}")

def send_data_from_file(client, data_file, topic):
    curr_dir = os.getcwd()
    data_path = os.path.join(curr_dir, data_file)
    try:
        with open(data_path, 'r') as f:
            print(f"Čitam podatke iz fajla: {data_file}")
            for line in f:
                try:
                    gas_level = float(line.strip())
                    data = {
                        "nivo opasnih gasova": gas_level
                    }
                    json_message = json.dumps(data)
                    client.publish(topic, json_message)
                    print(f"Poslao poruku na temu '{topic}': {json_message}")
                    time.sleep(15)
                
                except ValueError:
                    print(f"Preskačem nevalidnu liniju: '{line.strip()}'")
                    continue

    except FileNotFoundError:
        print(f"Greška: Fajl '{data_file}' nije pronađen.")
    except Exception as e:
        print(f"Došlo je do neočekivane greške: {e}")

def main():
    s = "urn:iot_projekat:device:sensors:1"
    u = f"uuid:8130ef32-2e70-4869-998f-bc1edec96316::{s}"
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

    send_data_from_file(client, DATA_FILE, TOPIC_GAS)

    client.loop_stop()
    client.disconnect()
    print("Završeno slanje svih podataka iz fajla.")

if __name__ == "__main__":
    main()
