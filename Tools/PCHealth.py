#Process that checks basic system health by determining CPU usage, memory usage, and disk usage
#Looking to expand in the future for more in depth diagnostics and 'health rating' system

import tkinter as tk
import psutil
import shutil

#Function called in MainMenu.py to initiate GUI prior to running the 'health check'
def HealthCheck():
    HCGUI()


#Function that pulls information to display
def get_system_health():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("/")

    return {
        "CPU Usage": f"{cpu}%",
        "RAM Usage": f"{round(ram.used / (1024 ** 3), 2)} / {round(ram.total / (1024 ** 3), 2)} GB ({ram.percent}%)",
        "Disk Usage": f"{round(disk.used / (1024 ** 3), 2)} / {round(disk.total / (1024 ** 3), 2)} GB ({round(disk.used / disk.total * 100, 2)}%)"
    }

def update_info(frame):
    info = get_system_health()
    for widget in frame.winfo_children():
        widget.destroy()

    for key, value in info.items():
        label = tk.Label(frame, text=f"{key}: {value}", anchor='w', bg="#1e1e1e", fg="white", font=("Segoe UI", 11))
        label.pack(fill='x', padx=10, pady=5)

# GUI Setup
def HCGUI():

    root = tk.Tk()
    root.title("System Health Checker")
    root.geometry("500x250")
    root.configure(bg="#1e1e1e")

    tk.Label(root, text="System Health Checker", font=("Segoe UI", 14, "bold"), bg="#1e1e1e", fg="cyan").pack(pady=10)

    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack(fill='both', expand=True)

    tk.Button(root, text="Refresh", command=update_info(frame)).pack(pady=5)


#***Calling these functions led to the application running prior to the GUI***
#update_info()
#root.mainloop()
