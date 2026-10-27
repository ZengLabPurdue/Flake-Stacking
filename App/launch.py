import os
import subprocess
import sys
from pathlib import Path
from tkinter import Tk, StringVar
from tkinter import ttk

home_dir = os.path.dirname(os.path.abspath(__file__))
scanner_path = Path(home_dir) / "app.py"
os.chdir(home_dir)

# Hello roommate

def on_close():
    prior_args_final = prior_args.get() or "0"
    thor_args_final = thor_args.get() or "0"

    with open("port.config", "w") as f:
        f.write(f"{prior_args_final}\n")
        f.write(f"{thor_args_final}\n")

    root.destroy()

    python_exe = Path(sys.executable)
    script = scanner_path

<<<<<<< Updated upstream
    cmd = [str(python_exe), str(script), str(prior_args_final), str(thor_args_final)]
    subprocess.run(cmd, check=True)
=======
    cmd = [str(python_exe), str(script), str(prior_args_final), str(olympius_args_final)]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(e)
>>>>>>> Stashed changes

try:
    with open("port.config", "r") as f:
        prior_args_value = f.readline().strip()
        thor_args_value = f.readline().strip()
except FileNotFoundError:
    prior_args_value = ""

root = Tk()
root.title("Launch")
root.resizable(False, False)

frame = ttk.Frame(root, padding=15)
frame.grid(row=0, column=0)

prior_label = ttk.Label(frame, text="Prior COM Port:")
prior_label.grid(row=0, column=0, padx=(0,10), pady=(0,10), sticky="e")

prior_args = StringVar(value=prior_args_value)
prior_entry = ttk.Entry(frame, textvariable=prior_args, width=10)
prior_entry.grid(row=0, column=1, pady=(0,10), sticky="w")
prior_entry.focus()

thor_label = ttk.Label(frame, text="Thor COM Port:")
thor_label.grid(row=1, column=0, padx=(0,10), pady=(0,10), sticky="e")

thor_args = StringVar(value=thor_args_value)
thor_entry = ttk.Entry(frame, textvariable=thor_args, width=10)
thor_entry.grid(row=1, column=1, pady=(0,10), sticky="w")

thor_entry.focus()

confirm_btn = ttk.Button(frame, text="Launch", command=on_close)
confirm_btn.grid(row=2, column=0, columnspan=2, pady=(5,0))

root.bind("<Return>", lambda e: on_close())

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
