import os
import shutil
import tkinter as tk
from tkinter import messagebox
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_temp_paths():
    paths = [
        os.environ.get('TEMP'),
        os.environ.get('TMP'),
    ]
    # Only try to clean system temp if running as admin
    if is_admin():
        paths.append(r'C:\Windows\Temp')
    return [p for p in paths if p]

def delete_temp_files():
    deleted_files = 0
    deleted_folders = 0

    for path in get_temp_paths():
        if not os.path.exists(path):
            continue
        try:
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        deleted_files += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path, ignore_errors=True)
                        deleted_folders += 1
                except PermissionError:
                    # can’t delete this one, skip it
                    continue
                except OSError:
                    continue
        except PermissionError:
            # no permission to even list this folder
            continue

    return deleted_files, deleted_folders

def empty_recycle_bin():
    ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000007)

def run_cleanup_gui():
    root = tk.Tk()
    root.title("System Sweeper")
    root.geometry("300x150")
    root.configure(bg="black")

    def start_cleanup():
        files, folders = delete_temp_files()
        try:
            empty_recycle_bin()
            rb_text = "Recycle Bin emptied."
        except:
            rb_text = "Recycle Bin could not be emptied."
        messagebox.showinfo(
            "Cleanup Complete!",
            f"Deleted {files} files and {folders} folders.\n{rb_text}"
        )

    label = tk.Label(root, text="Click below to clean up system temp files",
                     fg="lime", bg="black")
    label.pack(pady=20)

    clean_button = tk.Button(root, text="Start Cleanup",
                             command=start_cleanup, width=20,
                             fg="lime", bg="black")
    clean_button.pack(pady=10)

    root.mainloop()
