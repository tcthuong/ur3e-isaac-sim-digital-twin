# RunPod Ubuntu Desktop Setup

This guide targets a practical cloud workstation for Isaac Sim, ROS 2, and MoveIt 2.

## Recommended Pod

Use Ubuntu 24.04 with an RTX-capable GPU. Good first choices:

- RTX 4090
- RTX 6000 Ada
- L40 / L40S
- A6000

Avoid A100/H100 for this workflow. They are excellent compute GPUs, but Isaac Sim's RTX renderer and GUI workflows require RT-core capable GPUs.

Recommended storage:

- 80 GB minimum for Isaac Sim + ROS 2 + workspace
- 150 GB or more if you plan to install Isaac Lab or train policies

Recommended memory:

- 32 GB minimum
- 64 GB preferred for training and large scenes

## RunPod Access

Use one of these access patterns:

1. Ubuntu Desktop / VNC template for interactive GUI use.
2. SSH plus a remote desktop service if your chosen template does not include desktop access.
3. Headless Isaac Sim only after the visual workflow already works.

RunPod exposes services through HTTP proxy or TCP port forwarding. For desktop or SSH, use the connection details shown in the Pod's **Connect** panel.

Common ports:

- SSH: `22` as TCP
- noVNC web desktop: usually `6080` or template-specific HTTP port
- Jupyter or dev web UIs: `8888` as HTTP

RunPod docs:

- Expose ports: https://docs.runpod.io/pods/configuration/expose-ports
- SSH: https://docs.runpod.io/pods/configuration/use-ssh

## First Login Checklist

Run:

```bash
nvidia-smi
lsb_release -a
df -h
```

Expected:

- `nvidia-smi` shows your GPU and a recent NVIDIA driver.
- Ubuntu is 24.04 for the recommended ROS 2 Jazzy path.
- You have enough free disk space for Isaac Sim.

Install basic tools:

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  curl \
  git \
  locales \
  python3-pip \
  unzip \
  wget
```

Clone this repo:

```bash
cd ~
git clone https://github.com/YOUR_GITHUB_USER/ur3e-isaac-sim-digital-twin.git robotx
cd ~/robotx
```

Replace the URL with the real repository URL after the repo is published.
