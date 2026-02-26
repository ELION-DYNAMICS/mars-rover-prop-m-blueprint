from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    mode = LaunchConfiguration("mode")          # modern | prop_m
    use_nav2 = LaunchConfiguration("use_nav2")  # true | false
    use_sim_time = LaunchConfiguration("use_sim_time")

    pkg_share = FindPackageShare("rover_navigation")
    nav2_pkg = FindPackageShare("nav2_bringup")

    params_modern = PathJoinSubstitution([pkg_share, "params", "nav2_modern.yaml"])
    params_prop = PathJoinSubstitution([pkg_share, "params", "nav2_prop_m.yaml"])

    params_file = PythonExpression([
        '"', params_prop, '" if "', mode, '" == "prop_m" else "', params_modern, '"'
    ])

    nav2_launch = PathJoinSubstitution([nav2_pkg, "launch", "bringup_launch.py"])

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern"),
        DeclareLaunchArgument("use_nav2", default_value="true"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            condition=IfCondition(use_nav2),
            launch_arguments={
                "use_sim_time": use_sim_time,
                "params_file": params_file,
            }.items()
        ),
    ])
