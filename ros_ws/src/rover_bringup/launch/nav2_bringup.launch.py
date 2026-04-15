from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    mode = LaunchConfiguration("mode")
    use_nav2 = LaunchConfiguration("use_nav2")
    nav_pkg = FindPackageShare("rover_navigation")
    nav_launch = PathJoinSubstitution([nav_pkg, "launch", "nav2.launch.py"])

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern"),
        DeclareLaunchArgument("use_nav2", default_value="true"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav_launch),
            condition=IfCondition(use_nav2),
            launch_arguments={
                "mode": mode,
                "use_nav2": use_nav2,
                "use_sim_time": "true",
            }.items()
        ),
    ])
