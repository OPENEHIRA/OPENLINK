"""
kinematics_visualizer.py - Web-compatible SVG visualization
for 2DOF robot arm using kinematics module.
Contributed by Emmanuel Olutunmibi
"""

import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from kinematics import inverse_kinematics, forward_kinematics

# Arm segment lengths
L1 = 150  # pixels
L2 = 100  # pixels

def generate_arm_svg(target_x, target_y, width=400, height=400):
    """
    Generate SVG showing robot arm reaching target position.
    
    Args:
        target_x: Target x in pixels (relative to center)
        target_y: Target y in pixels (relative to center)
        width: SVG width
        height: SVG height
    
    Returns:
        SVG string to embed in webpage
    """
    cx = width // 2
    cy = height // 2

    # Scale target to arm units
    scale = L1 / 150
    tx = target_x * scale
    ty = target_y * scale

    theta1, theta2 = inverse_kinematics(tx, ty, L1, L2)

    if theta1 is None:
        return f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
          <rect width="100%" height="100%" fill="#1a1a1a"/>
          <text x="{cx}" y="{cy}" fill="red" text-anchor="middle">
            Target unreachable
          </text>
        </svg>
        """

    t1 = math.radians(theta1)
    t2 = math.radians(theta2)

    # Joint positions
    x1 = cx + L1 * math.cos(t1)
    y1 = cy - L1 * math.sin(t1)
    x2 = x1 + L2 * math.cos(t1 + t2)
    y2 = y1 - L2 * math.sin(t1 + t2)

    svg = f"""
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#1a1a1a"/>
      <line x1="{cx}" y1="0" x2="{cx}" y2="{height}"
            stroke="#333" stroke-width="1"/>
      <line x1="0" y1="{cy}" x2="{width}" y2="{cy}"
            stroke="#333" stroke-width="1"/>
      <line x1="{cx}" y1="{cy}" x2="{x1:.1f}" y2="{y1:.1f}"
            stroke="#00ff88" stroke-width="6" stroke-linecap="round"/>
      <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"
            stroke="#00ccff" stroke-width="4" stroke-linecap="round"/>
      <circle cx="{cx}" cy="{cy}" r="8" fill="#ffffff"/>
      <circle cx="{x1:.1f}" cy="{y1:.1f}" r="6" fill="#ffff00"/>
      <circle cx="{x2:.1f}" cy="{y2:.1f}" r="5" fill="#ff4444"/>
      <text x="10" y="20" fill="#aaaaaa" font-size="12">
        J1: {theta1:.1f}°  J2: {theta2:.1f}°
      </text>
      <text x="10" y="40" fill="#aaaaaa" font-size="12">
        Target: ({target_x}, {target_y})
      </text>
    </svg>
    """
    return svg


if __name__ == "__main__":
    svg = generate_arm_svg(100, 50)
    with open("arm_preview.svg", "w") as f:
        f.write(svg)
    print("SVG saved to arm_preview.svg")
