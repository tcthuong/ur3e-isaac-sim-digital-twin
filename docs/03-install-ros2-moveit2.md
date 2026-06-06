# Install ROS 2, MoveIt 2, and UR Packages

Recommended baseline:

- Ubuntu 24.04
- ROS 2 Jazzy
- MoveIt 2 binary packages
- Universal Robots ROS 2 packages for UR3e description, driver, and MoveIt config

Official docs:

- ROS 2 Jazzy Ubuntu install: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
- Isaac Sim ROS 2 setup: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html
- MoveIt 2 binary install: https://moveit.ai/install-moveit2/binary/
- Universal Robots ROS 2 driver: https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver
- UR MoveIt config: https://docs.universal-robots.com/Universal_Robots_ROS2_Documentation/doc/ur_robot_driver/ur_moveit_config/doc/index.html

## Install ROS 2 Jazzy

```bash
sudo apt update
sudo apt install -y locales software-properties-common curl
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

sudo add-apt-repository -y universe
sudo apt update
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

sudo apt update
sudo apt upgrade -y
sudo apt install -y ros-jazzy-desktop ros-dev-tools
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source /opt/ros/jazzy/setup.bash
```

Verify:

```bash
ros2 doctor
ros2 run demo_nodes_cpp talker
```

Open a second terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_py listener
```

## Install MoveIt 2 and UR Packages

```bash
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-jazzy-moveit \
  ros-jazzy-ur \
  ros-jazzy-vision-msgs \
  ros-jazzy-ackermann-msgs
```

Initialize rosdep once:

```bash
sudo rosdep init || true
rosdep update
```

## Build This Repo's ROS Workspace

```bash
cd ~/robotx/ros2_ws
source /opt/ros/jazzy/setup.bash
rosdep install -i --from-path src --rosdistro jazzy -y
colcon build --symlink-install
source install/setup.bash
```

Add the workspace to your shell:

```bash
echo "source ~/robotx/ros2_ws/install/setup.bash" >> ~/.bashrc
```

## UR3e MoveIt Mock Hardware

Use this to verify UR packages without a physical robot:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur3e \
  robot_ip:=192.168.56.101 \
  use_mock_hardware:=true \
  launch_rviz:=true
```

In another terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur3e launch_rviz:=true
```

For a real UR3e, replace `robot_ip` with the real robot controller IP and follow the Universal Robots driver setup and safety instructions. Do not command a physical robot until safety limits, emergency stop, calibration, and workspace boundaries are configured.
