from setuptools import setup

package_name = "rover_control"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Maintainer",
    maintainer_email="unknown@example.com",
    description="Command arbitration and safety shaping: /cmd_vel -> /cmd_vel_safe.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "rover_control_node = rover_control.control_node:main",
        ],
    },
)
