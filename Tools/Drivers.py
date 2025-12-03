# Tools/drivers.py

import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


def run_powershell(ps_command):
    """
    Helper to run a PowerShell command and return stdout or an error message.
    """
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if completed.returncode != 0:
            return "[ERROR]\n" + (completed.stderr.strip() or "Unknown PowerShell error.")
        return completed.stdout.strip()
    except Exception as e:
        return "[EXCEPTION]\n{0}".format(e)


def _get_days_from_ps(ps_snippet):
    """
    Run a PowerShell snippet that should output a single integer (days).
    Returns int or None.
    """
    out = run_powershell(ps_snippet).strip()
    try:
        return int(out)
    except Exception:
        return None


def _classify_age(days, ok_max, warn_max):
    """
    Classify 'age in days' into OK / WARNING / OUTDATED / UNKNOWN.
    """
    if days is None:
        return "UNKNOWN"

    if days <= ok_max:
        return "OK"
    elif days <= warn_max:
        return "WARNING"
    else:
        return "OUTDATED"


def generate_health_summary():
    """
    Build a short, human-readable health summary with status labels.
    """

    # Age in days since last Windows update installed
    wu_days = _get_days_from_ps(r"""
        $u = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1
        if ($u) { (New-TimeSpan -Start $u.InstalledOn -End (Get-Date)).Days } else { "" }
    """)

    # Age in days since BIOS release
    bios_days = _get_days_from_ps(r"""
        $bios = Get-CimInstance -ClassName Win32_BIOS
        if ($bios) { (New-TimeSpan -Start $bios.ReleaseDate -End (Get-Date)).Days } else { "" }
    """)

    # Age in days since latest DISPLAY (GPU) driver
    gpu_days = _get_days_from_ps(r"""
        $drv = Get-WmiObject Win32_PnPSignedDriver |
            Where-Object { $_.DeviceClass -eq 'DISPLAY' } |
            Sort-Object DriverDate -Descending |
            Select-Object -First 1
        if ($drv) { (New-TimeSpan -Start $drv.DriverDate -End (Get-Date)).Days } else { "" }
    """)

    # Age in days since latest NET (network) driver
    net_days = _get_days_from_ps(r"""
        $drv = Get-WmiObject Win32_PnPSignedDriver |
            Where-Object { $_.DeviceClass -eq 'NET' } |
            Sort-Object DriverDate -Descending |
            Select-Object -First 1
        if ($drv) { (New-TimeSpan -Start $drv.DriverDate -End (Get-Date)).Days } else { "" }
    """)

    # Thresholds (in days)
    # Windows Updates: OK <= 60, WARNING <= 90, OUTDATED > 90
    wu_status = _classify_age(wu_days, ok_max=60, warn_max=90)

    # BIOS: OK <= 730 days (~2y), WARNING <= 1095 (~3y), OUTDATED > 3y
    bios_status = _classify_age(bios_days, ok_max=730, warn_max=1095)

    # GPU driver: OK <= 365 days, WARNING <= 730, OUTDATED > 2y
    gpu_status = _classify_age(gpu_days, ok_max=365, warn_max=730)

    # Network driver: OK <= 730 days (~2y), WARNING <= 1095, OUTDATED > 3y
    net_status = _classify_age(net_days, ok_max=730, warn_max=1095)

    lines = []
    lines.append("=== Update & Driver Health Summary ===")

    if wu_days is not None:
        lines.append("Windows Updates: {0} (last installed ~{1} days ago)".format(wu_status, wu_days))
    else:
        lines.append("Windows Updates: UNKNOWN (no data)")

    if bios_days is not None:
        lines.append("BIOS: {0} (last update ~{1} days ago)".format(bios_status, bios_days))
    else:
        lines.append("BIOS: UNKNOWN (no data)")

    if gpu_days is not None:
        lines.append("Display Driver: {0} (last update ~{1} days ago)".format(gpu_status, gpu_days))
    else:
        lines.append("Display Driver: UNKNOWN (no data)")

    if net_days is not None:
        lines.append("Network Driver: {0} (last update ~{1} days ago)".format(net_status, net_days))
    else:
        lines.append("Network Driver: UNKNOWN (no data)")

    lines.append("")  # blank line after summary
    return "\n".join(lines)


