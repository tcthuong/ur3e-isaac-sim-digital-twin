# Install Isaac Sim

This repo currently uses the Isaac Sim Python package install. It works well on a root-based RunPod/container shell where a nested Docker install is blocked and where the standalone workstation zip has not been downloaded.

Official docs:

- Python environment install: https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/install_python.html
- Requirements: https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html
- Download page: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/download.html

## Version

The latest generally available release shown by NVIDIA is Isaac Sim `5.1.0`. Isaac Sim `6.0` documentation is currently marked as an Early Developer Release, so this project pins `5.1.0` for normal development.

## Install

```bash
python3.11 -m venv ~/isaacsim-5.1.0
~/isaacsim-5.1.0/bin/python -m pip install --upgrade pip
~/isaacsim-5.1.0/bin/pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
```

## Compatibility Check

```bash
cd ~/robotx
./scripts/check_isaac_sim.sh
```

The checker validates GPU, driver, OS, CPU, RAM, storage, and display support.

## First Launch

Use the wrapper script instead of calling `isaacsim` directly:

```bash
cd ~/robotx
./scripts/run_isaac_sim.sh
```

The wrapper does three important things:

- Accepts the EULA for non-interactive startup.
- Allows root execution in a root-based pod.
- Clears ROS Python 3.12 paths before launching Isaac Sim's Python 3.11 app, then points the ROS 2 Bridge at Isaac Sim's internal Jazzy bridge libraries.

The first launch can take several minutes because shaders and caches are warmed up.

To launch Isaac Sim and automatically open the current UR3e stage:

```bash
cd ~/robotx
./scripts/run_ur3e_isaac_sim.sh
```

If the UI gets into a bad cached state:

```bash
cd ~/robotx
./scripts/run_isaac_sim.sh --reset-user
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
cd ~/robotx
./scripts/run_isaac_sim.sh
```

ROS 2 graph nodes usually publish and subscribe only while simulation is playing.
