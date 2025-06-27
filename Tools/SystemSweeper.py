#Deletes TEMP/TMP files with an option to clean out Recycle Bin

import os 
import shutil 
import tkinter as tk
from tkinter import messagebox
import ctypes 

#Searches standard path for TEMP and TMP files for removal
def get_temp_paths():
    return [
        os.environ.get('TEMP'),
        os.environ.get('TMP'),
        r'C:\Windows\Temp' 
    ]


#Deletes detected temp files and optionally empties Recycle Bin
def delete_temp_files():
    deleted_files = 0
    deleted_folders = 0
    for path in get_temp_paths():
        if path and os.path.exists(path):
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        deleted_files += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        deleted_folders += 1
                except Exception as e:
                    continue
    return deleted_files, deleted_folders

def empty_recycle_bin():
    ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000007)

#Displays status of app and completion details
def run_cleanup_gui():
    root = tk.Tk()
    root.title("System Sweeper")
    root.geometry("300x150")
    root.configure(bg="black")

    def start_cleanup():
        files, folders = delete_temp_files()
        try:
            empty_recycle_bin()
        except:
            pass 
        messagebox.showinfo("Cleanup Complete!", f"Deleted {files} files and {folders} folders.\nRecycle Bin emptied.")

    label = tk.Label(root, text="Click below to clean up system temp files", fg="lime", bg="black")
    label.pack(pady=20)

    clean_button = tk.Button(root, text="Start Cleanup", command=start_cleanup, width=20, fg= "lime", bg="Black")
    clean_button.pack(pady=10)

    root.mainloop()