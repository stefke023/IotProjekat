import paho.mqtt.client as mqtt
import json
from enum import Enum
import sys
import re
sys.path.append("..")
from ssdp import *
from udp import *

#----------------------------------GLOBAL DEFINE------------------------------

DEVICES_USN = ["uuid:8130ef32-2e70-4869-998f-bc1edec96316::urn:iot_projekat:device:sensors:1", "uuid:1f3548e2-442f-4fe3-8d65-49b78c48c3ea::urn:iot_projekat:device:sensors:1",
               "uuid:a50acac6-9c29-48dd-b819-1be6f46769c2::urn:iot_projekat:device:actuators:1", "uuid:bb3ff8b2-2719-4be4-9609-cf819bc95c4a::urn:iot_projekat:device:actuators:1",
               "uuid:41b96678-08b9-4f7b-82a7-d6c09919095f::urn:iot_projekat:device:gui:1"]

DANGEROUS_DUST_LEVEL = 20.0
SUSPICIOUS_DUST_LEVEL = 10.0
DANGEROUS_GAS_LEVEL = 30.0
SUSPICIOS_GAS_LEVEL = 15.0


broker_address = "127.0.0.1" 
port = 1883

dust_level = 0
gas_level = 0

THEME_GAS = "senzori/gas/nivo"
THEME_DUST = "senzori/prasina/nivo"
THEME_VENTILATION = "aktuatori/ventilacija/aktivacija"
THEME_ALARM = "aktuatori/alarm/aktivacija"
THEME_SYSTEM = "sistem/status/obavestenje"


ACTIVATION_ON = {
    "aktiviraj": True
}

ACTIVATION_OFF = {
    "aktiviraj" : False
}

system_info = {
    "ventilation aktivan" : False, 
    "alarm aktivan": False,
    "nivo prasine" : 0, 
    "nivo opasnih gasova" : 0
}


#----------------------------------MQTT FUNCTIONS------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Centralni kontroler: Povezan na MQTT Broker.")
    else:
        print(f"Greška pri povezivanju sa kodom: {rc}")
        return 
    
    client.subscribe(THEME_GAS)
    print(f"Pretplacen na temu: {THEME_GAS}")
    client.subscribe(THEME_DUST)
    print(f"Pretplacen na temu: {THEME_DUST}")


def on_message(client, userdata, msg):
    global dust_level, gas_level, system_info
    try:
        json_message = msg.payload.decode('utf-8')
        data = json.loads(json_message)
    
        if msg.topic == THEME_DUST: 
            dust_level = data.get("nivo prasine")
        
        elif msg.topic == THEME_GAS:
            gas_level = data.get("nivo opasnih gasova")
        
    except json.JSONDecodeError:
        print(" Greška u parsiranju JSON poruke.")
        return
    except Exception as e:
        print(f"Došlo je do neočekivane greške: {e}")
        return
    
    json_message_activate = json.dumps(ACTIVATION_ON)
    json_message_deactivate = json.dumps(ACTIVATION_OFF)
    ventilation_active = False 
    alarm_active = False
    
    if dust_level > DANGEROUS_DUST_LEVEL or gas_level > DANGEROUS_GAS_LEVEL:
        print("Moramo aktivirati i alarm i ventilaciju")
        ventilation_active = True
        alarm_active = True
        client.publish(THEME_ALARM, json_message_activate)
        client.publish(THEME_VENTILATION, json_message_activate)
    
    elif dust_level > SUSPICIOUS_DUST_LEVEL or gas_level > SUSPICIOS_GAS_LEVEL:
        print("Aktiviramo samo ventilaciju")
        ventilation_active = True
        client.publish(THEME_ALARM, json_message_deactivate)
        client.publish(THEME_VENTILATION, json_message_activate)
        
    else:
        print("Ne aktiviramo nista")
        client.publish(THEME_ALARM, json_message_deactivate)
        client.publish(THEME_VENTILATION, json_message_deactivate)
        
    system_info["alarm aktivan"] = alarm_active
    system_info["ventilation aktivan"] = ventilation_active
    system_info["nivo opasnih gasova"] = gas_level
    system_info["nivo prasine"] = dust_level
    
    json_message_system = json.dumps(system_info)
    client.publish(THEME_SYSTEM, json_message_system)
        
def main(): 
    ssdp_host = SSDP()
    
    responses = []
    devices = []
    
    responses.extend(ssdp_host.discover(st = "urn:iot_projekat:device:sensors:1"))
    responses.extend(ssdp_host.discover(st = "urn:iot_projekat:device:actuators:1"))
    responses.extend(ssdp_host.discover(st = "urn:iot_projekat:device:gui:1"))
    
    for response in responses:
        match = re.search(r"USN:\s*(.+)", response)
        if match:
            matched_string = match.group(1)
            if matched_string not in devices:
                devices.append(matched_string[:-1])
    
    all_connected = True
    for usn in DEVICES_USN: 
        if usn not in devices:
            all_connected = False
            break
    
    if not all_connected:
        print("Nemamo sve potrebne elemente za nas sistem. Proverite konekcije.")
        send_activation_information("System ready: FALSE")
        return 

    send_activation_information("System ready: TRUE")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_address, port, 60)
    client.loop_forever()
        
if __name__ == "__main__":
    main()