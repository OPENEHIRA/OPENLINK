"""
hardware/base.py — The contract every hardware backend must follow.

Think of this as a checklist. Any backend (simulator, ROS, IoT) that wants
to work with OpenGuy must implement ALL of these methods with the same
inputs and outputs. This is what lets app.py swap backends without caring
which one is active.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class HardwareBackend(ABC):
    """
    Abstract base class for all hardware backends.

    Every backend (SimulatorBackend, ROSBackend, IoTBackend) must
    inherit from this class and implement every method below.
    """

    @abstractmethod
    def connect(self) -> bool:
        """
        Open the connection to the hardware.

        For simulator: nothing to connect, always returns True.
        For ROS: opens WebSocket to rosbridge server.
        For IoT: opens serial port or MQTT connection.

        Returns:
            True if connected successfully, False otherwise.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the connection cleanly.

        Always call this on shutdown to avoid leaving open ports or sockets.
        """
        ...

    @abstractmethod
    def execute(
        self,
        action: str,
        direction: Optional[str] = None,
        distance_cm: Optional[float] = None,
        angle_deg: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute one robot command.

        Args:
            action:      "move" | "rotate" | "grab" | "release" | "stop"
            direction:   "forward" | "backward" | "left" | "right" (for move/rotate)
            distance_cm: how far to move in centimetres (for move)
            angle_deg:   how many degrees to rotate (for rotate)

        Returns:
            Dict with at least {"success": True/False, "status": "..."}
            May also include "movement", "rotation", "gripper" keys.

        Raises:
            ValueError: if action or parameters are invalid
        """
        ...

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Return the current state of the robot.

        Returns:
            Dict with at least: x, y, facing, gripper_open, commands_executed
        """
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the backend is ready to receive commands.

        Returns:
            True if connected and ready, False otherwise.
        """
        ...

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the robot to its initial state.

        For simulator: resets x=0, y=0, facing=0, gripper open.
        For ROS/IoT: sends a reset command to the hardware.
        """
        ...

    @property
    def name(self) -> str:
        """Human-readable name of this backend. Used in logs and /api/health."""
        return self.__class__.__name__
