from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    mode = LaunchConfiguration("mode")          # modern | prop_m
    run_type = LaunchConfiguration("run_type")  # sim | hw
    use_nav2 = LaunchConfiguration("use_nav2")  # true | false

    pkg_share = FindPackageShare("rover_bringup")

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern", description="Operating mode: modern | prop_m"),
        DeclareLaunchArgument("run_type", default_value="sim", description="Execution: sim | hw"),
        DeclareLaunchArgument("use_nav2", default_value="true", description="Enable Nav2 stack (modern usually true)"),

        # Simulation or Hardware bringup
        GroupAction([
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([pkg_share, "launch", "sim_bringup.launch.py"])
                ),
                condition=None,
                launch_arguments={
                    "mode": mode,
                }.items()
            ),
        ]),

        # Nav2 bringup (optional)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([pkg_share, "launch", "nav2_bringup.launch.py"])
            ),
            launch_arguments={
                "mode": mode,
                "use_nav2": use_nav2,
            }.items()
        ),
    ])
