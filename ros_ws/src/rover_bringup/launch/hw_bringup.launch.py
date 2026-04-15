from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, RaiseError

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="modern"),

        LogInfo(
            msg=(
                "Hardware bringup requested, but the repository does not yet "
                "contain a validated hardware driver stack."
            )
        ),
        RaiseError(
            msg=(
                "hw_bringup.launch.py is an explicit placeholder until "
                "motor, IMU, encoder, and contact drivers are implemented "
                "and validated."
            )
        ),
    ])
