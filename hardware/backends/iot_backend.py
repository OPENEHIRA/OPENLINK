"""
iot_backend.py — IoT device backend.

STATUS: PLACEHOLDER — Soumyadeep fills in the TODOs based on their hardware.

To activate: set "backend": "iot" in hardware.json

Soumyadeep's job:
  - Pick protocol: "serial" (USB cable) or "mqtt" (WiFi)
  - Fill in the connect() and execute() TODOs below
  - Update hardware.json with device port/IP
"""

from typing import Optional, Dict, Any
from hardware.base import HardwareBackend


class IoTBackend(HardwareBackend):

    def __init__(self, protocol: str = "serial", port: str = "COM3", baud: int = 115200,
                 mqtt_host: str = "localhost", mqtt_port: int = 1883, mqtt_topic: str = "openguy/command"):
        self._protocol = protocol
        self._port = port
        self._baud = baud
        self._mqtt_host = mqtt_host
        self._mqtt_port = mqtt_port
        self._mqtt_topic = mqtt_topic
        self._connection = None

    def connect(self) -> bool:
        if self._protocol == "serial":
            # TODO Soumyadeep: pip install pyserial, then:
            # import serial
            # self._connection = serial.Serial(self._port, self._baud, timeout=1)
            # return self._connection.is_open
            pass

        elif self._protocol == "mqtt":
            # TODO Soumyadeep: pip install paho-mqtt, then:
            # import paho.mqtt.client as mqtt
            # self._connection = mqtt.Client()
            # self._connection.connect(self._mqtt_host, self._mqtt_port)
            # self._connection.loop_start()
            # return True
            pass

    def disconnect(self) -> None:
        # TODO Soumyadeep:
        # if self._connection:
        #     self._connection.close()  # serial
        #     self._connection.disconnect()  # mqtt
        pass

    def execute(
        self,
        action: str,
        direction: Optional[str] = None,
        distance_cm: Optional[float] = None,
        angle_deg: Optional[float] = None,
    ) -> Dict[str, Any]:
        # Message to send to the device
        # TODO Soumyadeep: adjust this format to match your device's firmware
        message = {
            "action": action,
            "direction": direction or "",
            "distance_cm": distance_cm or 0.0,
            "angle_deg": angle_deg or 0.0,
        }

        if self._protocol == "serial":
            # TODO Soumyadeep:
            # import json
            # self._connection.write((json.dumps(message) + "\n").encode("utf-8"))
            pass

        elif self._protocol == "mqtt":
            # TODO Soumyadeep:
            # import json
            # self._connection.publish(self._mqtt_topic, json.dumps(message))
            pass

    def get_status(self) -> Dict[str, Any]:
        # TODO Soumyadeep: read real position/state from device if it sends feedback
        # For now return empty — fill in when device sends data back
        return {
            "backend": "iot",
            "protocol": self._protocol,
        }

    def is_connected(self) -> bool:
        # TODO Soumyadeep: return self._connection.is_open  (serial)
        #                   return self._connection.is_connected()  (mqtt)
        return False

    def reset(self) -> None:
        # TODO Soumyadeep: send a reset command to the device if it supports one
        pass

    @property
    def name(self) -> str:
        return f"iot_{self._protocol}"
