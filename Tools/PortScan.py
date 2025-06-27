#Simple application that scans through all ports to display open/closed status

import tkinter as tk
from tkinter import scrolledtext
import socket
from threading import Thread


#Function called in MainMenu.py to initiate the GUI prior to running the application
def scanner_GUI():
    PSGUI()


#Function that iterates over the ports and determines their status
def scan_ports():
    target = ip_entry.get()
    try:
        start = int(start_port_entry.get())
        end = int(end_port_entry.get())
    except ValueError:
        output_box.insert(tk.END, "Port range must be numbers.\n")
        return

    output_box.delete('1.0', tk.END)
    output_box.insert(tk.END, f"Scanning {target} ports {start}-{end}...\n\n")

    def scanner():
        for port in range(start, end + 1):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target, port))
                print(f"Checking port {port} - result: {result}")
                if result == 0:
                    output_box.after(0, lambda p=port: output_box.insert(tk.END, f"Port {p}: OPEN\n"))
                else:
                    output_box.after(0, lambda p=port: output_box.insert(tk.END, f"Port {p}: Closed\n"))
                sock.close()
            except Exception as e:
                output_box.after(0, lambda p=port, err=str(e): output_box.insert(tk.END, f"Error on port {p}: {err}\n"))

    Thread(target=scanner).start()
    
# GUI Setup
def PSGUI():
    global ip_entry, start_port_entry, end_port_entry, output_box
    root = tk.Toplevel()
    root.title("Port Scanner")
    root.geometry("600x450")
    root.configure(bg="#1e1e1e")

    # Title
    tk.Label(root, text="Port Scanner", font=("Segoe UI", 14, "bold"), fg="cyan", bg="#1e1e1e").pack(pady=10)

    # Input fields
    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack()

    tk.Label(frame, text="Target IP/Host:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    ip_entry = tk.Entry(frame, width=25)
    ip_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame, text="Start Port:", bg="#1e1e1e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    start_port_entry = tk.Entry(frame, width=10)
    start_port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame, text="End Port:", bg="#1e1e1e", fg="white").grid(row=1, column=2, padx=5, pady=5, sticky="e")
    end_port_entry = tk.Entry(frame, width=10)
    end_port_entry.grid(row=1, column=3, padx=5, pady=5)

    # Scan Button
    tk.Button(root, text="Scan Ports", command=scan_ports).pack(pady=10)

    # Output box
    output_box = scrolledtext.ScrolledText(root, font=("Courier New", 10), width=70, height=15, bg="#121212", fg="lime")
    output_box.pack(pady=10)

    #root.mainloop()
    
if __name__ == "__main__":
    PSGUI()
