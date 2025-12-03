# MainMenu.py - Glassy / Modern IT Toolbox

import os
import subprocess
import sys
import time
import random
import ctypes

# ====== TOOL IMPORTS (adjust if your filenames differ) ======
from Tools.IPConfig import run_ipconfig
from Tools.PCHealth import HealthCheck
from Tools.SysInfo import run_SI
from Tools.PortScan import scanner_GUI
from Tools.SystemSweeper import run_cleanup_gui
from Tools.PWGenerator import gen_gui
from Tools.CleanUp import run_cleanup_suite
from Tools.Drivers import open_update_driver_checker
from Tools.SystemReport import open_system_report

# ====== GUI IMPORTS ======
import tkinter as tk  # for Canvas (matrix rain)
import customtkinter as ctk
from tkinter import messagebox

version = "1.2"

# =============================================================================
# Windows Acrylic Blur Support (glassy background)
# =============================================================================

class ACCENTPOLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_int),
        ("AnimationId", ctypes.c_int),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.c_void_p),
        ("SizeOfData", ctypes.c_size_t),
    ]


WCA_ACCENT_POLICY = 19
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4  # Win10 1803+


def enable_acrylic(hwnd, hex_color="#101820", opacity=0xCC):
    """
    Enable acrylic/blur behind the given window handle (Windows 10+).
    hex_color: hex tint like "#101820"
    opacity: 0x00–0xFF (alpha, higher = more solid)
    """
    try:
        color = int(hex_color.lstrip("#"), 16)
        # Windows expects BGR, so swap R and B
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        bgr = (b << 16) | (g << 8) | r

        gradient_color = (opacity << 24) | bgr

        accent = ACCENTPOLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 0
        accent.GradientColor = gradient_color
        accent.AnimationId = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
        data.SizeOfData = ctypes.sizeof(accent)

        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
    except Exception as e:
        # If something goes wrong, just print and continue without blur
        print("Acrylic blur not available:", e)


# =============================================================================
# Helper wrappers for existing tools
# =============================================================================

def placeholder():
    print("Button pressed (placeholder)")


def launch_sweeper():
    run_cleanup_gui()


def launch_cleanup_suite():
    run_and_notify(run_cleanup_suite)


# =============================================================================
# Greeting / Splash Screen
# =============================================================================

def show_greeting(root, callback):
    greeting_win = ctk.CTkToplevel(root)
    greeting_win.title("Welcome!")
    greeting_win.geometry("520x230")
    greeting_win.resizable(False, False)
    greeting_win.configure(fg_color="#050608")
    greeting_win.protocol("WM_DELETE_WINDOW", root.quit)

    text = f"""
v {version}
 ___ _____   _____           _ _
|_ _|_   _| |_   _|__   ___ | | |__   _____  __
 | |  | |     | |/ _ \\ / _ \\| | '_ \\ / _ \\ \\/ /
 | |  | |     | | (_) | (_) | | |_) | (_) >  <
|___| |_|     |_|\\___/ \\___/|_|_.__/ \\___/_/\\_\\
    """

    label = ctk.CTkLabel(
        greeting_win,
        text=text,
        text_color="#7CFC00",
        font=("Cascadia Mono", 11),
        justify="left"
    )
    label.pack(pady=(15, 5), padx=15)

    progress_label = ctk.CTkLabel(
        greeting_win,
        text="Loading: |------------------------------|   0%",
        text_color="#7CFC00",
        font=("Cascadia Mono", 11)
    )
    progress_label.pack(pady=(0, 10))

    progress_bar = ctk.CTkProgressBar(
        greeting_win,
        width=380,
        progress_color="#7CFC00",
        fg_color="#1b1b1b"
    )
    progress_bar.set(0)
    progress_bar.pack(pady=(0, 10))

    def update_bar(i=0):
        if i <= 30:
            bar_text = "█" * i + "-" * (30 - i)
            percent = int(i / 30 * 100)
            progress_label.configure(text=f"Loading: |{bar_text}| {percent:>3}%")
            progress_bar.set(i / 30)
            greeting_win.after(90, update_bar, i + 1)
        else:
            greeting_win.destroy()
            callback()

    update_bar()


# =============================================================================
# Matrix Rain Background
# =============================================================================

