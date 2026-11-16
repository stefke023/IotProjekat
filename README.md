# IoT Construction Site Safety System

IoT simulation of a construction-site safety system in Python.

## How it works

- Sensors (rain, soil moisture, lightning) publish readings over MQTT.
- A central controller evaluates the readings and decides when to trigger the
  actuators (alarm, ventilation, zone lock); a Tkinter GUI shows the system status.
- Devices are discovered with SSDP (multicast `239.255.255.250:1900`). Once all
  expected devices respond, the controller sends a UDP multicast "System ready"
  message (`239.1.1.1:5007`) that starts the system.
- Devices keep advertising over SSDP; if one disappears, the controller publishes
  a shutdown message and all components exit.

## Tech

Python 3, paho-mqtt, Mosquitto, sockets (UDP multicast), Tkinter.

## Run

1. Install Mosquitto and start it on port 1883 on the controller's machine
   (devices connect to the broker at the controller's IP address).
2. `pip install -r requirements.txt`
3. From the repo root, in separate terminals, start the devices first and the
   controller last (within 120 seconds, while the devices wait for discovery):

   ```
   python launcher.py publisher
   python launcher.py subscriber
   python launcher.py host
   ```

Sensor readings are read from the text files in `Publisher/`.
