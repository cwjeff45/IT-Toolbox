import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import datetime
import os
import threading
import ctypes
import sys


# ---------- Admin helpers ----------

def is_admin():
    """Return True if the current process is running with admin rights."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def restart_as_admin_and_exit():
    """
    Restart this app with Administrator rights via UAC, then exit this instance.
    Handles both frozen EXE (PyInstaller) and plain Python script.
    """
    # Make sure there is a Tk root for error dialogs if needed
    root = tk._default_root
    if root is None:
        root = tk.Tk()
        root.withdraw()

    try:
        if getattr(sys, "frozen", False):
            # Frozen EXE (e.g. PyInstaller) — sys.executable IS the .exe
            exe = sys.executable
            params = " ".join(sys.argv[1:])
        else:
            # Running as script: use python.exe and pass the script path as the first arg
            exe = sys.executable
            script = os.path.abspath(sys.argv[0])
            other = " ".join(sys.argv[1:])
            params = f"\"{script}\" {other}".strip()

        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            exe,
            params,
            None,
            1
        )
    except Exception as e:
        messagebox.showerror(
            "Elevation Failed",
            f"Could not restart with admin rights:\n{e}"
        )
    # Exit this (non-admin) process either way
    sys.exit(0)


# ---------- Low-level helpers ----------

def run_cmd(command, shell=False):
    """Run a command (CMD or PowerShell) and return a dict result."""
    try:
        completed = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True
        )
        return {
            "success": completed.returncode == 0,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Exception while running command: {e}",
            "returncode": -1
        }


def run_powershell(ps_command):
    """Run a PowerShell command string and return dict result."""
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command", ps_command
    ]
    return run_cmd(cmd)


def trim_text(text, limit=4000):
    """Trim very long outputs so the report window doesn't explode."""
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... [output truncated] ..."


# ---------- Individual tasks ----------

def task_windows_update_cleanup():
    name = "Clear Windows Update Cleanup (DISM StartComponentCleanup)"
    result = run_cmd(["dism", "/Online", "/Cleanup-Image", "/StartComponentCleanup"])
    summary = "Completed" if result["success"] else "FAILED"
    details = (
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}"
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_clean_thumbnail_cache():
    name = "Clean Thumbnail Cache"
    try:
        base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer")
        deleted = 0
        if os.path.isdir(base):
            for fname in os.listdir(base):
                if fname.lower().startswith("thumbcache") and fname.lower().endswith(".db"):
                    fpath = os.path.join(base, fname)
                    try:
                        os.remove(fpath)
                        deleted += 1
                    except Exception:
                        pass
        success = True
        summary = f"Deleted {deleted} thumbnail cache file(s)."
        details = f"Thumbnail cache path: {base}\nFiles deleted: {deleted}"
    except Exception as e:
        success = False
        summary = "FAILED"
        details = f"Error while cleaning thumbnail cache: {e}"
    return {"name": name, "success": success, "summary": summary, "details": details}


