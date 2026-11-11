#!/usr/bin/env bash
set -e

# ==============================================================================
# SLICE · Private Cloud System Container Engine — Automated Installer
# Supported OS: Ubuntu 24.04 LTS (Noble Numbat)
# ==============================================================================

CYAN="\033[38;5;51m"
GREEN="\033[38;5;82m"
YELLOW="\033[38;5;220m"
RED="\033[38;5;196m"
WHITE="\033[1;37m"
GRAY="\033[38;5;242m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${CYAN}${BOLD}"
echo "    _____ __    ________________"
echo "   / ___// /   /  _/ ____/ ____/"
echo "   \\__ \\/ /    / // /   / __/   "
echo "  ___/ / /____/ // /___/ /___   "
echo " /____/_____/___/\\____/_____/   "
echo -e "  SLICE · Private Cloud VPS Engine Installer 🍰⚡${RESET}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] Error: Please run this installer as root or with sudo.${RESET}"
    exit 1
fi

echo -e "${CYAN}[1/6] Installing Incus 6.0 LTS and prerequisite dependencies...${RESET}"
apt-get update -y
apt-get install -y incus incus-client btrfs-progs iptables-persistent fail2ban figlet python3 curl git

echo -e "${CYAN}[2/6] Configuring Laptop Hygiene (Prevent sleep on lid close)...${RESET}"
if [ -f /etc/systemd/logind.conf ]; then
    sed -i 's/^#*HandleLidSwitch=.*/HandleLidSwitch=ignore/' /etc/systemd/logind.conf
    sed -i 's/^#*HandleLidSwitchExternalPower=.*/HandleLidSwitchExternalPower=ignore/' /etc/systemd/logind.conf
    systemctl restart systemd-logind 2>/dev/null || true
fi
systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target 2>/dev/null || true

echo -e "${CYAN}[3/6] Setting up SLICE workspace directories...${RESET}"
mkdir -p /srv/slice/{bin,templates,state}
cp bin/slice /srv/slice/bin/slice
cp bin/slice_stats_formatter.py /srv/slice/bin/slice_stats_formatter.py
cp templates/* /srv/slice/templates/
chmod -R 755 /srv/slice/bin /srv/slice/templates
chmod -R 775 /srv/slice/state

# Symlink CLI to PATH
ln -sf /srv/slice/bin/slice /usr/local/bin/slice

echo -e "${CYAN}[4/6] Initializing Incus storage pool and virtual network bridge...${RESET}"
if ! incus storage show slice-pool >/dev/null 2>&1; then
    incus storage create slice-pool dir
fi

if ! incus network show slicebr0 >/dev/null 2>&1; then
    incus network create slicebr0 ipv4.address=10.150.0.1/24 ipv4.nat=true ipv6.address=none
fi

# Configure default profile
incus profile device add default root disk path=/ pool=slice-pool 2>/dev/null || true
incus profile device add default eth0 nic network=slicebr0 name=eth0 2>/dev/null || true
incus profile set default boot.autostart=true
incus profile set default security.nesting=true
incus profile set default limits.processes=500

echo -e "${CYAN}[5/6] Hardening Firewall & Fail2ban Brute-Force Shield...${RESET}"
iptables -I INPUT -p tcp -m multiport --dports 2211:2230 -m state --state NEW -m recent --set --name SLICE_SSH 2>/dev/null || true
iptables -I INPUT -p tcp -m multiport --dports 2211:2230 -m state --state NEW -m recent --update --seconds 60 --hitcount 6 --name SLICE_SSH -j DROP 2>/dev/null || true
netfilter-persistent save >/dev/null 2>&1 || true

cat << 'EOF' > /etc/fail2ban/jail.local
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port    = 22,2211:2230
backend = systemd
EOF
systemctl restart fail2ban 2>/dev/null || true

echo -e "${CYAN}[6/6] Installing bash autocompletion...${RESET}"
if [ -f completions/slice.bash ]; then
    cp completions/slice.bash /etc/bash_completion.d/slice
fi

echo ""
echo -e "${GREEN}${BOLD}[✓] SLICE Private Cloud Engine INSTALLED SUCCESSFULLY!${RESET}"
echo -e "Run '${CYAN}slice${RESET}' to get started."
