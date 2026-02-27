#!/bin/bash
set -e

echo "[devcontainer] Running post-create setup..."

cd /workspaces/mars-rover-prop-m-blueprint/ros_ws

source /opt/ros/humble/setup.bash

rosdep install --from-paths src --ignore-src -r -y

colcon build --symlink-install

echo "[devcontainer] Workspace built successfully."