def task_defrag_and_optimize():
    name = "Defrag HDD / Optimize Drives"
    # /C = all drives, /O = optimize for media type (handles SSD/TRIM)
    result = run_cmd(["defrag", "/C", "/O"])
    summary = "Completed" if result["success"] else "FAILED"
    details = (
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}"
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_windows_store_temp_and_cache():
    name = "Clear Windows Store Cache (wsreset)"
    result = run_cmd(["wsreset.exe", "-i"])
    summary = "Completed (Store cache reset triggered)" if result["success"] else "FAILED"
    details = (
        "wsreset.exe output (often minimal or empty):\n"
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}"
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_defender_full_scan():
    name = "Microsoft Defender Full Scan"
    ps = "Start-MpScan -ScanType FullScan"
    result = run_powershell(ps)
    summary = (
        "Full scan started (check Defender for progress/results)"
        if result["success"] else "FAILED to start full scan"
    )
    details = (
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}"
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_suspicious_scheduled_tasks():
    name = "Check for Suspicious Scheduled Tasks (report-only)"
    ps = r"""
$tasks = Get-ScheduledTask | ForEach-Object {
    try {
        $a = $_ | Get-ScheduledTaskInfo -ErrorAction SilentlyContinue
        [PSCustomObject]@{
            TaskName = $_.TaskName
            TaskPath = $_.TaskPath
            LastRunTime = $a.LastRunTime
            NextRunTime = $a.NextRunTime
        }
    } catch {}
}
$tasks | Sort-Object TaskPath, TaskName | Format-Table -AutoSize
"""
    result = run_powershell(ps)
    summary = (
        "Scheduled tasks listed (no automatic removal in this version)."
        if result["success"] else "FAILED to list tasks"
    )
    details = (
        f"stdout (tasks):\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}\n\n"
        "NOTE: Removal of 'known malicious' tasks is not automated in this safe build. Review tasks manually."
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_startup_items():
    name = "Check Suspicious Startup Items (report-only)"
    ps = r"""
Get-CimInstance Win32_StartupCommand |
    Select-Object Name, Command, Location |
    Sort-Object Name |
    Format-Table -AutoSize
"""
    result = run_powershell(ps)
    summary = (
        "Startup items listed (no automatic removal)."
        if result["success"] else "FAILED to list startup items"
    )
    details = (
        f"stdout (startup items):\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}"
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_sfc_scannow():
    name = "System File Checker (sfc /scannow)"
    result = run_cmd(["sfc", "/scannow"])
    summary = "Completed (check output for details)" if result["success"] else "FAILED"
    details = (
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}"
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_dism_restorehealth():
    name = "DISM RestoreHealth"
    result = run_cmd(["dism", "/Online", "/Cleanup-Image", "/RestoreHealth"])
    summary = "Completed" if result["success"] else "FAILED"
    details = (
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}"
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_smart_health():
    name = "Check SMART / Disk Health"
    ps = r"""
Get-PhysicalDisk |
    Select-Object FriendlyName, MediaType, Size, HealthStatus |
    Format-Table -AutoSize
"""
    result = run_powershell(ps)
    summary = (
        "Disk health queried (see output)." if result["success"]
        else "FAILED to query disk health"
    )
    details = (
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}"
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_bloatware_report():
    name = "Bloatware Apps Report (no auto-removal)"
    ps = r"""
$patterns = @(
    "*xbox*", "*bing*", "*solitaire*", "*game*", "*spotify*",
    "*twitter*", "*tiktok*", "*facebook*", "*instagram*"
)
$apps = foreach ($p in $patterns) {
    Get-AppxPackage -Name $p -ErrorAction SilentlyContinue
}
$apps | Select-Object Name, PackageFullName | Sort-Object Name | Format-Table -AutoSize
"""
    result = run_powershell(ps)
    summary = (
        "Potential bloatware apps listed (no removal)."
        if result["success"] else "FAILED to list potential bloatware"
    )
    details = (
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}\n\n"
        "NOTE: Removal is intentionally not automated; review list and remove manually if desired."
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


def task_driver_report():
    name = "Driver Sweep Report (no auto-removal)"
    result = run_cmd(["pnputil", "/enum-drivers"])
    summary = (
        "Driver list collected (no removal)." if result["success"]
        else "FAILED to list drivers"
    )
    details = (
        f"stdout:\n{trim_text(result['stdout'])}\n\n"
        f"stderr:\n{trim_text(result['stderr'])}\n\n"
        "NOTE: Sweeping/removing drivers is not automated in this safe build."
    )
    return {"name": name, "success": result["success"], "summary": summary, "details": details}


# ---------- Results & export window ----------

def show_results_window(results, limited_mode, admin_now):
    """Show a window with detailed results, notes box, and export button."""
    root = tk._default_root
    if root is None:
        root = tk.Tk()
        root.withdraw()

    win = tk.Toplevel(root)
    win.title("Cleanup Suite Results")
    win.geometry("800x600")

    mode_desc = []
    mode_desc.append(f"Running as admin: {'YES' if admin_now else 'NO'}")
    mode_desc.append(f"Limited mode (admin-only tasks skipped): {'YES' if limited_mode else 'NO'}")

    lbl_mode = tk.Label(win, text=" | ".join(mode_desc), font=("Segoe UI", 8, "italic"))
    lbl_mode.pack(anchor="w", padx=10, pady=(8, 0))

    lbl_results = tk.Label(win, text="Task Results:", font=("Segoe UI", 10, "bold"))
    lbl_results.pack(anchor="w", padx=10, pady=(5, 0))

    txt_results = scrolledtext.ScrolledText(win, wrap=tk.WORD, height=20)
    txt_results.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    lines = []
    for res in results:
        status = "OK" if res["success"] else "FAILED/SKIPPED"
        lines.append(f"=== {res['name']} ===")
        lines.append(f"Status : {status}")
        lines.append(f"Summary: {res['summary']}")
        lines.append("")
        lines.append(res["details"])
        lines.append("\n")

    txt_results.insert("1.0", "\n".join(lines))
    txt_results.configure(state="disabled")

    lbl_notes = tk.Label(
        win,
        text="Notes (PC owner name, ticket #, observations):",
        font=("Segoe UI", 10, "bold")
    )
    lbl_notes.pack(anchor="w", padx=10, pady=(0, 2))

    txt_notes = tk.Text(win, height=4)
    txt_notes.pack(fill="x", padx=10, pady=(0, 10))

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", padx=10, pady=(0, 10))

    def export_report():
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        default_name = "CleanupReport_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
        path = filedialog.asksaveasfilename(
            parent=win,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=default_name,
            title="Save Cleanup Report"
        )
        if not path:
            return

        notes = txt_notes.get("1.0", "end").strip()

        report_lines = []
        report_lines.append("PC Cleanup Suite Report")
        report_lines.append(f"Date/Time: {timestamp}")
        report_lines.append("")
        report_lines.append(f"Running as admin: {'YES' if admin_now else 'NO'}")
        report_lines.append(f"Limited mode (admin-only tasks skipped): {'YES' if limited_mode else 'NO'}")
        report_lines.append("")

        if notes:
            report_lines.append("Notes:")
            report_lines.append(notes)
            report_lines.append("")

        report_lines.append("===== Task Results =====")
        report_lines.append(txt_results.get("1.0", "end").strip())

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(report_lines))
            messagebox.showinfo("Export Complete", f"Report saved to:\n{path}", parent=win)
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save report:\n{e}", parent=win)

    btn_export = tk.Button(btn_frame, text="Export Report", command=export_report, width=15)
    btn_export.pack(side="left", padx=(0, 10))

    btn_close = tk.Button(btn_frame, text="Close", command=win.destroy, width=10)
    btn_close.pack(side="right")


# ---------- Progress window + threaded runner ----------

def run_cleanup_suite():
    """
    Run all cleanup/diagnostic tasks in a background thread, while showing a
    progress window with a label and progress bar. When done, show results.

    If not running as admin:
      - Ask whether to run in limited mode (skip admin-only tasks), or
      - Restart the app with admin rights (UAC prompt).
    """
    # Overall confirmation
    proceed = messagebox.askyesno(
        "Confirm Cleanup Suite",
        "This will run multiple system maintenance commands (DISM, SFC, Defender full scan, defrag, etc.).\n\n"
        "These operations can take a long time and many of them work best when run as Administrator.\n\n"
        "Do you want to continue?"
    )
    if not proceed:
        return

    admin_now = is_admin()
    limited_mode = False

    if not admin_now:
        choice = messagebox.askyesno(
            "Admin Recommended",
            "You are currently NOT running this toolbox with elevated (Administrator) rights.\n\n"
            "Some tasks (DISM, SFC, defrag, driver listing, etc.) require admin.\n\n"
            "Yes  = Continue in LIMITED MODE (admin-only tasks will be marked as skipped).\n"
            "No   = Restart this app with Administrator rights (you will see a UAC prompt)."
        )
        if choice:
            # User chose LIMITED MODE
            limited_mode = True
        else:
            # User chose to restart as Admin
            restart_as_admin_and_exit()
            return  # just in case

    root = tk._default_root
    if root is None:
        root = tk.Tk()
        root.withdraw()

    # Define tasks as dicts with "label", "func", and "requires_admin"
    tasks = [
        {
            "label": "Clear Windows Update Cleanup (DISM StartComponentCleanup)",
            "func": task_windows_update_cleanup,
            "requires_admin": True
        },
        {
            "label": "Clean Thumbnail Cache",
            "func": task_clean_thumbnail_cache,
            "requires_admin": False
        },
        {
            "label": "Defrag HDD / Optimize Drives",
            "func": task_defrag_and_optimize,
            "requires_admin": True
        },
        {
            "label": "Clear Windows Store Cache (wsreset)",
            "func": task_windows_store_temp_and_cache,
            "requires_admin": False
        },
        {
            "label": "Microsoft Defender Full Scan",
            "func": task_defender_full_scan,
            "requires_admin": True
        },
        {
            "label": "Check Suspicious Scheduled Tasks (report-only)",
            "func": task_suspicious_scheduled_tasks,
            "requires_admin": False  # may show less info without admin but still useful
        },
        {
            "label": "Check Suspicious Startup Items (report-only)",
            "func": task_startup_items,
            "requires_admin": False
        },
        {
            "label": "System File Checker (sfc /scannow)",
            "func": task_sfc_scannow,
            "requires_admin": True
        },
        {
            "label": "DISM RestoreHealth",
            "func": task_dism_restorehealth,
            "requires_admin": True
        },
        {
            "label": "Check SMART / Disk Health",
            "func": task_smart_health,
            "requires_admin": True  # physical disk info often needs admin
        },
        {
            "label": "Bloatware Apps Report (no auto-removal)",
            "func": task_bloatware_report,
            "requires_admin": False
        },
        {
            "label": "Driver Sweep Report (no auto-removal)",
            "func": task_driver_report,
            "requires_admin": True
        },
    ]

    # Progress window
    prog_win = tk.Toplevel(root)
    prog_win.title("Running Cleanup Suite...")
    prog_win.geometry("420x170")
    prog_win.resizable(False, False)

    # Prevent closing while running
    def on_close():
        messagebox.showinfo(
            "Please wait",
            "Cleanup Suite is still running. Please wait for it to finish.",
            parent=prog_win
        )
    prog_win.protocol("WM_DELETE_WINDOW", on_close)

    mode_label = "Mode: FULL (admin)" if admin_now and not limited_mode else (
        "Mode: LIMITED (no admin — some tasks skipped)" if limited_mode else
        "Mode: NORMAL"
    )
    lbl_mode = tk.Label(prog_win, text=mode_label, font=("Segoe UI", 8, "italic"))
    lbl_mode.pack(pady=(8, 0))

    lbl_task = tk.Label(prog_win, text="Starting...", font=("Segoe UI", 10, "bold"))
    lbl_task.pack(pady=(10, 8))

    progress = ttk.Progressbar(prog_win, orient="horizontal", mode="determinate")
    progress.pack(fill="x", padx=20)
    progress["maximum"] = len(tasks)
    progress["value"] = 0

    lbl_hint = tk.Label(
        prog_win,
        text="This may take a while (SFC, DISM, Defender full scan, etc.)",
        font=("Segoe UI", 8)
    )
    lbl_hint.pack(pady=(10, 0))

    # Shared state between thread and UI
    state = {
        "current_task": "Starting...",
        "completed": 0,
        "results": [],
        "done": False,
        "error": None
    }

    def worker():
        try:
            for task in tasks:
                label = task["label"]
                func = task["func"]
                requires_admin = task["requires_admin"]

                # Update current task name
                state["current_task"] = label

                # If we are in limited mode and this task needs admin, skip it
                if limited_mode and requires_admin:
                    res = {
                        "name": label,
                        "success": False,
                        "summary": "SKIPPED — requires Administrator. "
                                   "Rerun IT Toolbox as admin for this task.",
                        "details": (
                            "This task was not run because the Cleanup Suite is in LIMITED MODE and "
                            "the process is not elevated.\n\n"
                            "To run this task, close the toolbox and launch it using "
                            "'Run as administrator', then run the Cleanup Suite again."
                        )
                    }
                else:
                    try:
                        res = func()
                        # Make sure the label is consistent
                        res["name"] = label
                    except Exception as e:
                        res = {
                            "name": label,
                            "success": False,
                            "summary": "Exception thrown in task.",
                            "details": f"Exception: {e}"
                        }

                state["results"].append(res)
                state["completed"] += 1
        except Exception as e:
            state["error"] = e
        finally:
            state["done"] = True

    def poll():
        # Update label + progress bar from state
        lbl_task.config(text=f"Running: {state['current_task']}")
        progress["value"] = state["completed"]

        if not state["done"]:
            prog_win.after(500, poll)
        else:
            prog_win.destroy()
            if state["error"] is not None:
                messagebox.showerror(
                    "Cleanup Suite Error",
                    f"An error occurred while running the cleanup suite:\n{state['error']}"
                )
            else:
                show_results_window(state["results"], limited_mode=limited_mode, admin_now=admin_now)

    # Start background thread
    t = threading.Thread(target=worker, daemon=True)
    t.start()

    # Start polling for updates
    prog_win.after(300, poll)
