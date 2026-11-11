# 📋 Product Requirement Document (PRD) & Technical Specification
# Project: SLICE (`slice`) — Multi-Tenant System Container & Private Cloud VPS Engine

> **Document ID:** PRD-SLICE-2026-V1  
> **Classification:** Confidential / Internal Engineering Blueprint  
> **Project Code:** `slice` (formerly *hvps*)  
> **Target Node:** `playfam1` (Tailscale: `100.108.185.46` · LAN Wi-Fi: `192.168.20.193`)  
> **Hardware:** HP Pavilion Gaming Laptop 15-dk1xxx (Intel Core i7-10750H · 16GB RAM · 1TB SATA · GTX 1650)  
> **Authors:** Fathurrachman (GM / Project Lead) & ATNX 🖤⚡ (Systems Architect)  
> **Release Date:** November 2026 · Version 1.0.0  

---

## 1. 🎯 Executive Summary & Vision

### 1.1 Context & Background
The expansion of our computing infrastructure across Telkom OPMC and the ATNX fleet has reached three dedicated nodes:
1. **`fm.atnx` (ASUS TUF F15):** Central operational command center, hosting core databases, Coolify, 9router, and the primary ATNX autonomous agent.
2. **`playfam` (Desktop PC i7-4790):** Dedicated host for **Hermes Box (H-Box)**, serving multi-tenant sandbox environments tailored for beginner office peers (strict 1.5 GB limits, containerized Hermes AI, and integrated 24/7 Telegram bots).
3. **`playfam1` (HP Pavilion Gaming 15):** Designated as the **Advanced Developer Fleet Node**.

Advanced software engineers in our circle require full freedom that conventional application containers (plain Docker) cannot offer without severe trade-offs. They require:
* True operating system environments with native **`systemd`** as PID 1 (`systemctl`, `journalctl`, daemon supervisors).
* Full rootless and nested containerization capabilities (**Docker-in-VPS / Docker Compose** within their own sandbox).
* Unrestricted package installation (`apt`, `snap`, custom compilers for Rust, Go, Python, Node.js).
* Dedicated development port ranges to expose internal web servers, microservices, and databases for testing.
* Optional hardware acceleration via the onboard **NVIDIA GeForce GTX 1650 (4GB GDDR6)** for local AI inference, CUDA tasks, and media processing.

