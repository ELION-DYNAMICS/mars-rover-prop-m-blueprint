from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    mode = LaunchConfiguration("mode")
    use_nav2 = LaunchConfiguration("use_nav2")

    pkg_share = FindPackageShare("rover_bringup")

    nav2_params_modern = PathJoinSubstitution([pkg_share, "params", "nav2", "rover_v1.yaml"])
    nav2_params_prop = PathJoinSubstitution([pkg_share, "params", "nav2", "rover_prop_m_mode.yaml"])

    nav2_pkg = FindPackageShare("nav2_bringup")
    nav2_launch = PathJoinSubstitution([nav2_pkg, "launch", "bringup_launch.py"])

    # Select params file based on mode
    params_file = PythonExpression([
        '"', nav2_params_prop, '" if "', mode, '" == "prop_m" else "', nav2_params_modern, '"'
    ])

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern"),
        DeclareLaunchArgument("use_nav2", default_value="true"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            condition=IfCondition(use_nav2),
            launch_arguments={
                "use_sim_time": "true",
                "params_file": params_file,
            }.items()
        ),
    ])
