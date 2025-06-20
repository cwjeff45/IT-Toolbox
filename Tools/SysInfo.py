import tkinter as tk
import platform
import psutil
import socket
import uuid
import shutil

def run_SI():
    SIGUI()

def get_system_info():
    info = {
        "Operating System": f"{platform.system()} {platform.release()}",
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=False),
        "Logical CPUs": psutil.cpu_count(logical=True),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Disk Usage": f"{round(shutil.disk_usage('/').used / (1024 ** 3), 2)} / {round(shutil.disk_usage('/').total / (1024 ** 3), 2)} GB",
        "Hostname": socket.gethostname(),
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "MAC Address": ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])
    }
    return info

def display_info(frame):
    info = get_system_info()
    for key, value in info.items():
        label = tk.Label(frame, text=f"{key}: {value}", anchor='w', bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
        label.pack(fill='x', padx=10, pady=2)

# GUI Setup
def SIGUI():
    root = tk.Tk()
    root.title("System Info Viewer")
    root.geometry("500x350")
    root.configure(bg="#1e1e1e")

    title = tk.Label(root, text="System Information", bg="#1e1e1e", fg="cyan", font=("Segoe UI", 14, "bold"))
    title.pack(pady=10)

    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack(fill='both', expand=True)

#display_info()
#root.mainloop()

