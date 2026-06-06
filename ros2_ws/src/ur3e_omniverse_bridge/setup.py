from setuptools import find_packages, setup


package_name = "ur3e_omniverse_bridge"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml", "README.md"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="RobotX Maintainers",
    maintainer_email="dev@example.com",
    description="ROS 2 helpers for syncing external UR3e joint commands with NVIDIA Isaac Sim.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "ur3e_joint_command_demo = ur3e_omniverse_bridge.ur3e_joint_command_demo:main",
            "external_joint_state_relay = ur3e_omniverse_bridge.external_joint_state_relay:main",
            "display_trajectory_to_joint_command = ur3e_omniverse_bridge.display_trajectory_to_joint_command:main",
            "follow_joint_trajectory_to_joint_command = ur3e_omniverse_bridge.follow_joint_trajectory_to_joint_command:main",
            "http_joint_command_server = ur3e_omniverse_bridge.http_joint_command_server:main",
            "moveit_pick_place_demo = ur3e_omniverse_bridge.moveit_pick_place_demo:main",
        ],
    },
)
