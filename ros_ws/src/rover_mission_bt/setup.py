from setuptools import setup
from glob import glob
import os

package_name = "rover_mission_bt"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "trees"), glob("trees/*.xml")),
        ("share/" + package_name, ["README.md"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Elion Dynamics Engineering",
    maintainer_email="engineering@elion.com",
    description="Behavior Trees for rover mission cycles (Drive -> Stop/Measure -> Transmit/Log).",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "rover_mission_bt_node = rover_mission_bt.mission_bt_node:main",
        ],
    },
)
