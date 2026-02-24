from setuptools import setup

package_name = "rover_driver_base"

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
    description="Base driver layer. Provides simulation stubs and hardware abstraction interfaces.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "sim_imu_node = rover_driver_base.sim_imu_node:main",
            "sim_encoder_node = rover_driver_base.sim_encoder_node:main",
            "sim_contacts_node = rover_driver_base.sim_contacts_node:main",
            "sim_motor_interface_node = rover_driver_base.sim_motor_interface_node:main",
        ],
    },
)
