#!/bin/bash
set -euo pipefail

echo "[docker] Running headless sim smoke test..."

source /opt/ros/humble/setup.bash
cd /workspaces/mars-rover-prop-m-blueprint/ros_ws

# Ensure built workspace is sourced
if [ -f "install/setup.bash" ]; then
  source install/setup.bash
fi

# Gazebo Classic headless
export GAZEBO_MODEL_PATH="/workspaces/mars-rover-prop-m-blueprint/ros_ws/src/rover_sim_gazebo/models:${GAZEBO_MODEL_PATH:-}"
export GAZEBO_PLUGIN_PATH="/workspaces/mars-rover-prop-m-blueprint/ros_ws/install/rover_sim_gazebo/lib:${GAZEBO_PLUGIN_PATH:-}"

# Run Gazebo without GUI
export DISPLAY=""
export SVGA_VGPU10=0

timeout 30s ros2 launch rover_sim_gazebo sim.launch.py world:=mars_flat.sdf || true

echo "[docker] Smoke test finished (timeout is expected unless you add a shutdown condition)."
