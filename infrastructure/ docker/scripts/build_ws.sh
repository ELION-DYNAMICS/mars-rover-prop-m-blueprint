#!/bin/bash
set -euo pipefail

echo "[docker] Building ROS workspace..."

cd /workspaces/mars-rover-prop-m-blueprint/ros_ws
source /opt/ros/humble/setup.bash

# rosdep may already be initialized in image; safe to run
rosdep update || true
rosdep install --from-paths src --ignore-src -r -y

colcon build --symlink-install

echo "[docker] Build complete."
