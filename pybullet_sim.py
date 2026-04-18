"""
pybullet_sim.py - PyBullet physics simulation for 2DOF robot arm.
Integrates with kinematics module for joint control.
Contributed by Emmanuel Olutunmibi
"""

import pybullet as p
import pybullet_data
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from kinematics import inverse_kinematics

# Arm segment lengths in meters
L1 = 0.15
L2 = 0.10

def create_arm(physics_client):
    """Create a simple 2DOF robot arm in PyBullet."""
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.loadURDF("plane.urdf")
    p.setGravity(0, 0, -9.81)

    # Base
    base = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.05, 0.05, 0.05])
    base_id = p.createMultiBody(0, base, -1, [0, 0, 0.05])

    # Link 1
    link1 = p.createCollisionShape(p.GEOM_BOX, halfExtents=[L1/2, 0.02, 0.02])
    link1_id = p.createMultiBody(0.5, link1, -1, [L1/2, 0, 0.15])

    # Link 2
    link2 = p.createCollisionShape(p.GEOM_BOX, halfExtents=[L2/2, 0.02, 0.02])
    link2_id = p.createMultiBody(0.3, link2, -1, [L1 + L2/2, 0, 0.15])

    return base_id, link1_id, link2_id

def simulate(target_x, target_y, steps=500, use_gui=False):
    """
    Simulate arm moving to target position.
    
    Args:
        target_x: Target x position in meters
        target_y: Target y position in meters
        steps: Simulation steps
        use_gui: Show PyBullet GUI (requires display)
    """
    mode = p.GUI if use_gui else p.DIRECT
    client = p.connect(mode)

    try:
        create_arm(client)

        theta1, theta2 = inverse_kinematics(
            target_x, target_y, L1, L2
        )

        if theta1 is None:
            print(f"Target ({target_x}, {target_y}) is unreachable.")
            return None

        print(f"Target: ({target_x}, {target_y})")
        print(f"Joint 1: {theta1:.2f} degrees")
        print(f"Joint 2: {theta2:.2f} degrees")

        for _ in range(steps):
            p.stepSimulation()
            if use_gui:
                time.sleep(1.0 / 240.0)

        print("Simulation complete.")
        return theta1, theta2

    finally:
        p.disconnect(client)

if __name__ == "__main__":
    print("OpenGuy PyBullet Simulation")
    print("Testing arm movement to (0.15, 0.10)...")
    simulate(0.15, 0.10)

    print("\nTesting arm movement to (0.20, 0.05)...")
    simulate(0.20, 0.05)

    print("\nTesting unreachable position (1.0, 1.0)...")
    simulate(1.0, 1.0)
