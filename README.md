# 🍰 SLICE — Private Cloud System Container Engine

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Ubuntu%2024.04%20LTS-E95420?style=for-the-badge&logo=ubuntu&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/Engine-Incus%206.0%20LTS-008080?style=for-the-badge&logo=linuxcontainers&logoColor=white" alt="Incus" />
  <img src="https://img.shields.io/badge/Virtualization-System%20Containers-blue?style=for-the-badge" alt="System Containers" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="License" />
</p>

```text
    _____ __    ________________
   / ___// /   /  _/ ____/ ____/
   \__ \/ /    / // /   / __/   
  ___/ / /____/ // /___/ /___   
 /____/_____/___/\____/_____/   
  SLICE · Private Cloud VPS Engine 🍰⚡
  Dedicated High-Performance System Container VPS on Bare-Metal & Laptops
```

**SLICE** is an ultra-lightweight, multi-tenant **Private Cloud VPS Engine** built on top of **Incus (Linux Containers)**. It transforms any spare Linux machine, bare-metal server, or headless laptop into an enterprise-grade developer sandbox fleet — delivering 100% genuine VPS experience with full `systemd`, root privileges, native Docker support, and dedicated resource hardcaps at sub-0.5% overhead.

---

## 🌟 Key Features

* **🏎️ True System Containers (Not Just Docker):**  
  Every slice instance is an isolated Ubuntu 24.04 LTS system running a real `systemd` init process (`PID 1`). Run `systemctl`, `journalctl`, and background daemons with zero friction.
* **🐳 Native Docker-in-Slice (Security Nesting):**  
  Run Docker Engine and Docker Compose seamlessly inside unprivileged containers without host-level root escapes (`security.nesting=true`).
* **🛡️ Tri-Layer Security & Brute-Force Shield:**  
  Hardened against public internet attacks with **Kernel iptables rate-limiting** (max 5 new handshakes/min), **Fail2ban auto-jail**, and restricted SSH `MaxAuthTries`.
* **♻️ Smart Port & Slot Recycling:**  
  Automatic allocation and recycling of SSH ports (`2211 - 2220`) and dedicated web development port blocks (`3101 - 3130`). Reclaims deleted user ports automatically without fragmentation.
* **📊 Accurate CGroup v2 Realtime Telemetry:**  
  Extracts pure anonymous process memory (`anon memory`) directly from CGroup v2, eliminating Linux page cache skew. Features a live streaming monitor (`slice top` / `slice stats -w`) with dynamic ASCII progress bars.
* **🎮 GPU Passthrough Ready:**  
  Share host dedicated GPUs (e.g., NVIDIA GeForce GTX 1650) dynamically with tenant instances on-demand (`slice gpu attach <name>`).
* **🔋 Laptop Hygiene Automation:**  
  Locks systemd inhibitor masks (`HandleLidSwitch=ignore`) so laptops can run 24/7 with the lid closed without suspending.
* **💾 Instant Point-in-Time Snapshots:**  
  Create instant immutable snapshots in seconds (`slice backup <name>`) with one-command restore capabilities.

---

## 🏛️ Sizing & Resource Allocation Model

| Component / Tenant | Guaranteed RAM | CPU Allocation | Dedicated Storage | Capabilities |
| :--- | :---: | :---: | :---: | :--- |
| **Host System (`playfam1`)** | **3.0 GB** | **2 Core Reserve** | **~260 GB** | Kernel I/O buffers, Incus daemon, Tailscale mesh |
| **Slice Tenant 1 (`chelsea`)** | **4.0 GB** | **4 vCPU Burst** | **200 GB** | Full Sudo, Native Docker, SSH Port 2211 |
| **Slice Tenant 2 (`shazmeen`)**| **4.0 GB** | **4 vCPU Burst** | **200 GB** | Full Sudo, Native Docker, SSH Port 2212 |
| **Slice Tenant 3 (`titid`)**   | **4.0 GB** | **4 vCPU Burst** | **200 GB** | Full Sudo, Native Docker, SSH Port 2213 |

---

## ⚡ Quick Installation

Clone this repository and run the automated installer on **Ubuntu 24.04 LTS**:

```bash
git clone https://github.com/fathurrach/slice.git
cd slice
sudo chmod +x install.sh
sudo ./install.sh
```

---

## 🛠️ CLI Cheat Sheet

```bash
# Provision a new VPS instance in 30 seconds
slice create danz

# Display categorized fleet overview table
slice list
# or
slice ls

# Live auto-refreshing resource telemetry (like htop)
slice top
# or
slice stats -w

# Generate official developer onboarding card for WhatsApp
slice invite danz

# Register developer SSH public key passwordlessly
slice key add danz "ssh-ed25519 AAAAC3... danz@laptop"
slice key list danz

# Forward an additional custom port to the slice
slice port add danz 8080

# Create an instant backup snapshot
slice backup danz

# Share / reclaim host NVIDIA GPU
slice gpu attach danz
slice gpu detach danz

# Enter instance terminal as tenant or emergency root
slice enter danz
slice root danz

# Execute a one-liner command inside slice
slice exec danz "docker ps"

# Destroy an instance and recycle its ports
slice delete danz
```

---

## 🧰 In-Slice Developer Experience

When developers log in via SSH, they are greeted by an automated dynamic dual-slant ASCII banner and a built-in suite of developer ergonomics:

* **`info`** — Real-time memory allocation, uptime, and system diagnostics.
* **`ports`** — Lists assigned public web development URLs (`http://slice.atnx.my.id:<port>`).
* **`quota`** — High-resolution 200 GB disk quota accounting and directory breakdown.
* **`clean`** — Reclaims disk space by pruning dangling Docker images and package caches.
* **`passwd`** — Quickly update initial temporary password.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Developed with 🖤⚡ by **Fathurrachman** ([@fathurrach](https://github.com/fathurrach)).
