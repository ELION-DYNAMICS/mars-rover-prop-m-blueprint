from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    use_sim = LaunchConfiguration("use_sim")
    use_ros2_control = LaunchConfiguration("use_ros2_control")

    pkg = FindPackageShare("rover_description")
    xacro_file = PathJoinSubstitution([pkg, "urdf", "rover.urdf.xacro"])

    robot_description = Command([
        "xacro ", xacro_file,
        " use_sim:=", use_sim,
        " use_ros2_control:=", use_ros2_control
    ])

    return LaunchDescription([
        DeclareLaunchArgument("use_sim", default_value="true"),
        DeclareLaunchArgument("use_ros2_control", default_value="true"),

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description, "use_sim_time": True}],
        ),
    ])