def generate_update_driver_report():
    """
    Build a multi-section text report for OS, updates, and key driver info.
    Includes a health summary at the top.
    """
    lines = []

    # === Health Summary ===
    lines.append(generate_health_summary())

    # === OS & Build ===
    try:
        os_name = platform.system()
        os_release = platform.release()
        os_version = platform.version()
        arch = platform.machine()
        full_platform = platform.platform()
        lines.append("=== OS & Build ===")
        lines.append(full_platform)
        lines.append("System: {0} {1}".format(os_name, os_release))
        lines.append("Version: {0}".format(os_version))
        lines.append("Architecture: {0}".format(arch))
        lines.append("")  # blank line
    except Exception as e:
        lines.append("=== OS & Build ===")
        lines.append("Error getting OS info: {0}".format(e))
        lines.append("")

    # === Hardware & BIOS ===
    hw_cmd = r"""
    $cs = Get-CimInstance -ClassName Win32_ComputerSystem
    $bios = Get-CimInstance -ClassName Win32_BIOS
    [PSCustomObject]@{
        Manufacturer = $cs.Manufacturer
        Model        = $cs.Model
        BIOSVersion  = ($bios.SMBIOSBIOSVersion -join ', ')
        BIOSDate     = $bios.ReleaseDate
    } | Format-List
    """
    lines.append("=== Hardware & BIOS ===")
    lines.append(run_powershell(hw_cmd))
    lines.append("")

    # === Recent Windows Updates ===
    updates_cmd = r"""
    Get-HotFix |
        Sort-Object InstalledOn -Descending |
        Select-Object -First 5 HotFixID, InstalledOn, Description |
        Format-Table -AutoSize
    """
    lines.append("=== Recent Windows Updates (Top 5) ===")
    lines.append(run_powershell(updates_cmd))
    lines.append("")

    # === Display (GPU) Drivers ===
    display_cmd = r"""
    Get-WmiObject Win32_PnPSignedDriver |
        Where-Object { $_.DeviceClass -eq 'DISPLAY' } |
        Select-Object DeviceName, DriverVersion, DriverDate |
        Sort-Object DriverDate -Descending |
        Format-Table -AutoSize
    """
    lines.append("=== Display Drivers ===")
    lines.append(run_powershell(display_cmd))
    lines.append("")

    # === Network Drivers ===
    net_cmd = r"""
    Get-WmiObject Win32_PnPSignedDriver |
        Where-Object { $_.DeviceClass -eq 'NET' } |
        Select-Object DeviceName, DriverVersion, DriverDate |
        Sort-Object DriverDate -Descending |
        Format-Table -AutoSize
    """
    lines.append("=== Network Drivers ===")
    lines.append(run_powershell(net_cmd))
    lines.append("")

    return "\n".join(lines)


def open_update_driver_checker(parent):
    """
    Opens a new window that generates and displays an Update & Driver Status report.
    `parent` should be your main Tk() or Toplevel() instance.
    """
    win = tk.Toplevel(parent)
    win.title("Update & Driver Status Checker")
    win.geometry("900x600")

    # Top frame (title + button)
    top_frame = ttk.Frame(win)
    top_frame.pack(fill="x", padx=10, pady=5)

    title_label = ttk.Label(
        top_frame,
        text="Update & Driver Status Checker",
        font=("Segoe UI", 12, "bold")
    )
    title_label.pack(side="left")

    run_btn = ttk.Button(top_frame, text="Run Check")
    run_btn.pack(side="right", padx=5)

    # Scrolling text area for report
    text_area = scrolledtext.ScrolledText(
        win,
        wrap="word",
        font=("Consolas", 9)
    )
    text_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # Configure tags for highlighting statuses
    text_area.tag_configure("status_ok", foreground="lime green")
    text_area.tag_configure("status_warn", foreground="orange")
    text_area.tag_configure("status_bad", foreground="red")

    # Status bar
    status_var = tk.StringVar(value="Click 'Run Check' to generate report.")
    status_bar = ttk.Label(win, textvariable=status_var, anchor="w")
    status_bar.pack(fill="x", padx=10, pady=(0, 5))

    def highlight_status_words():
        """
        Find OK / WARNING / OUTDATED in the text and color them.
        """
        for word, tag in [
            ("OK", "status_ok"),
            ("WARNING", "status_warn"),
            ("OUTDATED", "status_bad")
        ]:
            start = "1.0"
            while True:
                pos = text_area.search(word, start, stopindex="end")
                if not pos:
                    break
                end = "{0}+{1}c".format(pos, len(word))
                text_area.tag_add(tag, pos, end)
                start = end

    def do_check():
        run_btn.config(state="disabled")
        status_var.set("Running checks... this may take a few seconds.")
        text_area.delete("1.0", tk.END)
        win.update_idletasks()

        try:
            report = generate_update_driver_report()
            text_area.insert(tk.END, report)
            highlight_status_words()
            status_var.set("Check complete.")
        except Exception as e:
            messagebox.showerror("Error", "An error occurred:\n{0}".format(e))
            status_var.set("Error during check. See message.")
        finally:
            run_btn.config(state="normal")

    run_btn.config(command=do_check)
