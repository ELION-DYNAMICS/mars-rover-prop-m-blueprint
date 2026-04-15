from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    mode = LaunchConfiguration("mode")  # modern | prop_m

    bringup_pkg = FindPackageShare("rover_bringup")
    mission_pkg = FindPackageShare("rover_mission_bt")
    description_pkg = FindPackageShare("rover_description")
    estimation_pkg = FindPackageShare("rover_estimation")

    common_params = PathJoinSubstitution([bringup_pkg, "params", "common.yaml"])
    modern_params = PathJoinSubstitution([bringup_pkg, "params", "modes", "modern.yaml"])
    prop_params = PathJoinSubstitution([bringup_pkg, "params", "modes", "prop_m.yaml"])
    description_launch = PathJoinSubstitution([description_pkg, "launch", "description.launch.py"])
    estimation_launch = PathJoinSubstitution([estimation_pkg, "launch", "ekf.launch.py"])
    modern_tree = PathJoinSubstitution([mission_pkg, "trees", "modern_cycle.xml"])
    prop_tree = PathJoinSubstitution([mission_pkg, "trees", "prop_m_cycle.xml"])

    tree_file = PythonExpression([
        '"', prop_tree, '" if "', mode, '" == "prop_m" else "', modern_tree, '"'
    ])

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(description_launch),
            launch_arguments={
                "use_sim": "true",
                "use_ros2_control": "true",
            }.items()
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(estimation_launch),
            launch_arguments={
                "mode": mode,
            }.items()
        ),

        Node(
            package="rover_control",
            executable="rover_control_node",
            name="rover_control",
            output="screen",
            parameters=[common_params, modern_params, prop_params, {"use_sim_time": True}],
        ),

        Node(
            package="rover_mission_bt",
            executable="rover_mission_bt_node",
            name="rover_mission_bt",
            output="screen",
            parameters=[
                common_params,
                modern_params,
                prop_params,
                {
                    "use_sim_time": True,
                    "tree_file": tree_file,
                },
            ],
        ),
    ])
