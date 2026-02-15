import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import subprocess
import sys
import threading
import os
import runpy  # Used to run scripts safely


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()


SCRIPT_REGISTER = os.path.join(BASE_PATH, "register.py")
SCRIPT_TRAIN = os.path.join(BASE_PATH, "generate_embeddings.py")
SCRIPT_RECOGNIZE = os.path.join(BASE_PATH, "recognize.py")
SCRIPT_MANAGE = os.path.join(BASE_PATH, "manage_records.py")

MAIN_LIST_FILE = os.path.join(BASE_PATH, "records", "main_list.csv")
CONFIG_FOLDER = os.path.join(BASE_PATH, "config")
PASS_FILE = os.path.join(CONFIG_FOLDER, "admin_pass.txt")


# This block detects if the EXE is being used as a worker or a GUI
if len(sys.argv) > 1 and sys.argv[1] == "--run-script":
    # WE ARE IN WORKER MODE 
    script_to_run = sys.argv[2]
    extra_args = sys.argv[3:]
    
    # Fake the arguments so the script thinks it was run normally
    sys.argv = [script_to_run] + extra_args
    
    try:
        # Run the external script file
        runpy.run_path(script_to_run, run_name="__main__")
    except Exception as e:
        print(f"CRITICAL ERROR running {script_to_run}: {e}")
    
    sys.exit(0) # Quit the worker process when done


# If we reach here, no arguments were passed. Open the Window.

class FaceRecognitionSystem:

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance System (v3.0 - Professional)")
        self.root.geometry("800x650")
        self.root.resizable(False, False)

        self.current_process = None

        self.setup_style()
        self.create_widgets()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))

    def create_widgets(self):
        header = tk.Frame(self.root, bg="white", height=80)
        header.pack(fill="x")

        ttk.Label(header, text="Smart Attendance System", style="Header.TLabel", background="white").pack(pady=20)

        content = ttk.Frame(self.root, padding=20)
        content.pack(fill="both", expand=True)

        # Registration
        reg_frame = ttk.LabelFrame(content, text="New Student Registration", padding=15)
        reg_frame.pack(fill="x", pady=5)
        ttk.Label(reg_frame, text="Student Name:").grid(row=0, column=0, padx=5)
        self.entry_name = ttk.Entry(reg_frame, width=30)
        self.entry_name.grid(row=0, column=1, padx=10)
        ttk.Button(reg_frame, text="Start Capture", command=self.start_registration).grid(row=0, column=2, padx=10)

        # Operations
        ops_frame = ttk.LabelFrame(content, text="System Operations", padding=15)
        ops_frame.pack(fill="x", pady=15)
        
        ttk.Button(ops_frame, text="Train Model", width=25, 
                   command=lambda: self.run_script(SCRIPT_TRAIN)).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(ops_frame, text="Start Attendance", width=25, 
                   command=lambda: self.run_script(SCRIPT_RECOGNIZE)).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(ops_frame, text="Update Records", width=25, 
                   command=lambda: self.run_script(SCRIPT_MANAGE)).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(ops_frame, text="Open Main List", width=25, 
                   command=self.open_main_list).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(ops_frame, text="Erase Main List (Admin)", width=25, 
                   command=self.erase_main_list).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(ops_frame, text="Change Password", width=25, 
                   command=self.change_admin_password).grid(row=2, column=1, padx=10, pady=5)
        ttk.Button(ops_frame, text="Stop Process", width=20, 
                   command=self.stop_process).grid(row=0, column=2, padx=10)

        # Logs
        log_frame = ttk.LabelFrame(content, text="System Logs", padding=10)
        log_frame.pack(fill="both", expand=True, pady=10)
        self.console = scrolledtext.ScrolledText(log_frame, height=12, state="disabled", font=("Consolas", 9), bg="#f0f0f0")
        self.console.pack(fill="both", expand=True)
        ttk.Button(content, text="Clear Logs", command=self.clear_logs).pack(side="left")
        ttk.Button(content, text="Exit Application", command=self.root.quit).pack(side="right")

    # ================= LOGGING =================
    def log(self, message):
        self.root.after(0, self._log_ui, message)

    def _log_ui(self, message):
        self.console.configure(state="normal")
        self.console.insert(tk.END, ">> " + message + "\n")
        self.console.see(tk.END)
        self.console.configure(state="disabled")

    def clear_logs(self):
        self.console.configure(state="normal")
        self.console.delete(1.0, tk.END)
        self.console.configure(state="disabled")

    # ================= PROCESS CONTROL =================
    def start_registration(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Please enter a Student Name first.")
            return
        self.log(f"Starting Registration for: {name}")
        self.run_script(SCRIPT_REGISTER, [name])

    def stop_process(self):
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            self.current_process = None
            self.log("Process stopped.")
        else:
            self.log("No active process running.")

    def run_script(self, script_path, extra_args=None):
        if not os.path.exists(script_path):
            self.log(f"ERROR: File not found: {script_path}")
            self.log("Ensure .py files are in the same folder as the EXE.")
            return

        if self.current_process and self.current_process.poll() is None:
            messagebox.showwarning("Busy", "A process is already running.")
            return

        self.log(f"Launching {os.path.basename(script_path)}...")
        
        threading.Thread(
            target=self._run_process_thread,
            args=(script_path, extra_args if extra_args else []),
            daemon=True
        ).start()

    def _run_process_thread(self, script_path, extra_args):
        try:
            # THIS IS THE MAGIC PART
            # We call our own EXE (sys.executable) with the special flag --run-script
            cmd = [sys.executable, "--run-script", script_path] + extra_args
            
            # If running as .py, we use normal python
            if not getattr(sys, 'frozen', False):
                cmd = [sys.executable, script_path] + extra_args

            # Start the safe subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=BASE_PATH # Ensure it runs in the correct folder
            )

            self.current_process = process

            # Read output line by line
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log(line.strip())

            # Read errors
            stderr_out = process.stderr.read()
            if stderr_out:
                self.log("ERROR: " + stderr_out.strip())

            process.wait()
            self.current_process = None
            self.log("Process finished.")

        except Exception as e:
            self.log(f"Execution failed: {e}")
 
    def get_admin_password(self):
        if not os.path.exists(PASS_FILE):
            with open(PASS_FILE, "w") as f: f.write("admin")
            return "admin"
        with open(PASS_FILE, "r") as f: return f.read().strip()

    def verify_admin(self):
        entered = simpledialog.askstring("Admin", "Enter Password:", show="*")
        return entered == self.get_admin_password()

    def erase_main_list(self):
        if self.verify_admin():
            if os.path.exists(MAIN_LIST_FILE):
                os.remove(MAIN_LIST_FILE)
                self.log("Main list erased.")
            else: messagebox.showwarning("Error", "File not found.")
        else: messagebox.showerror("Error", "Wrong password.")

    def change_admin_password(self):
        if self.verify_admin():
            p = simpledialog.askstring("New Password", "Enter new password:", show="*")
            if p:
                with open(PASS_FILE, "w") as f: f.write(p)
                messagebox.showinfo("Success", "Password updated.")

    def open_main_list(self):
        if os.path.exists(MAIN_LIST_FILE):
            os.startfile(MAIN_LIST_FILE)
        else: messagebox.showwarning("Error", "File not found.")

if __name__ == "__main__":
    os.makedirs(CONFIG_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(BASE_PATH, "records"), exist_ok=True)
    
    root = tk.Tk()
    app = FaceRecognitionSystem(root)
    root.mainloop()