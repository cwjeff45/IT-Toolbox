# SystemReport.py - UPDATED WITH WORKGROUP + TPM SUPPORT

import subprocess
import os
import platform
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


def run_cmd(cmd):
    """Runs a command and returns output as text (or empty string on failure)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    except Exception:
        return ""


def get_first_data_line(output):
    """Helper that returns the first real value after a WMIC/PowerShell header."""
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    return lines[1] if len(lines) >= 2 else "Unknown"


def get_mac_address():
    output = run_cmd("getmac")
    for line in output.split("\n"):
        line = line.strip()
        if "-" in line and ("Disconnected" not in line):
            parts = line.split()
            if parts:
                return parts[0]
    return "Unknown"


def get_ipv4():
    output = run_cmd("ipconfig")
    for line in output.splitlines():
        line = line.strip()
        if "IPv4" in line and ":" in line:
            return line.split(":", 1)[1].strip()
    return "Unknown"


def get_dns():
    output = run_cmd("ipconfig /all")
    dns_servers = []
    record = False

    for line in output.split("\n"):
        if "DNS Servers" in line:
            record = True
            dns_servers.append(line.split(":", 1)[1].strip())
        elif record:
            stripped = line.strip()
            if stripped == "":
                break
            dns_servers.append(stripped)

    return ", ".join(dns_servers) if dns_servers else "Unknown"


def get_last_update():
    ps = '(Get-HotFix | sort InstalledOn -Descending | select -first 1).InstalledOn'
    result = run_cmd(f'powershell -command "{ps}"')
    return result if result else "Unknown"


def get_antivirus_status():
    ps_cmd = '(Get-MpComputerStatus).RealTimeProtectionEnabled'
    output = run_cmd(f'powershell -command "{ps_cmd}"')
    if "True" in output:
        return "On"
    if "False" in output:
        return "Off"
    return "Unknown"


def get_workgroup():
    """Return domain name or 'Workgroup' if in a workgroup."""
    ps = '(Get-CimInstance Win32_ComputerSystem).Domain'
    result = run_cmd(f'powershell -command "{ps}"').strip()

    if not result or result.lower() == "workgroup":
        return "Workgroup"

    return result


def get_tpm_status():
    """
    Return a human-friendly TPM status string using PowerShell Get-Tpm.
    Possible outputs:
        - 'Enabled'
        - 'Present but not fully enabled'
        - 'Not Present'
        - 'Unknown'
    """
    ps = (
        "if (Get-Command Get-Tpm -ErrorAction SilentlyContinue) { "
        "$t = Get-Tpm; "
        "if (-not $t.TpmPresent) {'Not Present'} "
        "elseif ($t.TpmPresent -and $t.TpmEnabled -and $t.TpmReady) {'Enabled'} "
        "else {'Present but not fully enabled'} "
        "} else {'Unknown'}"
    )
    result = run_cmd(f'powershell -command "{ps}"').strip()
    return result if result else "Unknown"


# ----------------- Generate Report -----------------

def generate_system_report():
    hostname = platform.node() or "Unknown"

    try:
        user = os.getlogin()
    except Exception:
        user = os.environ.get("USERNAME", "Unknown")

    system = platform.system()
    version = platform.version()
    release = platform.release()
    arch = platform.machine()

    # Manufacturer / Model
    manufacturer = run_cmd(
        'powershell -command "(Get-CimInstance Win32_ComputerSystem).Manufacturer"'
    ).strip() or "Unknown"
    model = run_cmd(
        'powershell -command "(Get-CimInstance Win32_ComputerSystem).Model"'
    ).strip() or "Unknown"

    # CPU
    cpu = run_cmd(
        'powershell -command "(Get-CimInstance Win32_Processor).Name"'
    ).strip() or "Unknown"

    # RAM (GB)
    out_ram = run_cmd(
        'powershell -command "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"'
    ).strip()
    try:
        ram_gb = round(int(out_ram) / (1024 ** 3), 2)
    except Exception:
        ram_gb = "Unknown"

    # Drive C via PowerShell
    out_drive = run_cmd(
        'powershell -command "$d = Get-CimInstance Win32_LogicalDisk -Filter \\"DeviceID=\'C:\'\\"; '
        'if ($d) { $d.Size; $d.FreeSpace }"'
    ).strip()

    size_gb = free_gb = "Unknown"
    if out_drive:
        lines = [l.strip() for l in out_drive.splitlines() if l.strip()]
        if len(lines) >= 2:
            try:
                size_gb = round(int(lines[0]) / (1024 ** 3), 2)
                free_gb = round(int(lines[1]) / (1024 ** 3), 2)
            except Exception:
                pass

    # Network + Security Info
    ipv4 = get_ipv4()
    mac = get_mac_address()
    dns = get_dns()
    last_update = get_last_update()
    av_status = get_antivirus_status()
    workgroup = get_workgroup()
    tpm_status = get_tpm_status()

    report = f"""
=== System Report ===

User: {user}
Computer Name: {hostname}
Model: {manufacturer} {model}

OS: {system} {release} ({arch})
Build Version: {version}

CPU: {cpu}
RAM: {ram_gb} GB
Drive C: {size_gb} GB total, {free_gb} GB free

IPv4 Address: {ipv4}
MAC Address: {mac}
DNS Servers: {dns}
Workgroup / Domain: {workgroup}
TPM Status: {tpm_status}

Antivirus: Microsoft Defender (Real-time Protection: {av_status})
Last Windows Update: {last_update}
"""

    return report.strip()


# ----------------- GUI -----------------

def open_system_report(parent):
    """Creates a window displaying and allowing copying of the system report."""
    win = tk.Toplevel(parent)
    win.title("System Report")
    win.geometry("800x500")

    report = generate_system_report()

    text_box = scrolledtext.ScrolledText(
        win, width=100, height=25, font=("Consolas", 10)
    )
    text_box.pack(padx=10, pady=10, fill="both", expand=True)
    text_box.insert("1.0", report)

    def copy_to_clipboard():
        win.clipboard_clear()
        win.clipboard_append(report)
        messagebox.showinfo("Copied", "System report copied to clipboard.")

    btn_frame = ttk.Frame(win)
    btn_frame.pack(pady=8)

    ttk.Button(btn_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(
        side="left", padx=5
    )
