"""
ros_backend.py — ROS 2 backend via roslibpy.

STATUS: PLACEHOLDER — fill in TODOs after ROS meeting.

To activate: set "backend": "ros" in hardware.json
"""

from typing import Optional, Dict, Any
from hardware.base import HardwareBackend


class ROSBackend(HardwareBackend):

    def __init__(self, host: str = "localhost", port: int = 9090):
        self._host = host
        self._port = port
        self._client = None
        self._publisher = None

    def connect(self) -> bool:
        # TODO: install roslibpy → pip install roslibpy
        # TODO: get host IP and port from ROS person
        # self._client = roslibpy.Ros(host=self._host, port=self._port)
        # self._client.run()
        # self._publisher = roslibpy.Topic(self._client, "/openguy/command", "std_msgs/String")
        # return self._client.is_connected
        pass

    def disconnect(self) -> None:
        # TODO: self._client.terminate()
        pass

    def execute(
        self,
        action: str,
        direction: Optional[str] = None,
        distance_cm: Optional[float] = None,
        angle_deg: Optional[float] = None,
    ) -> Dict[str, Any]:
        # TODO: confirm message format with ROS person (see hardware/contracts/message_spec.md)
        # message = {
        #     "action": action,
        #     "direction": direction or "",
        #     "distance_cm": distance_cm or 0.0,
        #     "angle_deg": angle_deg or 0.0,
        # }
        # self._publisher.publish(roslibpy.Message({"data": json.dumps(message)}))
        pass

    def get_status(self) -> Dict[str, Any]:
        # TODO: subscribe to /openguy/status and return real robot position
        pass

    def is_connected(self) -> bool:
        # TODO: return self._client.is_connected
        return False

    def reset(self) -> None:
        # TODO: send reset command to robot
        pass

    @property
    def name(self) -> str:
        return "ros"
