# IotProjekat
A simulation of an IoT (Internet of Things) system built in Python using multiple terminal instances to represent networked devices.

Overview
The project simulates how IoT devices discover and communicate with each other over a network. It demonstrates the process of device discovery and message exchange using real networking protocols.

Features
- SSDP (Simple Service Discovery Protocol) used for device discovery and initial network connection.
- MQTT (Message Queuing Telemetry Transport) protocol used for efficient, lightweight device communication.
- Simulates multiple IoT devices communicating via separate Python terminals.
- Includes logging of device activity and message flow for debugging and visualization.
- Uses a Makefile to easily start all components (devices and central controller) with a single command.

Technologies Used
- Python
- SSDP protocol
- MQTT protocol (via paho-mqtt library)
- Multi-terminal simulation
- Makefile for process automation

How It Works
Devices announce their presence using SSDP to connect to the network.
Once discovered, they subscribe and publish to MQTT topics to exchange data.
The simulation shows a basic IoT network workflow: discovery → connection → communication.
