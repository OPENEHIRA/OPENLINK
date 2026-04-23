# OpenGuy - ROS2 + Gazebo + Flask
# Base image with ROS2 Humble
FROM ros:humble-ros-base-jammy

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-rclpy \
    ros-humble-geometry-msgs \
    ros-humble-control-msgs \
    ros-humble-rosbridge-server \
    gazebo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install gz-web
RUN pip3 install gz-web || echo "gz-web install attempted"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p robot_notes robot_learning

# Expose ports
# 5000 - Flask app
# 9090 - rosbridge WebSocket
# 9091 - gz-web
EXPOSE 5000 9090 9091

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV ROS_DOMAIN_ID=0

# Startup script
RUN echo '#!/bin/bash\n\
source /opt/ros/humble/setup.bash\n\
# Start rosbridge\n\
ros2 launch rosbridge_server rosbridge_websocket_launch.xml &\n\
# Start gz-web\n\
python3 -m gz.web --port 9091 &\n\
# Start Flask\n\
gunicorn --bind 0.0.0.0:5000 --timeout 120 --workers 2 app:app\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

CMD ["/app/start.sh"]
