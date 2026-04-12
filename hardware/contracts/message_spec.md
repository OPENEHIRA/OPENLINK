# OpenGuy ↔ ROS / C++ Message Contract

This document is the handshake between OpenGuy (Python) and the C++ ROS node.
Both sides must agree on everything here before integration can work.

**Status:** DRAFT — confirm with ROS team before implementation.

---

## 1. ROS Setup Required (ROS Team's Job)

```bash
# Install and run rosbridge on the robot's machine
sudo apt install ros-<distro>-rosbridge-server
ros2 run rosbridge_server rosbridge_websocket
# Runs on ws://localhost:9090 by default
```

---

## 2. Command Topic (OpenGuy → Robot)

**Topic name:** `/openguy/command`
**Direction:** OpenGuy publishes, C++ node subscribes
**Proposed message type:** `std_msgs/String` (JSON string payload)

> NOTE: Confirm message type with ROS team. May switch to a custom msg type.

### Payload format (JSON inside the String):

```json
{
  "action":      "move",
  "direction":   "forward",
  "distance_cm": 10.0,
  "angle_deg":   0.0,
  "sequence_id": 42
}
```

### Field definitions:

| Field         | Type    | Values                                          | Notes                          |
|---------------|---------|--------------------------------------------------|-------------------------------|
| `action`      | string  | `move`, `rotate`, `grab`, `release`, `stop`     | always present                |
| `direction`   | string  | `forward`, `backward`, `left`, `right`          | required for move and rotate  |
| `distance_cm` | float   | 0.0 – 100.0                                     | required for move             |
| `angle_deg`   | float   | 0.0 – 360.0                                     | required for rotate           |
| `sequence_id` | integer | 1, 2, 3, ...                                    | monotonically increasing      |

### Example messages per action:

**Move forward 10cm:**
```json
{"action": "move", "direction": "forward", "distance_cm": 10.0, "angle_deg": 0.0, "sequence_id": 1}
```

**Rotate right 90°:**
```json
{"action": "rotate", "direction": "right", "distance_cm": 0.0, "angle_deg": 90.0, "sequence_id": 2}
```

**Grab:**
```json
{"action": "grab", "direction": "", "distance_cm": 0.0, "angle_deg": 0.0, "sequence_id": 3}
```

**Release:**
```json
{"action": "release", "direction": "", "distance_cm": 0.0, "angle_deg": 0.0, "sequence_id": 4}
```

**Stop:**
```json
{"action": "stop", "direction": "", "distance_cm": 0.0, "angle_deg": 0.0, "sequence_id": 5}
```

---

## 3. Status Topic (Robot → OpenGuy)

**Topic name:** `/openguy/status`
**Direction:** C++ node publishes, OpenGuy subscribes
**Proposed message type:** `std_msgs/String` (JSON string payload)

> NOTE: Optional for Phase 1. Required for Phase 2 (real feedback).

### Payload format:

```json
{
  "x":            12.5,
  "y":            -3.0,
  "facing":       90.0,
  "gripper_open": false,
  "sequence_ack": 3,
  "success":      true,
  "error":        ""
}
```

### Field definitions:

| Field          | Type    | Notes                                              |
|----------------|---------|----------------------------------------------------|
| `x`            | float   | Current X position in cm                          |
| `y`            | float   | Current Y position in cm                          |
| `facing`       | float   | Current facing angle in degrees                   |
| `gripper_open` | bool    | True = open, False = closed                       |
| `sequence_ack` | integer | Echo of the `sequence_id` from the command         |
| `success`      | bool    | True if command executed without error            |
| `error`        | string  | Error message if success=false, else empty string |

---

## 4. Integration Checklist

### OpenGuy Side (Python team):
- [ ] roslibpy installed (`pip install roslibpy`)
- [ ] ROSBackend.connect() wired with correct host/port
- [ ] ROSBackend.execute() publishes real roslibpy message
- [ ] ROSBackend subscribes to `/openguy/status` for feedback
- [ ] hardware.json updated: `"backend": "ros"`, correct host IP

### ROS Side (C++ team):
- [ ] rosbridge server running on robot machine
- [ ] C++ node subscribes to `/openguy/command`
- [ ] C++ node parses JSON payload from the String message
- [ ] C++ node executes the correct motor commands
- [ ] C++ node publishes real position to `/openguy/status`
- [ ] Tested with a dummy Python publisher before OpenGuy integration

---

## 5. Testing Without Full Integration

### Test 1 — Dummy subscriber (ROS team verifies messages arrive)
```bash
ros2 topic echo /openguy/command
```
Then send a command from OpenGuy UI. Message should appear in the terminal.

### Test 2 — Dummy publisher (OpenGuy team verifies status parsing)
```bash
ros2 topic pub /openguy/status std_msgs/String \
  '{"data": "{\"x\": 5.0, \"y\": 0.0, \"facing\": 90.0, \"gripper_open\": true, \"sequence_ack\": 1, \"success\": true, \"error\": \"\"}"}'
```
OpenGuy should update its displayed position.

---

## 6. Open Questions (Discuss at Meeting)

- [ ] Should we use `std_msgs/String` or define a custom ROS message type?
- [ ] What is the rosbridge server IP when running on separate machines?
- [ ] What coordinate system does the physical robot use? (match with OpenGuy's x/y)
- [ ] What are the real physical limits (max distance, max angle) for this robot?
- [ ] Does the robot need a homing/calibration command before operation?
- [ ] How does the C++ node handle an unknown/invalid action?