### 1.2 The Solution: `slice`
**`slice`** is an ultra-lightweight, high-performance Private Cloud VPS manager built on top of **Incus** (the independent, community-driven continuation of Canonical's LXD by the Linux Containers team). 

Instead of heavy hardware emulation (KVM / Proxmox) which locks RAM statically and wastes compute cycles, `slice` provisions **System Containers** running Ubuntu 24.04 LTS. Each instance behaves 100% like a dedicated cloud VPS from DigitalOcean, Linode, or Hetzner, while operating with near-zero virtualization overhead and shared kernel efficiency.

### 1.3 Why the Name "Slice"?
Historically, before the term "VPS" became generic, pioneer hosting platforms coined the term *"a slice of a server"* (most notably *Slicehost*). The name **`slice`** captures this philosophy perfectly:
* **Monosyllabic & Ergonomic:** Single-syllable, punchy, memorable, and lightning-fast to type in terminal sessions (`slice list`, `slice create`).
* **Universal & Non-Biased:** Free of vendor or platform constraints (unlike *hvps* or *hbox*). A slice is simply a clean, independent slice of modern Linux computing power for developers to use as they see fit.

---

## 2. 🖥️ Physical Hardware Baseline (`playfam1`)

Comprehensive hardware discovery performed on node `playfam1` confirms the following physical topology:

| Hardware Subsystem | Detected Specification | Engineering Assessment |
| :--- | :--- | :--- |
| **Chassis / Model** | HP Pavilion Gaming Laptop 15-dk1xxx | Dual-fan rear exhaust thermal chassis |
| **Processor (CPU)** | Intel Core i7-10750H (Comet Lake-H) | 6 Cores / 12 Threads @ 2.60 GHz (Max Turbo 5.0 GHz) · 12MB Cache · Hardware VT-x Enabled |
| **System Memory (RAM)**| 16 GB DDR4-2933 MHz (15 GiB usable) | 4.0 GB Swap space active on drive. Base idle consumption: ~820 MB |
| **Primary Storage (SATA)**| 1.0 TB SATA HDD/SSD (`/dev/sda2`: 930.5 GB) | Mounted at `/`. 860 GB available unallocated space. Selected as the **exclusive** `slice` storage pool |
| **Secondary Storage (NVMe)**| 256 GB M.2 NVMe SSD (`/dev/nvme0n1`) | Contains pre-installed factory OEM Windows (NTFS, EFI, Recovery). **STRICTLY EXCLUDED / UNTOUCHED** |
| **Discrete GPU** | NVIDIA GeForce GTX 1650 Mobile / Max-Q | Chipset TU117M (4GB GDDR6 VRAM) · 896 CUDA Cores · NVENC/NVDEC hardware engines |
| **Operating System** | Ubuntu Server 24.04.5 LTS (Noble Numbat) | Linux Kernel 6.8.0-149-generic (x86_64) |
| **Network Interfaces** | Tailscale P2P (`100.108.185.46`) + Wi-Fi | Sub-30ms latency over encrypted Tailscale mesh |

---

## 3. 🏗️ Core Technology: Why Incus System Containers?

Traditional virtual machines (KVM) emulate physical hardware (virtual BIOS, virtual PCI buses, virtual NICs), incurring an unavoidable 10%–15% memory and CPU tax. Traditional Docker containers, on the other hand, isolate single processes and lack `systemd`, making it frustrating for developers who need to run background services, databases, and cron daemons together.

Incus bridges this gap:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      ARCHITECTURE COMPARISON MATRIX                    │
 ├─────────────────────────┬──────────────────────────┬───────────────────┤
 │ Docker Application Ctr  │ Incus System Container   │ Hardware KVM / VM │
 ├─────────────────────────┼──────────────────────────┼───────────────────┤
 │ Single Process (PID 1)  │ Full Init System (systemd│ Full OS & Kernel  │
 │ No background daemons   │ Native daemons & services│ Full daemons      │
 │ High risk for nested Dkr│ Native secure Docker DinI│ Secure nesting    │
 │ Shared root risk        │ Unprivileged User Namespc│ Hard hypervisor   │
 │ RAM overhead: ~10 MB    │ RAM overhead: ~25-35 MB  │ RAM overhead: ~1GB│
 │ 16GB limit: Many apps   │ 16GB limit: 3-5 Full VPS │ 16GB limit: 2 VM  │
 └─────────────────────────┴──────────────────────────┴───────────────────┘
```

### 3.1 Security via Unprivileged User Namespaces
By default, all Incus containers run as **unprivileged containers**. The container's root user (`UID 0`) is mapped to an unprivileged sub-UID on the host (e.g., `UID 1000000`). Even if a malicious actor or errant script achieves root privilege inside a slice, their real UID on the host laptop remains unprivileged, eliminating container breakouts to the host filesystem.

### 3.2 Native Docker Nesting (`security.nesting=true`)
Developers can install Docker Engine, Docker Compose, or lightweight Kubernetes (`k3s`) directly inside their slice. Incus configures the necessary cgroup controllers and namespace mounts safely without requiring dangerous privileged flags.

---

## 4. 🗄️ Storage Architecture & Disk Policy

### 4.1 Strict Preservation of OEM Windows NVMe
The secondary 256 GB NVMe SSD (`/dev/nvme0n1`) holds:
* `/dev/nvme0n1p1`: EFI System Partition (`vfat`, UUID `2050-A441`)
* `/dev/nvme0n1p2`: Microsoft Reserved Partition
* `/dev/nvme0n1p3`: Windows Basic Data Partition (`ntfs`, 237.9 GB)
* `/dev/nvme0n1p4`: Windows Recovery Environment (`ntfs`)

**Policy Directive:** Under no circumstances shall `/dev/nvme0n1` be formatted, mounted, repartitioned, or added to Incus storage pools. This guarantees that the laptop can revert to Windows or dual-boot at any time without data loss.

### 4.2 Primary SATA Pool Configuration
All system containers, root filesystems, images, and user volumes reside on `/dev/sda2`:
* **Pool Name:** `slice-pool`
* **Driver:** `dir` or loop-backed `btrfs` / `zfs` on `/var/lib/incus/storage-pools/slice-pool`.
* **Available Capacity:** ~860 GB free space.
* **Storage Allocation per Slice:** Hard capped at **200 GB per user**, enforced via quota mechanisms.
* **Host Cushion:** ~260 GB retained exclusively by the host OS for caching, temporary compile artifacts, and system updates.

---

## 5. 📊 Capacity Sizing & Resource Model (3-Instance Model)

To guarantee high responsiveness, thermal safety for the laptop, and genuine "pro-tier" performance for developers, the resources of `playfam1` are partitioned according to a strict **1 Host + 3 Slices** formula:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                PHYSICAL HARDWARE: HP Pavilion 15 (16GB RAM)            │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
       ┌─────────────────────────────┼──────────────────────────────┐
       ▼                             ▼                              ▼
 ┌───────────┐                 ┌───────────┐                  ┌───────────┐
 │  HOST OS  │                 │  SLICE 1  │                  │  SLICE 2  │ ... (SLICE 3)
 │ 3.0 GB RAM│                 │4.0 GB RAM │                  │4.0 GB RAM │
 │ 2 Threads │                 │ 4 vCPU    │                  │ 4 vCPU    │
 │ ~260 GB   │                 │ 200 GB    │                  │ 200 GB    │
 └───────────┘                 └───────────┘                  └───────────┘
```

### 5.1 Resource Allocation Matrix

| Instance / Entity | Guaranteed RAM | CPU Allocation | Disk Quota | Process Cap | Roles & Capabilities |
| :--- | :---: | :---: | :---: | :---: | :--- |
| 🖥️ **Host OS (`playfam1`)** | **3.0 GB** | **2 Core Reserve** *(Kernel Prio)* | **~260 GB** | **Kernel stability**, I/O disk buffer cache, Tailscale daemon, Incus management. |
| 🍰 **Slice 1 (Dev A)** | **4.0 GB** | **4 vCPU** *(Dynamic Burst)* | **200 GB** | **500 PIDs** | Full VPS sandbox. Docker, Node.js, Go, Rust, PostgreSQL, Redis. |
| 🍰 **Slice 2 (Dev B)** | **4.0 GB** | **4 vCPU** *(Dynamic Burst)* | **200 GB** | **500 PIDs** | Full VPS sandbox. Docker, Node.js, Go, Rust, PostgreSQL, Redis. |
| 🍰 **Slice 3 (Dev C)** | **4.0 GB** | **4 vCPU** *(Dynamic Burst)* | **200 GB** | **500 PIDs** | Full VPS sandbox. Docker, Node.js, Go, Rust, PostgreSQL, Redis. |
| **TOTAL** | **15.0 GB** | **12 vCPU Total** | **~860 GB** | — | **Zero waste, mathematically balanced, 100% capacity utilization.** |

### 5.2 Technical Justification
1. **3.0 GB Host Reservation:**
   When three developers concurrently execute intensive tasks (such as `npm install`, `cargo build`, or compiling Docker images), disk I/O demands skyrocket. The Linux kernel relies on unallocated physical memory as page cache to smooth out disk write spikes. Reserving 3.0 GB prevents laptop freezing, audio/system jitter, and kernel OOM panics.
2. **Dynamic CPU Burst (4 vCPU Limit):**
   Developer workloads are inherently spiky. Instead of statically pinning 3 threads per instance, Incus assigns `limits.cpu: 4` with balanced CFS shares. A developer compiling code can consume up to 4 full threads instantly, releasing them back to the pool immediately upon completion.
3. **Generous 200 GB Storage:**
   Commercial cloud providers charge substantial premiums for 100GB+ SSD storage. Offering 200 GB per slice provides ample headroom for Docker images, local databases, and large datasets without friction.

---

## 6. 🌐 Network Architecture & Ingress

### 6.1 Internal Bridge (`slicebr0`)
* Incus provisions an isolated virtual bridge: `slicebr0`.
* IPv4 Subnet: `10.150.0.1/24` with internal dnsmasq handling DHCP and hostname resolution.
* Slices receive deterministic private IPs: `10.150.0.11`, `10.150.0.12`, `10.150.0.13`.

### 6.2 Port Forwarding Architecture
Because developers access `playfam1` across Tailscale or office Wi-Fi, port forwarding is managed via Incus native proxy devices (`type: proxy`), bypassing complex manual iptables:

#### A. SSH Access Ports
* **Slice 1:** `100.108.185.46:2211` ──► Slice 1 Port `22`
* **Slice 2:** `100.108.185.46:2212` ──► Slice 2 Port `22`
* **Slice 3:** `100.108.185.46:2213` ──► Slice 3 Port `22`

#### B. Development Port Blocks (Web Apps & API Testing)
Each slice receives a dedicated block of 5 forwarded ports to test web applications without port collisions:
* **Slice 1:** Host Ports `3101 - 3105` ──► Container Ports `3101 - 3105`
* **Slice 2:** Host Ports `3201 - 3205` ──► Container Ports `3201 - 3205`
* **Slice 3:** Host Ports `3301 - 3305` ──► Container Ports `3301 - 3305`

---

## 7. 🎮 GPU Passthrough (NVIDIA GTX 1650 4GB VRAM)

Node `playfam1` houses an onboard **NVIDIA GeForce GTX 1650 Mobile (TU117M)**. Incus supports sharing host GPU devices with unprivileged containers without requiring full VFIO PCI stubbing.

### 7.1 Passthrough Implementation
Host NVIDIA proprietary drivers are installed on `playfam1`. When a developer requires GPU power (for PyTorch, Whisper, or 3D rendering), the administrator attaches the GPU device dynamically:
```bash
slice gpu attach <slice_name>
```
Which executes the underlying Incus call:
```bash
incus config device add <slice_name> gpu0 gpu id=01:00.0
```

### 7.2 Developer Experience
Inside the slice, the developer can run `nvidia-smi` natively, access CUDA compute capabilities, and utilize NVENC hardware acceleration with zero emulation overhead.

---

## 8. 🔋 24/7 Laptop Hygiene & Reliability Protocols

Operating a gaming laptop as a 24/7 headless server requires proactive thermal and ACPI management to prevent unwanted sleep states:

1. **Lid Close Inhibition (`/etc/systemd/logind.conf`):**
   ```ini
   [Login]
   HandleLidSwitch=ignore
   HandleLidSwitchExternalPower=ignore
   HandleLidSwitchDocked=ignore
   LidSwitchIgnoreInhibited=no
   ```
2. **Masking System Suspend & Sleep Targets:**
   ```bash
   sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
   ```
3. **Physical Ventilation:**
   The laptop must be mounted on a ventilated riser or stand (rear lifted by at least 2.5 cm) to facilitate unrestricted intake airflow for the dual-fan cooling assembly.

---

## 9. 📁 Project Structure & Filesystem Layout

All code, configurations, templates, and state tracking for the `slice` platform will be consolidated under **/srv/slice/**:

```text
/srv/slice/
├── bin/
│   └── slice                      # Primary Bash CLI orchestrator (symlinked to /usr/local/bin/slice)
├── profiles/
│   ├── slice-standard.yaml        # Standard Incus profile (4GB RAM, 4 vCPU, 500 PIDs, nesting=true)
│   └── slice-gpu.yaml             # GPU passthrough profile overlay
├── templates/
│   ├── user-data.yaml             # Cloud-init template (provisions user, passwordless sudo, sshd config)
│   └── motd-banner.sh             # Elegant terminal welcome banner shown on SSH login
├── state/
│   └── slice-state.json           # Local database tracking assigned ports, IPs, quotas, and users
├── scripts/
│   ├── 01-host-prep.sh            # Idempotent script for lid sleep masking and kernel adjustments
│   ├── 02-init-storage.sh         # Formats/initializes SATA storage pool and incusbr0
│   └── 03-install-incus.sh        # Automates Incus package installation and group permissions
├── docs/
│   └── PRD_SLICE_VPS.pdf          # Compiled technical PRD and architecture blueprint
└── README.md                      # Operational runbook for administrators
```

---

## 10. 🛠️ CLI Manager Specification: `slice`

The `/usr/local/bin/slice` command provides an intuitive, high-level control plane for administrator operations.

### 10.1 Command Vocabulary

| Command Syntax | Description | Example Usage |
| :--- | :--- | :--- |
| `slice create <name> [port] [pass]` | Provisions a new Ubuntu 24.04 VPS slice with 4GB RAM, 4 vCPU, and 200GB storage. | `slice create danz` |
| `slice list` (or `slice ls`) | Displays a formatted table of all active slices, IP addresses, ports, and resource usage. | `slice list` |
| `slice stats` (or `slice top`) | Live telemetry dashboard showing CPU, RAM, and disk utilization per slice. | `slice stats` |
| `slice invite <name>` | Generates a clean, ready-to-copy WhatsApp onboarding card with credentials and ports. | `slice invite danz` |
| `slice gpu attach <name>` | Grants the slice direct access to the NVIDIA GTX 1650 GPU. | `slice gpu attach danz` |
| `slice gpu detach <name>` | Reclaims GPU access back to the host. | `slice gpu detach danz` |
| `slice port add <name> <port>` | Forwards an additional custom port from host to slice. | `slice port add danz 8080` |
| `slice port list <name>` | Lists all active port forwardings for a specific slice. | `slice port list danz` |
| `slice enter <name>` | Opens an instant interactive root shell inside the container (emergency rescue). | `slice enter danz` |
| `slice start / stop / restart` | Controls the lifecycle of a slice container. | `slice restart danz` |
| `slice delete <name> [--purge]` | Destroys the slice instance (optionally wiping persistent data). | `slice delete danz --purge` |

---

## 11. 📩 Onboarding & Developer Experience

Upon provisioning via `slice create <name>`, the administrator executes `slice invite <name>`, producing a formal, professional invitation card:

```text
======================================================================
  🍰 PANDUAN AKSES LINGKUNGAN PRIVATE CLOUD VPS: 'SLICE'
======================================================================
Yth. Rekan Pengembang / danz,

Lingkungan Private VPS mandiri Anda pada node 'playfam1' telah aktif.

Spesifikasi Sumber Daya (Dedicated Slice):
• Sistem Operasi         : Ubuntu 24.04 LTS (Native systemd)
• Alokasi Memori (RAM)   : 4.0 GB Dedicated (Hardcap)
• Alokasi Prosesor (CPU) : 4 vCPU (Dynamic Burst)
• Alokasi Penyimpanan    : 200 GB Storage (High-Speed SATA)
• Akses Administratif    : Full Sudo / Root Access di dalam VPS
• Dukungan Docker        : Native Docker & Docker Compose Enabled

Informasi Akses SSH:
• Host Jaringan (Tailscale) : 100.108.185.46
• Host Jaringan (Wi-Fi)     : 192.168.20.193
• Port SSH Layanan          : 2211
• Nama Pengguna (Username)  : danz
• Kata Sandi Sementara      : [REDACTED]

Jatah Port Development (Testing Web / API / DB):
• Port Forward Aktif : 3101 s/d 3105 (Host ──► VPS Anda)

Perintah Menghubungkan (Terminal Mac / Linux / PowerShell):
ssh danz@100.108.185.46 -p 2211

Catatan Keamanan:
Disarankan untuk segera mendaftarkan SSH Public Key Anda pada file
~/.ssh/authorized_keys dan memperbarui kata sandi awal Anda.
======================================================================
```

---

## 12. 🚀 Phased Implementation Roadmap

* **Phase 1: Host Preparation & Hygiene (ETA: Day 1)**
  - Implement lid switch ignore and mask sleep targets in systemd.
  - Verify network parameters and Tailscale routing.
* **Phase 2: Incus Engine & Storage Initialization (ETA: Day 1)**
  - Install Incus from official Linux Containers repositories.
  - Initialize `slice-pool` on `/dev/sda2` (200GB quota capabilities).
  - Provision virtual bridge `slicebr0`.
* **Phase 3: Directory Blueprint & CLI Engineering (ETA: Day 2)**
  - Construct `/srv/slice/` workspace.
  - Implement `/usr/local/bin/slice` orchestrator script with full vocabulary.
  - Configure cloud-init automation templates and unprivileged profiles.
* **Phase 4: Pilot Testing & Verification (ETA: Day 2)**
  - Spin up pilot slice `slice-pilot` on port 2211.
  - Test SSH login, `systemctl` service management, and nested Docker installation.
  - Validate 4GB RAM ceiling and dynamic CPU limits.
* **Phase 5: Production Handover (ETA: Day 3)**
  - Provision slices for designated developer peers.
  - Dispatch onboarding cards and conduct orientation.

---

<p align="center">
  <b>SLICE: High-Performance Private Cloud VPS Infrastructure</b><br>
  <i>Designed & Maintained by ATNX 🖤⚡ · Node playfam1 · Telkom OPMC</i>
</p>
