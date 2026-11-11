#!/usr/bin/env python3
import sys
import subprocess

CYAN = "\033[38;5;51m"
MAGENTA = "\033[38;5;201m"
BOLD = "\033[1m"
RESET = "\033[0m"

user_name = sys.argv[1].upper() if len(sys.argv) > 1 else "USER"

slice_art = [
    "   _____ __    ________________",
    "  / ___// /   /  _/ ____/ ____/",
    "  \\__ \\/ /    / // /   / __/   ",
    " ___/ / /____/ // /___/ /___   ",
    "/____/_____/___/\\____/_____/   "
]

# Generate user ASCII slant via figlet
try:
    cmd = ["figlet", "-f", "slant", user_name]
    res = subprocess.check_output(cmd, text=True).splitlines()
    # Filter empty lines
    user_art = [l for l in res if l.strip()]
except Exception:
    user_art = []

if len(user_art) >= 5:
    for s, u in zip(slice_art, user_art[:5]):
        print(f"{CYAN}{BOLD}{s}{RESET}    {MAGENTA}{BOLD}{u}{RESET}")
else:
    for s in slice_art:
        print(f"{CYAN}{BOLD}{s}{RESET}")
    print(f"                                      {MAGENTA}{BOLD}[ {user_name} ]{RESET}")
