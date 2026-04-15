from setuptools import setup
from glob import glob
import os

package_name = "rover_bringup"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "params"), glob("params/*.yaml")),
        (os.path.join("share", package_name, "params", "modes"), glob("params/modes/*.yaml")),
        (os.path.join("share", package_name, "params", "nav2"), glob("params/nav2/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Elion Dynamics Engineering",
    maintainer_email="engineering@elion.com",
    description="Bringup and mode-switch launch for Mars Rover Prop-M Blueprint.",
    license="Apache-2.0",
)
