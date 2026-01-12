import paho.mqtt.client as mqtt
import json
from enum import Enum
import sys
import re
sys.path.append(".")
from ssdp import *
from udp import *
import threading
import os

#----------------------------------GLOBAL DEFINE------------------------------

DEVICES_USN = ["uuid:8130ef32-2e70-4869-998f-bc1edec96316::urn:iot_projekat:device:sensors:1", "uuid:1f3548e2-442f-4fe3-8d65-49b78c48c3ea::urn:iot_projekat:device:sensors:1",
               "uuid:a50acac6-9c29-48dd-b819-1be6f46769c2::urn:iot_projekat:device:actuators:1", "uuid:bb3ff8b2-2719-4be4-9609-cf819bc95c4a::urn:iot_projekat:device:actuators:1",
               "uuid:41b96678-08b9-4f7b-82a7-d6c09919095f::urn:iot_projekat:device:gui:1",  "uuid:7c2f4b91-9e6a-4f4e-b0c8-2d8a7e3b9c14::urn:iot_projekat:device:sensors:1",
               "uuid:d94a1f6e-3e21-4c67-8c6f-5e0b2d91a8f3::urn:iot_projekat:device:actuators:1"]

DANGEROUS_MOISTURE_LEVEL = 80.0
DANGEROUS_RAIN_LEVEL = 50.0

broker_address = "127.0.0.1" 
port = 1883

moisture_level = 0
rain_level = 0
is_lighting = ""

TOPIC_LIGHTNING = "sensors/lightning/event"
TOPIC_MOISTURE = "sensors/soil/moisture"
TOPIC_RAIN = "sensors/weather/rain"
TOPIC_ALARM = "actuators/alarm/commands"
TOPIC_LOCK = "actuators/zone/lock"
TOPIC_VENTILATION = "actuators/ventilation/commands"
TOPIC_SYSTEM = "system/status/info"
TOPIC_SHUTDOWN = "system/shutdown"


ACTIVATION_ON = {
    "aktiviraj": True
}

ACTIVATION_OFF = {
    "aktiviraj" : False
}


SHUTDOWN = {
    "ugasi se" : True
}

system_info = {
    "ventilation aktivan" : False, 
    "alarm aktivan": False,
    "zona zakljucana" : False, 
    "nivo vlaznosti" : 0, 
    "nivo kise" : 0,
    "udar groma" : False
}


#----------------------------------MQTT FUNCTIONS------------------------------#
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Centralni kontroler: Povezan na MQTT Broker.")
    else:
        print(f"Greška pri povezivanju sa kodom: {rc}")
        return 
    
    client.subscribe(TOPIC_LIGHTNING)
    print(f"Pretplacen na temu: {TOPIC_LIGHTNING}")
    client.subscribe(TOPIC_MOISTURE)
    print(f"Pretplacen na temu: {TOPIC_MOISTURE}")
    client.subscribe(TOPIC_RAIN)
    print(f"Pretplacen na temu: {TOPIC_RAIN}")

def on_message(client, userdata, msg):
    global moisture_level, is_lighting, rain_level , system_info
    try:
        json_message = msg.payload.decode('utf-8')
        data = json.loads(json_message)
    
        if msg.topic == TOPIC_LIGHTNING: 
            is_lighting = data.get("udar groma")
        
        elif msg.topic == TOPIC_MOISTURE:
            moisture_level = data.get("nivo vlaznosti")

        elif msg.topic == TOPIC_RAIN:
            rain_level = data.get("nivo kise")
        
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
    lock_active = False


    if is_lighting == "True": 
        print("Udario je grom. Aktiviramo alarm i zakljucavamo zonu.")
        lock_active = True
        alarm_active = True
        client.publish(TOPIC_LOCK, json_message_activate)
        client.publish(TOPIC_ALARM, json_message_activate)
        client.publish(TOPIC_VENTILATION, json_message_deactivate)
    
    elif moisture_level > DANGEROUS_MOISTURE_LEVEL:
        print("Previsoka vlaznost. Aktiviramo ventilaciju.")
        ventilation_active = True
        client.publish(TOPIC_LOCK, json_message_deactivate)
        client.publish(TOPIC_ALARM, json_message_deactivate)
        client.publish(TOPIC_VENTILATION, json_message_activate)
    
    elif rain_level > DANGEROUS_RAIN_LEVEL:
        print("Velika kolicina padavina. Aktiviramo alarm.")
        alarm_active = True
        client.publish(TOPIC_LOCK, json_message_deactivate)
        client.publish(TOPIC_ALARM, json_message_deactivate)
        client.publish(TOPIC_VENTILATION, json_message_activate)
        
    else:
        print("Ne aktiviramo nista")
        client.publish(TOPIC_ALARM, json_message_deactivate)
        client.publish(TOPIC_VENTILATION, json_message_deactivate)
        client.publish(TOPIC_LOCK, json_message_deactivate)
        
    system_info["alarm aktivan"] = alarm_active
    system_info["ventilation aktivan"] = ventilation_active
    system_info["zona zakljucana"] = lock_active
    system_info["udar groma"] = is_lighting
    system_info["nivo kise"] = rain_level
    system_info["nivo vlaznosti"] = moisture_level

    json_message_system = json.dumps(system_info)
    client.publish(TOPIC_SYSTEM, json_message_system)

def const_check(ssdp_host, client):
    end = False

    while not end:
        current_usn = ssdp_host.listen()

        for usn in DEVICES_USN:
            if usn not in current_usn:
                print("Nemamo sve potrebne elemente za nas sistem. Proverite konekcije.")
                json_shutdown = json.dumps(SHUTDOWN)
                client.publish(TOPIC_SHUTDOWN, json_shutdown)
                os._exit(1)
        
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
            print(usn)
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

    threading.Thread(target = const_check, args=(ssdp_host, client) , daemon=True).start()
    client.loop_forever()
        
if __name__ == "__main__":
    main()