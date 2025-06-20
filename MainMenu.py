import os
import sys
import time
from Tools.IPConfig import run_ipconfig
from Tools.PCHealth import HealthCheck
from Tools.SysInfo import run_SI
import tkinter as tk
from tkinter import messagebox

version = '1.1'

def show_greeting(root, callback):
    greeting_win = tk.Toplevel(root)
    greeting_win.title("Welcome!")
    greeting_win.geometry("500x200")
    #greeting_win.resizable(False, False)
    greeting_win.configure(bg="black")

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

    def update_bar(i=0):
        if i <= 30:
            bar_text = "█" * i + "-" * (30 - i)
            bar.config(text=f"Loading: |{bar_text}| {int(i/30*100):>3}%")
            greeting_win.after(100, update_bar, i + 1)

        else:
            greeting_win.destroy()
            callback()

    update_bar()

def lauch_toolbox():
    window = tk.Tk()
    window.title("IT Toolbox v" + version)
    window.geometry("400x300")

    tk.Label(window, text="IT Toolbox", font=("Arial", 18)).pack(pady=10)

    tk.Button(window, text="1) IPConfig", width=20, command=lambda: run_and_notify(run_ipconfig)).pack(pady=5)
    tk.Button(window, text="2) PC Health Check", width=20, command=lambda: run_and_notify(HealthCheck)).pack(pady=5)
    tk.Button(window, text="3) System Information", width=20, command=lambda: run_and_notify(run_SI)).pack(pady=5)

    tk.Button(window, text="Exit", width=25, command=window.quit).pack(pady=20)

    window.mainloop()

def run_and_notify(toolfunc):
    try:
        toolfunc()
        #messagebox.showinfo()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    root.withdraw() #hide root window until greeting is done
    show_greeting(root, callback=lambda: [root.destroy(), lauch_toolbox()])
    root.mainloop()

if __name__ == "__main__":
    main()