import os
import sys
import shutil
import ctypes
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import winreg
from pathlib import Path
import customtkinter as ctk

# Appearance Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def setup_cleanmgr_registry():
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_ENUMERATE_SUB_KEYS) as root_key:
            subkeys = []
            i = 0
            while True:
                try:
                    subkeys.append(winreg.EnumKey(root_key, i))
                    i += 1
                except OSError:
                    break
        
        # Set StateFlags65535 to 2 to automatically enable all checkboxes in cleanmgr /sagerun
        for subkey in subkeys:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{key_path}\\{subkey}", 0, winreg.KEY_SET_VALUE) as sk:
                    winreg.SetValueEx(sk, "StateFlags65535", 0, winreg.REG_DWORD, 2)
            except Exception:
                pass
    except Exception:
        pass

class CleanupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Deep System Cleanup Utility")
        self.geometry("900x650")
        self.minsize(800, 550)
        
        # Checkbox variables
        self.var_temp = ctk.BooleanVar(value=True)
        self.var_logs = ctk.BooleanVar(value=True)
        self.var_browser = ctk.BooleanVar(value=True)
        self.var_dev = ctk.BooleanVar(value=False)
        self.var_native = ctk.BooleanVar(value=True)
        self.var_recycle = ctk.BooleanVar(value=True)
        self.var_screenshots = ctk.BooleanVar(value=False) # Safe default
        
        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        # Main Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar Title
        sidebar_title = ctk.CTkLabel(self.sidebar, text="Cleanup Options", font=ctk.CTkFont(size=18, weight="bold"))
        sidebar_title.pack(pady=20, padx=20, anchor="w")
        
        # Checkboxes
        self.chk_temp = ctk.CTkCheckBox(self.sidebar, text="Temporary Files", variable=self.var_temp)
        self.chk_temp.pack(pady=10, padx=20, anchor="w")
        
        self.chk_logs = ctk.CTkCheckBox(self.sidebar, text="System Logs (CBS, etc.)", variable=self.var_logs)
        self.chk_logs.pack(pady=10, padx=20, anchor="w")
        
        self.chk_browser = ctk.CTkCheckBox(self.sidebar, text="Browser Caches", variable=self.var_browser)
        self.chk_browser.pack(pady=10, padx=20, anchor="w")
        
        self.chk_dev = ctk.CTkCheckBox(self.sidebar, text="Developer Caches", variable=self.var_dev)
        self.chk_dev.pack(pady=10, padx=20, anchor="w")
        
        self.chk_native = ctk.CTkCheckBox(self.sidebar, text="Native cleanmgr & DISM", variable=self.var_native)
        self.chk_native.pack(pady=10, padx=20, anchor="w")
        
        self.chk_recycle = ctk.CTkCheckBox(self.sidebar, text="Recycle Bin", variable=self.var_recycle)
        self.chk_recycle.pack(pady=10, padx=20, anchor="w")
        
        self.chk_screenshots = ctk.CTkCheckBox(self.sidebar, text="Screenshots (Warning)", variable=self.var_screenshots, fg_color="#d9534f")
        self.chk_screenshots.pack(pady=10, padx=20, anchor="w")
        
        # Select All / Unselect All
        self.btn_toggle_all = ctk.CTkButton(self.sidebar, text="Toggle All", command=self.toggle_all_checkboxes, fg_color="transparent", border_width=1)
        self.btn_toggle_all.pack(side=tk.BOTTOM, pady=20, padx=20, fill=tk.X)
        
        # Main Area Title
        title_label = ctk.CTkLabel(self.main_frame, text="Deep System Cleanup", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(pady=(10, 10), padx=20, anchor="w")
        
        # Console / Log Box
        self.console = ctk.CTkTextbox(self.main_frame, font=("Consolas", 11))
        self.console.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(fill=tk.X, padx=20, pady=(0, 15))
        self.progress_bar.set(0)
        
        # Action Frame
        action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.btn_start = ctk.CTkButton(action_frame, text="Run Cleanup", font=ctk.CTkFont(size=14, weight="bold"), height=40, command=self.start_cleanup)
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.btn_clear = ctk.CTkButton(action_frame, text="Clear Log", width=120, height=40, fg_color="gray30", hover_color="gray40", command=self.clear_console)
        self.btn_clear.pack(side=tk.RIGHT)
        
        self.log("System Ready. Select items from the sidebar and click 'Run Cleanup'.\n")

    def log(self, message):
        def append():
            self.console.insert("end", message + "\n")
            self.console.see("end")
        self.after(0, append)

    def clear_console(self):
        self.console.delete('1.0', 'end')

    def toggle_all_checkboxes(self):
        any_false = not (self.var_temp.get() and self.var_logs.get() and self.var_browser.get() and self.var_dev.get() and self.var_native.get() and self.var_recycle.get() and self.var_screenshots.get())
        val = any_false
        self.var_temp.set(val)
        self.var_logs.set(val)
        self.var_browser.set(val)
        self.var_dev.set(val)
        self.var_native.set(val)
        self.var_recycle.set(val)
        self.var_screenshots.set(val)

    def manage_service(self, service_name, action):
        try:
            subprocess.run(f"net {action} {service_name}", shell=True, capture_output=True, check=True)
            self.log(f"    [+] Service '{service_name}' {action}ed.")
        except subprocess.CalledProcessError:
            self.log(f"    [!] Could not {action} '{service_name}'.")

    def clean_directory(self, target_path):
        expanded_path = Path(os.path.expandvars(target_path))
        if not expanded_path.exists():
            return

        self.log(f"[*] Cleaning: {expanded_path}")
        deleted_count = 0
        skipped_count = 0
        
        for item in expanded_path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                deleted_count += 1
            except PermissionError:
                skipped_count += 1
            except Exception as e:
                self.log(f"    [!] Failed: {item.name} - {e}")
                skipped_count += 1
                
        if deleted_count > 0:
            self.log(f"    [+] Deleted {deleted_count} items.")
        if skipped_count > 0:
            self.log(f"    [i] Skipped {skipped_count} items (files in use/permission denied).")

    def empty_recycle_bin(self):
        self.log("[*] Emptying Recycle Bin...")
        try:
            result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            if result == 0:
                self.log("    [+] Recycle Bin cleared.")
            else:
                self.log(f"    [!] Failed to empty Recycle Bin (code: {result}).")
        except Exception as e:
            self.log(f"    [!] Recycle Bin Error: {e}")

    def clean_browser_caches(self):
        # Chrome
        chrome_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"))
        if chrome_dir.exists():
            self.log("[*] Scanning Chrome profiles...")
            default_cache = chrome_dir / "Default" / "Cache"
            if default_cache.exists():
                self.clean_directory(str(default_cache))
            
            for item in chrome_dir.iterdir():
                if item.is_dir() and (item.name.startswith("Profile ") or item.name == "Guest Profile"):
                    profile_cache = item / "Cache"
                    if profile_cache.exists():
                        self.clean_directory(str(profile_cache))
        else:
            self.log("    [-] Chrome installation not found.")

        # Edge
        edge_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"))
        if edge_dir.exists():
            self.log("[*] Scanning Edge profiles...")
            default_cache = edge_dir / "Default" / "Cache"
            if default_cache.exists():
                self.clean_directory(str(default_cache))
            
            for item in edge_dir.iterdir():
                if item.is_dir() and (item.name.startswith("Profile ") or item.name == "Guest Profile"):
                    profile_cache = item / "Cache"
                    if profile_cache.exists():
                        self.clean_directory(str(profile_cache))
        else:
            self.log("    [-] Edge installation not found.")

        # Firefox
        ff_profiles = Path(os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"))
        if ff_profiles.exists():
            cleaned_ff = False
            for profile in ff_profiles.iterdir():
                cache2 = profile / "cache2"
                if cache2.exists():
                    self.log(f"[*] Cleaning Firefox cache for profile: {profile.name}")
                    self.clean_directory(str(cache2))
                    cleaned_ff = True
            if not cleaned_ff:
                self.log("    [-] Firefox cache folders not found.")
        else:
            self.log("    [-] Firefox installation not found.")

    def clean_dev_caches(self):
        self.log("    [i] Cleaning NuGet packages cache will require restoring all project packages.")
        self.clean_directory(r"%USERPROFILE%\.nuget\packages")
        
        commands = {
            "Python Pip": ("pip cache purge", "pip"),
            "Node NPM": ("npm cache clean --force", "npm"),
            ".NET NuGet": ("dotnet nuget locals all --clear", "dotnet")
        }

        for name, (cmd, exe) in commands.items():
            if shutil.which(exe) is None:
                self.log(f"    [-] {name} CLI tool '{exe}' not found in PATH. Skipping.")
                continue
            self.log(f"[*] Purging {name} Cache...")
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if res.returncode == 0:
                    self.log(f"    [+] {name} cache cleared.")
                else:
                    self.log(f"    [!] {name} failed: {res.stderr.strip() or res.stdout.strip()}")
            except Exception as e:
                self.log(f"    [!] Failed to clear {name}: {e}")

    def root_disable_controls(self):
        def update():
            self.btn_start.configure(state="disabled")
            self.chk_temp.configure(state="disabled")
            self.chk_logs.configure(state="disabled")
            self.chk_browser.configure(state="disabled")
            self.chk_dev.configure(state="disabled")
            self.chk_native.configure(state="disabled")
            self.chk_recycle.configure(state="disabled")
            self.chk_screenshots.configure(state="disabled")
            self.btn_toggle_all.configure(state="disabled")
        self.after(0, update)

    def root_enable_controls(self):
        def update():
            self.btn_start.configure(state="normal")
            self.chk_temp.configure(state="normal")
            self.chk_logs.configure(state="normal")
            self.chk_browser.configure(state="normal")
            self.chk_dev.configure(state="normal")
            self.chk_native.configure(state="normal")
            self.chk_recycle.configure(state="normal")
            self.chk_screenshots.configure(state="normal")
            self.btn_toggle_all.configure(state="normal")
        self.after(0, update)

    def cleanup_worker(self):
        self.root_disable_controls()
        self.log("\n=== STARTING CLEANUP PROCESS ===")
        
        steps = []
        if self.var_temp.get(): steps.append("temp")
        if self.var_logs.get(): steps.append("logs")
        if self.var_browser.get(): steps.append("browser")
        if self.var_dev.get(): steps.append("dev")
        if self.var_native.get(): steps.append("native")
        if self.var_recycle.get(): steps.append("recycle")
        if self.var_screenshots.get(): steps.append("screenshots")
        
        if not steps:
            self.log("[!] No items selected. Cleanup aborted.")
            self.log("================================\n")
            self.root_enable_controls()
            return
            
        total_steps = len(steps)
        current_step = 0
        
        def update_progress():
            nonlocal current_step
            current_step += 1
            self.progress_bar.set(current_step / total_steps)

        # 1. Temp files
        if "temp" in steps:
            self.log("\n--- Cleaning Temporary Files ---")
            targets = [
                r"%WINDIR%\Temp",
                r"%LOCALAPPDATA%\Temp",
                r"%WINDIR%\Prefetch",
                r"%LOCALAPPDATA%\Microsoft\Windows\INetCache"
            ]
            for t in targets:
                self.clean_directory(t)
            update_progress()
            
        # 2. Logs
        if "logs" in steps:
            self.log("\n--- Cleaning System Logs ---")
            self.clean_directory(r"%WINDIR%\Logs\CBS")
            self.clean_directory(r"%PROGRAMDATA%\Microsoft\Windows\WER")
            update_progress()
            
        # 3. Browser Cache
        if "browser" in steps:
            self.log("\n--- Cleaning Browser Caches ---")
            self.clean_browser_caches()
            update_progress()
            
        # 4. Dev Cache
        if "dev" in steps:
            self.log("\n--- Cleaning Developer Caches ---")
            self.clean_dev_caches()
            update_progress()
            
        # 5. Native cleanmgr & DISM
        if "native" in steps:
            self.log("\n--- Running Windows Native Deep Clean & DISM ---")
            
            run_dism = messagebox.askyesno(
                "DISM Component Cleanup Warning",
                "Warning: The DISM component cleanup task deletes older versions of system components.\n"
                "This makes all currently installed Windows Updates permanent (cannot be uninstalled).\n\n"
                "Do you want to run the DISM cleanup step? (Click 'No' to skip DISM but run other native cleanups)"
            )
            
            self.log("[*] Pre-configuring Native Disk Cleanup settings...")
            setup_cleanmgr_registry()
            
            self.log("[*] Triggering Windows Native Deep Clean...")
            try:
                subprocess.Popen("cleanmgr /sagerun:65535", shell=True)
                self.log("    [+] Native Disk Cleanup triggered.")
            except Exception as e:
                self.log(f"    [!] Error triggering cleanmgr: {e}")
                
            self.log("[*] Processing Windows Update Cache...")
            self.manage_service("wuauserv", "stop")
            self.clean_directory(r"%WINDIR%\SoftwareDistribution\Download")
            self.manage_service("wuauserv", "start")
            
            self.log("[*] Cleaning Delivery Optimization cache...")
            self.clean_directory(r"%PROGRAMDATA%\Microsoft\Windows\DeliveryOptimization\Cache")
            
            system_drive = os.environ.get("SystemDrive", "C:")
            old_windows = Path(f"{system_drive}/Windows.old")
            if old_windows.exists():
                self.log("[*] Removing Windows.old...")
                try:
                    subprocess.run(f'takeown /f "{system_drive}\\Windows.old" /r /d y 2>nul', capture_output=True, shell=True, timeout=120)
                    subprocess.run(f'icacls "{system_drive}\\Windows.old" /grant Administrators:F /T /Q 2>nul', capture_output=True, shell=True, timeout=120)
                    subprocess.run(f'rd /s /q "{system_drive}\\Windows.old"', capture_output=True, shell=True, timeout=120)
                    self.log("    [+] Windows.old removed.")
                except Exception as e:
                    self.log(f"    [!] Failed to remove Windows.old: {e}")
            else:
                self.log("    [-] Windows.old not found.")
                
            if run_dism:
                self.log("[*] Running DISM WinSxS component cleanup (may take several minutes)...")
                try:
                    subprocess.run("Dism /online /Cleanup-Image /StartComponentCleanup /ResetBase", capture_output=True, shell=True, timeout=600)
                    self.log("    [+] WinSxS component cleanup completed.")
                except subprocess.TimeoutExpired:
                    self.log("    [!] DISM timed out (still running in background).")
                except Exception as e:
                    self.log(f"    [!] DISM cleanup failed: {e}")
            else:
                self.log("    [-] DISM component cleanup skipped by user.")
                
            update_progress()
            
        # 6. Recycle bin
        if "recycle" in steps:
            self.log("\n--- Emptying Recycle Bin ---")
            self.empty_recycle_bin()
            update_progress()
            
        # 7. Screenshots
        if "screenshots" in steps:
            self.log("\n--- Cleaning Screenshots ---")
            self.clean_directory(r"%USERPROFILE%\Pictures\Screenshots")
            update_progress()
            
        self.log("\n==================================")
        self.log("=== ALL SELECTED CLEANUPS DONE ===")
        self.log("==================================\n")
        self.root_enable_controls()

    def start_cleanup(self):
        self.progress_bar.set(0)
        threading.Thread(target=self.cleanup_worker, daemon=True).start()

if __name__ == "__main__":
    if not is_admin():
        script = sys.argv[0]
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        
        if script.endswith(".py"):
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
        else:
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
            
        if int(ret) <= 32:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Administrator Rights Required", 
                "This cleanup utility must be run as Administrator to access system files.\n\nPrivilege elevation failed or was denied."
            )
            root.destroy()
            sys.exit(1)
        sys.exit(0)
    else:
        app = CleanupApp()
        app.mainloop()