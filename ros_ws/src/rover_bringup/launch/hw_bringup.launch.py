from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node

def generate_launch_description():
    # Hardware bringup is intentionally strict and separate.
    # Add driver nodes here once they exist.
    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern"),

        Node(
            package="rover_driver_motor",
            executable="motor_driver_node",
            name="rover_driver_motor",
            output="screen",
            parameters=[{"use_sim_time": False}],
        ),
    ])
