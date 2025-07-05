import tkinter as tk 
from tkinter import messagebox 
import random 
import string

def gen_gui():
    PWGUI()

def gen_pw(length, use_upper, use_lower, use_digits, use_symbols):
    pool = ''
    if use_upper:
        pool += string.ascii_uppercase
    if use_lower:
        pool += string.ascii_lowercase
    if use_digits:
        pool += string.digits
    if use_symbols:
        pool += string.punctuation
        
    if not pool:
        raise ValueError("Select at least one character type.")
    
    pw = []
    if use_upper:
        pw.append(random.choice(string.ascii_uppercase))
    if use_lower:
        pw.append(random.choice(string.ascii_lowercase))
    if use_digits:
        pw.append(random.choice(string.digits))
    if use_symbols:
        pw.append(random.choice(string.punctuation))
        
    while len(pw) < length:
        pw.append(random.choice(pool))
        
    random.shuffle(pw)
    return ''.join(pw)

def PWGUI():
    win = tk.Toplevel()
    win.title("Password Generator")
    win.geometry("400x300")
    win.configure(bg="black")

    result_var = tk.StringVar()
    upper_var = tk.BooleanVar(value=True)
    lower_var = tk.BooleanVar(value=True)
    digits_var = tk.BooleanVar(value=True)
    symbols_var = tk.BooleanVar(value=True)

    # Password Length Input
    tk.Label(win, text="Password Length:", bg="black", fg="lime").pack(pady=5)
    length_entry = tk.Entry(win, justify="center")
    length_entry.insert(0, "12")
    length_entry.pack()

    # Checkboxes
    tk.Checkbutton(win, text="Include Uppercase", variable=upper_var, bg="black", fg="white", selectcolor="black").pack(anchor='w')
    tk.Checkbutton(win, text="Include Lowercase", variable=lower_var, bg="black", fg="white", selectcolor="black").pack(anchor='w')
    tk.Checkbutton(win, text="Include Digits", variable=digits_var, bg="black", fg="white", selectcolor="black").pack(anchor='w')
    tk.Checkbutton(win, text="Include Symbols", variable=symbols_var, bg="black", fg="white", selectcolor="black").pack(anchor='w')

    # Result Display
    tk.Button(win, text="Generate", bg="black", fg="lime", command=lambda: on_generate()).pack(pady=10)
    result_entry = tk.Entry(win, textvariable=result_var, justify='center', font=("Courier", 12))
    result_entry.pack(pady=5)

    # Copied Label (starts hidden)
    copied_label = tk.Label(win, text="Copied!", fg="lime", bg="black", font=("Courier", 10))
    copied_label.pack()
    copied_label.pack_forget()

    def on_generate():
        try:
            length = int(length_entry.get())
            if length < 4:
                copied_label.pack_forget()
                messagebox.showwarning("Too Short", "Password must be at least 4 characters.")
                return
            pwd = gen_pw(
                length,
                upper_var.get(),
                lower_var.get(),
                digits_var.get(),
                symbols_var.get()
            )
            result_var.set(pwd)
            copied_label.pack_forget()  # Hide 'Copied' when new password is generated
        except Exception as e:
            copied_label.pack_forget()
            messagebox.showerror("Error", str(e))

    def copy_to_clipboard():
        password = result_var.get()
        if password:
            win.clipboard_clear()
            win.clipboard_append(password)
            copied_label.pack()  # Show 'Copied!' below the password box

    tk.Button(win, text="Copy to Clipboard", bg="black", fg="lime", command=copy_to_clipboard).pack(pady=5)
