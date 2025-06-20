import os
import sys
import time
import random
from Tools.IPConfig import run_ipconfig
from Tools.PCHealth import HealthCheck
from Tools.SysInfo import run_SI
import tkinter as tk
from tkinter import messagebox

version = '1.1'

#test function for buttons until app functionality is added
def placeholder():
    print("Button pressed")

#when app is opened, this header will run with the loading bar
def show_greeting(root, callback):
    greeting_win = tk.Toplevel(root)
    greeting_win.title("Welcome!")
    greeting_win.geometry("500x200")
    #greeting_win.resizable(False, False)
    greeting_win.configure(bg="black")
    greeting_win.protocol("WM_DELETE_WINDOW", root.quit)

    text = f"""
v {version}
*      . +    o. '    . +.  +*   +  .    * '. +.
' _|_ .+    . + .  + +++.    +      ''  '+  .
 . | o'      . |  IT TOOLBOX  .'   o           ++
    .        - o -  o ' .    +_|_ '+ '+       /
'   +  +' +.  . |        '   '  |       .   ' *
    """
    label = tk.Label(greeting_win, text=text, fg="lime", bg="black", font=("Courier", 9))
    label.pack(pady=10)

    progress = tk.IntVar()
    bar = tk.Label(greeting_win, text="", fg="lime", bg="black")
    bar.pack()

    #greeting animation loading bar
    def update_bar(i=0):
        if i <= 30:
            bar_text = "█" * i + "-" * (30 - i)
            bar.config(text=f"Loading: |{bar_text}| {int(i/30*100):>3}%")
            greeting_win.after(100, update_bar, i + 1)

        else:
            greeting_win.destroy()
            callback()

    update_bar()

#These 2 functions detect hover on buttons to change their bg
def enter(e):
    e.widget['bg'] = "#181818"

def leave(e):
    e.widget['bg'] = 'black'

#Animated Rain BG
def start_rain(canvas, width, height):
    columns = width // 20
    drops = [0 for _ in range(columns)]

    def draw():
        nonlocal drops
        canvas.delete("rain")
        for i in range(columns):
            x = i * 20
            y = drops[i] * 20
            char = random.choice("01")
            canvas.create_text(x, y, text=char, fill='lime', tags="rain", font=("Courier", 10, "bold"))
            drops[i] = y + 20 if y < height else 0
        if rain_active:
            canvas.after(100, draw)

    draw()


#stops rain when called
def stop_rain(canvas):
    canvas.delete("rain")


rain_active = False
rain_ids = []
#functionality for rain on/off
def toggle_rain(canvas, height, width, toggle_btn):
    global rain_active
    #toggle_btn = None
    rain_active = not rain_active
    if rain_active:
        start_rain(canvas, 800, 650)
        toggle_btn.config(text="Rain: ON")
    else:
        stop_rain(canvas)
        toggle_btn.config(text="Rain: OFF")
    
#---------------------------------------------------------------------------------------------------------------------------
def launch_toolbox():
    window = tk.Tk()
    width, height = 800, 650
    window.geometry(f"{width}x{height}")
    window.title("IT Toolbox v" + version)
    window.configure(bg="black")

    canvas = tk.Canvas(window, bg="black", highlightthickness=0)
    canvas.place(relwidth=1, relheight=1)
    canvas.lower("all")

    # initial state using a dict to allow mutation in nested scope
    rain_state = {"active": False, "after_id": None}

    def start_rain(canvas, width, height):
        columns = width // 20
        drops = [random.randint(0, height // 20) for _ in range(columns)]  # random start positions

        def draw():
            canvas.delete("rain")
            for i in range(columns):
                x = i * 20
                y = drops[i] * 20
                char = random.choice("01")
                canvas.create_text(x, y, text=char, fill='lime', tags="rain", font=("Courier", 10, "bold"))

                # move the drop down or reset if it hits bottom
                drops[i] = 0 if y > height else drops[i] + 1

            if rain_state["active"]:
                rain_state["after_id"] = canvas.after(50, draw)

        draw()

    def stop_rain():
        if rain_state["after_id"]:
            canvas.after_cancel(rain_state["after_id"])
            rain_state["after_id"] = None
        canvas.delete("rain")

    def toggle_rain():
        rain_state["active"] = not rain_state["active"]
        if rain_state["active"]:
            toggle_btn.config(text = "Rain: ON")
            start_rain(canvas, width, height)
        else:
            toggle_btn.config(text="Rain: OFF")
            stop_rain()

    # Start rain initially
    #start_rain() - automatically starts rain on startup

    # premade button style template
    button_style = {
        "width": 20,
        "height": 5,
        "bg": "black",
        "fg": "lime",
        "activebackground": "#333",
        "activeforeground": "lime",
        "font": ("Segoe UI", 10, "bold"),
        "bd": 2,
        "relief": "groove",
        "padx": 5,
        "pady": 5
    }

    tk.Label(window, text="IT Toolbox", font=("Segoe UI", 16, "bold"), fg="lime", bg="black").pack(pady=(10, 20))

    button_frame = tk.Frame(window, bg="black")
    button_frame.pack()

    tools = [
        ("IPConfig", run_ipconfig),
        ("PC Health Check", HealthCheck),
        ("System Info", run_SI),
        ("Tool 4", placeholder),
        ("Tool 5", placeholder),
        ("Tool 6", placeholder),
        ("Tool 7", placeholder),
        ("Tool 8", placeholder),
        ("Tool 9", placeholder)
    ]

    for idx, (label, cmd) in enumerate(tools):
        r = idx // 3
        c = idx % 3
        btn = tk.Button(button_frame, text=label, command=cmd, **button_style)
        btn.grid(row=r, column=c, padx=10, pady=10)
        btn.bind("<Enter>", enter)
        btn.bind("<Leave>", leave)

    # Create toggle button *after* defining the toggle_rain function
    toggle_btn = tk.Button(
        window,
        text="Rain: OFF",
        fg="lime",
        bg="black",
        font=("Segoe UI", 8),
        bd=1,
        relief="ridge",
        command=toggle_rain  # Don't call it here, just reference it
    )
    toggle_btn.place(x=5, y=5)

    x_btn = tk.Button(window, text="EXIT", command=window.destroy, height=5, width=20, fg="lime", bg="black")
    x_btn.pack(pady=20)
    x_btn.bind("<Enter>", enter)
    x_btn.bind("<Leave>", leave)

    window.mainloop()
#---------------------------------------------------------------------------------------------------------------------------

#launch_toolbox()

def run_and_notify(toolfunc):
    try:
        toolfunc()
        #messagebox.showinfo()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    root.withdraw() #hide root window until greeting is done

    #prevents menu from reopening when clicking the 'X'
    def start():
        try:
            root.destroy()
        except:
            pass
        launch_toolbox()

    show_greeting(root, callback=start)
    root.mainloop()

if __name__ == "__main__":
    main()