import tkinter as tk
import socket
import uuid
import psutil

def run_ipconfig():
    IPGUI()

def get_network_info():
    info = {}
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])

    info["Hostname"] = hostname
    info["Local IP"] = ip_address
    info["MAC Address"] = mac

    # Use psutil to get additional network info
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                info["Interface"] = interface
                info["Subnet Mask"] = addr.netmask
            elif addr.family == psutil.AF_LINK:
                info["MAC (from psutil)"] = addr.address

    # Use psutil for default gateway
    gws = psutil.net_if_stats()
    for name, stats in psutil.net_if_stats().items():
        if stats.isup:
            break

    try:
        info["Default Gateway"] = psutil.net_if_addrs()[interface][0].address
    except:
        info["Default Gateway"] = "Unknown"

    return info

def display_info(frame):
    info = get_network_info()
    for widget in frame.winfo_children():
        widget.destroy()

    for key, value in info.items():
        label = tk.Label(frame, text=f"{key}: {value}", anchor='w', bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
        label.pack(fill='x', padx=10, pady=2)

# GUI Setup
def IPGUI():
    win = tk.Toplevel()
    win.title("IPConfig Tool")
    win.geometry("500x300")
    win.configure(bg="#1e1e1e")

    tk.Label(win, text="IP Configuration", font=("Segoe UI", 14, "bold"), bg="#1e1e1e", fg="cyan").pack(pady=10)

    frame = tk.Frame(win, bg="#1e1e1e")
    frame.pack(fill='both', expand=True)

    display_info(frame)
    
    tk.Button(win, text="Refresh", command=lambda: display_info(frame)).pack(pady=5)