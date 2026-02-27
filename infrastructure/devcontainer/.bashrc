source /opt/ros/humble/setup.bash

if [ -f ~/workspaces/mars-rover-prop-m-blueprint/ros_ws/install/setup.bash ]; then
  source ~/workspaces/mars-rover-prop-m-blueprint/ros_ws/install/setup.bash
fi

export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
