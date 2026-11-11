#!/usr/bin/env python3
import sys
import json
import os
import subprocess
import time

# ANSI Colors
CYAN = "\033[38;5;51m"
GREEN = "\033[38;5;82m"
YELLOW = "\033[38;5;220m"
RED = "\033[38;5;196m"
WHITE = "\033[1;37m"
GRAY = "\033[38;5;242m"
MAGENTA = "\033[38;5;201m"
BOLD = "\033[1m"
RESET = "\033[0m"

STATE_FILE = "/srv/slice/state/slice-state.json"

def format_bytes(b):
    if b is None or b == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024.0:
            return f"{b:.1f} {unit}"
        b /= 1024.0
    return f"{b:.1f} PB"

def make_progress_bar(pct, width=8):
    filled = int(round(width * pct / 100))
    filled = min(width, max(0, filled))
    empty = width - filled
    
    if pct < 70:
        bar_color = GREEN
    elif pct < 85:
        bar_color = YELLOW
    else:
        bar_color = RED
        
    return f"{bar_color}[{'■' * filled}{' ' * empty}]{RESET} {pct:>2}%"

def get_pure_anon_memory(instance_name):
    """
    Mengekstrak memori murni proses (anon memory) dari CGroup v2,
    mengabaikan page cache sementara agar metrik 100% akurat.
    """
    try:
        cmd = ["sudo", "incus", "exec", instance_name, "--", "cat", "/sys/fs/cgroup/memory.stat"]
        out = subprocess.check_output(cmd, text=True, timeout=2)
        for line in out.splitlines():
            if line.startswith("anon "):
                return int(line.split()[1])
    except Exception:
        pass
    return None

def fetch_instances():
    try:
        out = subprocess.check_output(["sudo", "incus", "list", "--format", "json"], text=True)
        return json.loads(out)
    except Exception:
        return []

def render_list(instances):
    state_data = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                state_data = json.load(f)
        except Exception:
            pass

    slice_instances = [i for i in instances if i.get('name', '').startswith('slice-')]
    
    print(f"{CYAN}{BOLD}┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{CYAN}{BOLD}│  🍰 SLICE PRIVATE CLOUD — ACTIVE INSTANCES FLEET                                                       │{RESET}")
    print(f"{CYAN}{BOLD}└────────────────────────────────────────────────────────────────────────────────────────────────────────┘{RESET}")
    print(f"  • Host Node: {WHITE}playfam1 (36.66.72.42){RESET}  │  Mesh IP: {WHITE}100.108.185.46{RESET}  │  Engine: {GREEN}Incus 6.0 LTS{RESET}")
    print()
    
    print(f"{GRAY}┌──────────────┬─────────────┬─────────────────┬──────────┬──────────────────────┬─────────┬───────────────────┐{RESET}")
    print(f"{GRAY}│{RESET} {BOLD}{'INSTANCE':<12}{RESET} {GRAY}│{RESET} {BOLD}{'STATUS':<11}{RESET} {GRAY}│{RESET} {BOLD}{'PRIVATE IP':<15}{RESET} {GRAY}│{RESET} {BOLD}{'SSH PORT':<8}{RESET} {GRAY}│{RESET} {BOLD}{'ACTIVE RAM / MAX':<20}{RESET} {GRAY}│{RESET} {BOLD}{'VCPU':<7}{RESET} {GRAY}│{RESET} {BOLD}{'DEV PORTS':<17}{RESET} {GRAY}│{RESET}")
    print(f"{GRAY}├──────────────┼─────────────┼─────────────────┼──────────┼──────────────────────┼─────────┼───────────────────┤{RESET}")
    
    if not slice_instances:
        print(f"{GRAY}│{RESET} {YELLOW}{'No active SLICE instances found. Run \"slice create <name>\" to provision one.':<98}{RESET} {GRAY}│{RESET}")
    else:
        for item in slice_instances:
            full_name = item.get('name', '')
            name = full_name.replace('slice-', '')
            st = item.get('status', 'Unknown')
            
            if st.lower() == 'running':
                st_str = f"{GREEN}● ACTIVE{RESET}   "
                # Ambil anon memory murni
                anon_bytes = get_pure_anon_memory(full_name)
                mem_total_bytes = item.get('state', {}).get('memory', {}).get('total', 4294967296)
                if anon_bytes is None:
                    anon_bytes = item.get('state', {}).get('memory', {}).get('usage', 0)
                mem_str = f"{format_bytes(anon_bytes)} / {format_bytes(mem_total_bytes)}"
            else:
                st_str = f"{RED}○ STOPPED{RESET}  "
                mem_str = "0 B / 4.0 GB"
                
            eth0 = item.get('state', {}).get('network', {}).get('eth0', {})
            addresses = eth0.get('addresses', []) if eth0 else []
            ipv4 = next((a['address'] for a in addresses if a.get('family') == 'inet'), '-')
            
            user_state = state_data.get(name, {})
            ssh_port = str(user_state.get('port', '-'))
            dev_ports = str(user_state.get('dev_ports', '-'))
            
            cpus = item.get('config', {}).get('limits.cpu', '4')
            cpu_str = f"{cpus} vCPU"
            
            print(f"{GRAY}│{RESET} {WHITE}{BOLD}{name:<12}{RESET} {GRAY}│{RESET} {st_str:<20} {GRAY}│{RESET} {CYAN}{ipv4:<15}{RESET} {GRAY}│{RESET} {YELLOW}{ssh_port:<8}{RESET} {GRAY}│{RESET} {GREEN}{mem_str:<20}{RESET} {GRAY}│{RESET} {cpu_str:<7} {GRAY}│{RESET} {GRAY}{dev_ports:<17}{RESET} {GRAY}│{RESET}")
            
    print(f"{GRAY}└──────────────┴─────────────┴─────────────────┴──────────┴──────────────────────┴─────────┴───────────────────┘{RESET}")
    print(f"  {GRAY}💡 Quick Connect: {WHITE}ssh <name>@36.66.72.42 -p <port>{GRAY}  │  Manage: {CYAN}slice invite <name>{RESET}")
    print()