def start_rain(canvas, width, height, rain_state):
    columns = max(1, width // 20)
    drops = [random.randint(0, height // 20) for _ in range(columns)]

    def draw():
        canvas.delete("rain")
        for i in range(columns):
            x = i * 20
            y = drops[i] * 20
            char = random.choice("01")
            canvas.create_text(
                x,
                y,
                text=char,
                fill="#00ff7f",
                tags="rain",
                font=("Courier New", 10, "bold")
            )
            drops[i] = 0 if y > height else drops[i] + 1

        if rain_state["active"]:
            rain_state["after_id"] = canvas.after(50, draw)

    draw()


def stop_rain(canvas, rain_state):
    if rain_state.get("after_id"):
        canvas.after_cancel(rain_state["after_id"])
        rain_state["after_id"] = None
    canvas.delete("rain")


# =============================================================================
# Main Toolbox Window
# =============================================================================

def launch_toolbox():
    ctk.set_appearance_mode("dark")        # "light", "dark", "system"
    ctk.set_default_color_theme("dark-blue")

    width, height = 800, 650
    window = ctk.CTk()
    window.geometry(f"{width}x{height}")
    window.title(f"IT Toolbox v{version}")
    window.minsize(780, 620)

    # Dark base color for glass effect
    window.configure(fg_color="#101820")

    # Enable Windows acrylic blur if possible
    if sys.platform == "win32":
        try:
            hwnd = window.winfo_id()
            enable_acrylic(hwnd, hex_color="#101820", opacity=0xCC)
        except Exception as e:
            print("Could not enable acrylic blur:", e)

    # Matrix rain canvas behind everything
    canvas = tk.Canvas(window, bg="#050608", highlightthickness=0)
    canvas.place(relwidth=1, relheight=1)
    canvas.lower("all")

    rain_state = {"active": False, "after_id": None}

    def toggle_rain():
        rain_state["active"] = not rain_state["active"]
        if rain_state["active"]:
            rain_button.configure(text="Rain: ON")
            start_rain(canvas, width, height, rain_state)
        else:
            rain_button.configure(text="Rain: OFF")
            stop_rain(canvas, rain_state)

    # Main glassy card
    main_frame = ctk.CTkFrame(
        window,
        fg_color="#111827",
        corner_radius=20,
    )
    main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.85)

    # Header
    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(15, 5))

    title_label = ctk.CTkLabel(
        header_frame,
        text="IT Toolbox",
        font=("Segoe UI", 24, "bold")
    )
    title_label.pack(side="left")

    version_label = ctk.CTkLabel(
        header_frame,
        text=f"v{version}",
        font=("Segoe UI", 14),
        text_color="#8f9ba8"
    )
    version_label.pack(side="left", padx=(10, 0))

    rain_button = ctk.CTkButton(
        header_frame,
        text="Rain: OFF",
        width=80,
        height=28,
        font=("Segoe UI", 11),
        fg_color="#1e2933",
        hover_color="#2b3a47",
        text_color="#cde4ff",
        corner_radius=10,
        command=toggle_rain
    )
    rain_button.pack(side="right")

    # Clock
    clock_label = ctk.CTkLabel(
        main_frame,
        font=("Cascadia Mono", 14),
        text_color="#9ee6a8"
    )
    clock_label.pack(pady=(0, 15))

    def update_clock():
        current_time = time.strftime("%I:%M:%S %p")
        clock_label.configure(text=f"Time: {current_time}")
        window.after(1000, update_clock)

    update_clock()

    # ASCII logo
    ascii_label = ctk.CTkLabel(
        main_frame,
        text=r"""
 ___ _____   _____           _ _
|_ _|_   _| |_   _|__   ___ | | |__   _____  __
 | |  | |     | |/ _ \ / _ \| | '_ \ / _ \ \/ /
 | |  | |     | | (_) | (_) | | |_) | (_) >  <
|___| |_|     |_|\___/ \___/|_|_.__/ \___/_/\_\
        """,
        font=("Cascadia Mono", 10),
        text_color="#7CFC00",
        justify="left"
    )
    ascii_label.pack(pady=(0, 10))

    # Tools grid
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(pady=10, padx=20, fill="both", expand=True)

    def launch_drivers_tool():
        open_update_driver_checker(window)

    def launch_system_report():
        open_system_report(window)

    tools = [
        ("IPConfig", run_ipconfig),
        ("PC Health Check", HealthCheck),
        ("System Info", run_SI),
        ("Port Scanner", scanner_GUI),
        ("System Sweeper", launch_sweeper),
        ("Password Generator", gen_gui),
        ("PC Cleanup", launch_cleanup_suite),
        ("Drivers / Updates", launch_drivers_tool),
        ("System Report", launch_system_report),
    ]

    def make_tool_button(parent, text, func):
        return ctk.CTkButton(
            parent,
            text=text,
            command=lambda: run_and_notify(func),
            width=190,
            height=70,
            corner_radius=14,
            fg_color="#1f2933",
            hover_color="#304255",
            text_color="#e5f0ff",
            font=("Segoe UI", 11, "bold")
        )

    for idx, (label, func) in enumerate(tools):
        r = idx // 3
        c = idx % 3
        btn = make_tool_button(button_frame, label, func)
        btn.grid(row=r, column=c, padx=12, pady=12, sticky="nsew")

    for i in range(3):
        button_frame.columnconfigure(i, weight=1)
    for i in range(3):
        button_frame.rowconfigure(i, weight=1)

    # Bottom bar
    bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    bottom_frame.pack(fill="x", padx=20, pady=(5, 15))

    exit_button = ctk.CTkButton(
        bottom_frame,
        text="Exit",
        width=120,
        height=36,
        corner_radius=10,
        fg_color="#7f1d1d",
        hover_color="#991b1b",
        text_color="white",
        font=("Segoe UI", 11, "bold"),
        command=window.destroy
    )
    exit_button.pack(side="right")

    window.mainloop()


# =============================================================================
# Shared run wrapper
# =============================================================================

def run_and_notify(toolfunc):
    try:
        toolfunc()
    except Exception as e:
        messagebox.showerror("Error", str(e))


# =============================================================================
# Entry point
# =============================================================================

def main():
    # Root just for splash, then destroyed
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.withdraw()

    def start():
        try:
            root.destroy()
        except Exception:
            pass
        launch_toolbox()

    show_greeting(root, callback=start)
    root.mainloop()


if __name__ == "__main__":
    main()
