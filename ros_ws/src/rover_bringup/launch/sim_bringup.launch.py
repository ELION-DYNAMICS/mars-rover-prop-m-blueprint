from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    mode = LaunchConfiguration("mode")  # modern | prop_m

    pkg_share = FindPackageShare("rover_bringup")

    common_params = PathJoinSubstitution([pkg_share, "params", "common.yaml"])
    modern_params = PathJoinSubstitution([pkg_share, "params", "modes", "modern.yaml"])
    prop_params = PathJoinSubstitution([pkg_share, "params", "modes", "prop_m.yaml"])

    # NOTE: We load both mode files but use them via namespacing or node-specific selection later.
    # For now, keep it explicit and controlled.

    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern"),

        # Robot State Publisher (URDF is assumed to be provided elsewhere; wire later)
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"use_sim_time": True}],
        ),

        # Placeholder core nodes (replace packages/executables with your real ones as they exist)
        # Control arbitration / safety
        Node(
            package="rover_control",
            executable="rover_control_node",
            name="rover_control",
            output="screen",
            parameters=[common_params, modern_params, prop_params],
        ),

        # Estimation (EKF)
        Node(
            package="rover_estimation",
            executable="rover_estimation_node",
            name="rover_estimation",
            output="screen",
            parameters=[common_params, modern_params, prop_params],
        ),

        # Mission executive
        Node(
            package="rover_mission",
            executable="rover_mission_node",
            name="rover_mission",
            output="screen",
            parameters=[common_params, modern_params, prop_params],
        ),
    ])
