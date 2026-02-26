from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    desc_pkg = FindPackageShare("rover_description")
    xacro_file = PathJoinSubstitution([desc_pkg, "urdf", "rover.urdf.xacro"])

    robot_desc = Command(["xacro ", xacro_file, " use_sim:=true use_ros2_control:=true"])

    return LaunchDescription([
        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=[
                "-topic", "robot_description",
                "-entity", "rover",
                "-x", "0", "-y", "0", "-z", "0.15",
            ],
            output="screen",
            parameters=[{"robot_description": robot_desc}],
        ),
    ])