def render_stats(instances):
    slice_instances = [i for i in instances if i.get('name', '').startswith('slice-')]
    
    now_str = time.strftime('%H:%M:%S')
    print(f"{CYAN}{BOLD}┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{CYAN}{BOLD}│  📊 SLICE REALTIME TELEMETRY & HARDWARE USAGE MONITOR  [{WHITE}{now_str}{CYAN}{BOLD}]                                  │{RESET}")
    print(f"{CYAN}{BOLD}└────────────────────────────────────────────────────────────────────────────────────────────────────────┘{RESET}")
    print(f"  • Host CPU: {WHITE}i7-10750H (12 Cores){RESET}  │  System Memory: {WHITE}16 GB DDR4{RESET}  │  Storage Pool: {GREEN}SATA 1TB{RESET}")
    print()
    
    print(f"{GRAY}┌──────────────┬─────────────┬──────────────────────────┬────────────────┬──────────┬────────────────────────┐{RESET}")
    print(f"{GRAY}│{RESET} {BOLD}{'INSTANCE':<12}{RESET} {GRAY}│{RESET} {BOLD}{'STATUS':<11}{RESET} {GRAY}│{RESET} {BOLD}{'PROCESS RAM / LIMIT':<24}{RESET} {GRAY}│{RESET} {BOLD}{'RAM PRESSURE':<14}{RESET} {GRAY}│{RESET} {BOLD}{'PIDS':<8}{RESET} {GRAY}│{RESET} {BOLD}{'NET I/O (RX / TX)':<22}{RESET} {GRAY}│{RESET}")
    print(f"{GRAY}├──────────────┼─────────────┼──────────────────────────┼────────────────┼──────────┼────────────────────────┤{RESET}")
    
    if not slice_instances:
        print(f"{GRAY}│{RESET} {YELLOW}{'No active SLICE instances to monitor.':<98}{RESET} {GRAY}│{RESET}")
    else:
        for item in slice_instances:
            full_name = item.get('name', '')
            name = full_name.replace('slice-', '')
            st = item.get('status', 'Unknown')
            
            if st.lower() == 'running':
                st_str = f"{GREEN}● ACTIVE{RESET}   "
                anon_bytes = get_pure_anon_memory(full_name)
                mem_total_bytes = item.get('state', {}).get('memory', {}).get('total', 4294967296)
                if anon_bytes is None:
                    anon_bytes = item.get('state', {}).get('memory', {}).get('usage', 0)
                pct = int((anon_bytes / mem_total_bytes) * 100) if mem_total_bytes > 0 else 0
                bar = make_progress_bar(pct, width=6)
                mem_str = f"{format_bytes(anon_bytes)} / {format_bytes(mem_total_bytes)}"
            else:
                st_str = f"{RED}○ STOPPED{RESET}  "
                mem_str = "0 B / 4.0 GB"
                bar = f"{GRAY}[      ]  0%{RESET}"
                
            pids = item.get('state', {}).get('processes', 0)
            pid_str = f"{pids} / 500"
            
            eth0 = item.get('state', {}).get('network', {}).get('eth0', {})
            counters = eth0.get('counters', {}) if eth0 else {}
            rx = format_bytes(counters.get('bytes_received', 0))
            tx = format_bytes(counters.get('bytes_sent', 0))
            net_str = f"{rx} / {tx}"
            
            print(f"{GRAY}│{RESET} {WHITE}{BOLD}{name:<12}{RESET} {GRAY}│{RESET} {st_str:<20} {GRAY}│{RESET} {GREEN}{mem_str:<24}{RESET} {GRAY}│{RESET} {bar:<23} {GRAY}│{RESET} {pid_str:<8} {GRAY}│{RESET} {net_str:<22} {GRAY}│{RESET}")
            
    print(f"{GRAY}└──────────────┴─────────────┴──────────────────────────┴────────────────┴──────────┴────────────────────────┘{RESET}")
    print()

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'list'
    watch_mode = any(arg in ['-w', '--watch', 'watch'] for arg in sys.argv)
    
    if watch_mode or mode in ['top', 'watch']:
        try:
            while True:
                # ANSI clear screen and move cursor to top-left
                sys.stdout.write("\033[H\033[2J")
                sys.stdout.flush()
                data = fetch_instances()
                render_stats(data)
                print(f"  {GRAY}Auto-refreshing every 2s. Press {WHITE}{BOLD}Ctrl+C{RESET}{GRAY} to exit live monitor.{RESET}")
                time.sleep(2)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[*] Live telemetry session terminated.{RESET}")
    else:
        # One-shot render
        if not sys.stdin.isatty():
            try:
                data = json.load(sys.stdin)
            except Exception:
                data = fetch_instances()
        else:
            data = fetch_instances()
            
        if mode == 'stats':
            render_stats(data)
        else:
            render_list(data)
