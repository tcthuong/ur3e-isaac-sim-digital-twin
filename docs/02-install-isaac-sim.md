# Install Isaac Sim

NVIDIA's workstation install is the simplest path for an Ubuntu Desktop pod because it gives you the GUI application and the built-in ROS 2 Bridge extension.

Official docs:

- Workstation install: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_workstation.html
- Requirements: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html
- ROS 2 setup: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html

## Download

Download the Linux x86_64 Isaac Sim standalone package from NVIDIA into `~/Downloads`.

The docs example uses:

```bash
isaac-sim-standalone-6.0.0-linux-x86_64.zip
```

If NVIDIA marks the latest release as an early developer release or changes the package name, use the latest generally available standalone Linux package from the same official download page.

## Install

```bash
mkdir -p ~/isaacsim
cd ~/Downloads
unzip "isaac-sim-standalone-6.0.0-linux-x86_64.zip" -d ~/isaacsim
cd ~/isaacsim
./post_install.sh
```

If your file name differs, replace the zip name in the command.

## Compatibility Check

```bash
cd ~/isaacsim
./isaac-sim.compatibility_check.sh --/app/quitAfter=10 --no-window
```

The checker validates GPU, driver, OS, CPU, RAM, storage, and display support.

## First Launch

From the desktop terminal:

```bash
cd ~/isaacsim
./isaac-sim.sh
```

The first launch can take several minutes because shaders and caches are warmed up.

If the UI gets into a bad cached state:

```bash
cd ~/isaacsim
./isaac-sim.sh --reset-user
```

## Open the UR3e Asset

In Isaac Sim:

1. Use **File > Open**.
2. Open `~/robotx/assets/ur3e/ur3e.usd`.
3. Press **Play** only after the ROS 2 graph is configured.

## Enable ROS 2 Bridge

In Isaac Sim:

1. Open **Window > Extensions**.
2. Search for `isaacsim.ros2.bridge`.
3. Enable it.
4. Enable auto-load if you want it on every launch.

You can also launch with:

```bash
cd ~/isaacsim
./isaac-sim.sh --enable isaacsim.ros2.bridge
```

ROS 2 graph nodes usually publish and subscribe only while simulation is playing.
