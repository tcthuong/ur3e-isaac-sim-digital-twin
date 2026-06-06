#!/usr/bin/env bash
set -euo pipefail

if [[ "$(lsb_release -rs)" != "24.04" ]]; then
  echo "This script targets Ubuntu 24.04 + ROS 2 Jazzy." >&2
  exit 1
fi

sudo apt update
sudo apt install -y locales software-properties-common curl git build-essential python3-pip
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

sudo add-apt-repository -y universe
sudo apt update

if ! dpkg -s ros2-apt-source >/dev/null 2>&1; then
  ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
  curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo "${UBUNTU_CODENAME:-${VERSION_CODENAME}}")_all.deb"
  sudo dpkg -i /tmp/ros2-apt-source.deb
fi

sudo apt update
sudo apt upgrade -y
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-dev-tools \
  ros-jazzy-desktop \
  ros-jazzy-moveit \
  ros-jazzy-vision-msgs \
  ros-jazzy-ackermann-msgs

if ! sudo apt install -y ros-jazzy-ur; then
  sudo apt install -y \
    ros-jazzy-ur-description \
    ros-jazzy-ur-moveit-config \
    ros-jazzy-ur-robot-driver
fi

if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  sudo rosdep init
fi
rosdep update

if ! grep -q "source /opt/ros/jazzy/setup.bash" "$HOME/.bashrc"; then
  echo "source /opt/ros/jazzy/setup.bash" >> "$HOME/.bashrc"
fi

echo "ROS 2 Jazzy, MoveIt 2, and UR packages are installed."
