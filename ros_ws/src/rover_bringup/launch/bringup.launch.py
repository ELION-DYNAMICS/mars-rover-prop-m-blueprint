from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    mode = LaunchConfiguration("mode")          # modern | prop_m
    run_type = LaunchConfiguration("run_type")  # sim | hw
    use_nav2 = LaunchConfiguration("use_nav2")  # true | false

    pkg_share = FindPackageShare("rover_bringup")

    sim_selected = PythonExpression(['"', run_type, '" == "sim"'])

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern", description="Operating mode: modern | prop_m"),
        DeclareLaunchArgument("run_type", default_value="sim", description="Execution: sim | hw"),
        DeclareLaunchArgument("use_nav2", default_value="true", description="Enable Nav2 stack (modern usually true)"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([pkg_share, "launch", "sim_bringup.launch.py"])
            ),
            condition=IfCondition(sim_selected),
            launch_arguments={
                "mode": mode,
            }.items()
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([pkg_share, "launch", "hw_bringup.launch.py"])
            ),
            condition=UnlessCondition(sim_selected),
            launch_arguments={
                "mode": mode,
            }.items()
        ),

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
