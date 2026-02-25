from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    mode = LaunchConfiguration("mode")  # modern | prop_m
    pkg = FindPackageShare("rover_estimation")

    cfg_modern = PathJoinSubstitution([pkg, "config", "ekf_modern.yaml"])
    cfg_prop = PathJoinSubstitution([pkg, "config", "ekf_prop_m.yaml"])

    params_file = PythonExpression([
        '"', cfg_prop, '" if "', mode, '" == "prop_m" else "', cfg_modern, '"'
    ])

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern"),

        Node(
            package="robot_localization",
            executable="ekf_node",
            name="ekf_filter_node",
            output="screen",
            parameters=[params_file],
            remappings=[
                # Ensure output matches your ICD expectations
                ("/odometry/filtered", "/odometry/filtered"),
            ],
        ),
    ])
