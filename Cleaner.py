import os
import shutil
import ctypes
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

class CleanupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deep System Cleanup Utility")
        self.root.geometry("700x500")
        self.root.configure(padx=10, pady=10)

        # Title Label
        title_label = tk.Label(root, text="System & Developer Cleanup", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # Output Console 
        self.console = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, font=("Consolas", 9))
        self.console.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button Frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)

        # Buttons
        self.btn_basic = tk.Button(btn_frame, text="Basic Cleanup", width=15, command=self.start_basic_cleanup)
        self.btn_basic.pack(side=tk.LEFT, padx=5)

        self.btn_deep = tk.Button(btn_frame, text="Deep Cleanup", width=15, command=self.start_deep_cleanup)
        self.btn_deep.pack(side=tk.LEFT, padx=5)

        self.btn_dev = tk.Button(btn_frame, text="Clear Dev Caches", width=15, command=self.start_dev_cleanup)
        self.btn_dev.pack(side=tk.LEFT, padx=5)

        self.btn_browser = tk.Button(btn_frame, text="Browser Caches", width=15, command=self.start_browser_cleanup)
        self.btn_browser.pack(side=tk.LEFT, padx=5)

        self.btn_clear_log = tk.Button(btn_frame, text="Clear Log", width=15, command=self.clear_console)
        self.btn_clear_log.pack(side=tk.RIGHT, padx=5)

        self.log("Ready.\n")

    def log(self, message):
        def append():
            self.console.insert(tk.END, message + "\n")
            self.console.see(tk.END)
        self.root.after(0, append)

    def clear_console(self):
        self.console.delete('1.0', tk.END)

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
        for item in expanded_path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                self.log(f"    [+] Deleted: {item.name}")
            except Exception as e:
                self.log(f"    [!] Failed: {item.name} - {e}")

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

    
    
    def basic_cleanup_worker(self):
        self.root.after(0, lambda: self.btn_basic.config(state=tk.DISABLED))
        self.log("\n=== STARTING BASIC CLEANUP ===")
        targets = [
            r"%WINDIR%\Temp",
            r"%LOCALAPPDATA%\Temp",
            r"%WINDIR%\Prefetch",
            r"%LOCALAPPDATA%\Microsoft\Windows\INetCache",
            r"%USERPROFILE%\Pictures\Screenshots"
        ]
        for t in targets:
            self.clean_directory(t)
        self.empty_recycle_bin()
        self.log("=== BASIC CLEANUP COMPLETE ===\n")
        self.root.after(0, lambda: self.btn_basic.config(state=tk.NORMAL))

    def deep_cleanup_worker(self):
        self.root.after(0, lambda: self.btn_deep.config(state=tk.DISABLED))
        self.log("\n=== STARTING DEEP SYSTEM CLEANUP ===")
        
        # Stop Windows Update, clean, restart
        self.log("[*] Processing Windows Update Cache...")
        self.manage_service("wuauserv", "stop")
        self.clean_directory(r"%WINDIR%\SoftwareDistribution\Download")
        self.manage_service("wuauserv", "start")
        
     
        self.log("[*] Triggering Windows Native Deep Clean (Runs in background)...")
        self.log("    [i] Requires prior setup: run 'cleanmgr /sageset:65535' once to configure settings.")
        try:
            subprocess.Popen("cleanmgr /sagerun:65535", shell=True)
            self.log("    [+] Native Disk Cleanup triggered.")
        except Exception as e:
            self.log(f"    [!] Error triggering cleanmgr: {e}")

        self.log("[*] Cleaning CBS logs...")
        self.clean_directory(r"%WINDIR%\Logs\CBS")

        self.log("[*] Cleaning Delivery Optimization cache...")
        self.clean_directory(r"%PROGRAMDATA%\Microsoft\Windows\DeliveryOptimization\Cache")

        self.log("[*] Cleaning Windows Error Reporting dumps...")
        self.clean_directory(r"%PROGRAMDATA%\Microsoft\Windows\WER")

        self.log("[*] Cleaning Thumbnail Cache...")
        thumb_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer"))
        if thumb_dir.exists():
            for f in thumb_dir.glob("thumbcache_*.db"):
                try:
                    f.unlink()
                    self.log(f"    [+] Deleted: {f.name}")
                except Exception as e:
                    self.log(f"    [!] Failed: {f.name} - {e}")

        self.log("[*] Removing Windows.old...")
        self.log("    [i] This deletes the previous Windows installation (no rollback possible).")
        old_windows = Path("C:/Windows.old")
        if old_windows.exists():
            try:
                subprocess.run('takeown /f "C:\\Windows.old" /r /d y 2>nul', capture_output=True, shell=True, timeout=120)
                subprocess.run('icacls "C:\\Windows.old" /grant Administrators:F /T /Q 2>nul', capture_output=True, shell=True, timeout=120)
                subprocess.run('rd /s /q "C:\\Windows.old"', capture_output=True, shell=True, timeout=120)
                self.log("    [+] Windows.old removed.")
            except Exception as e:
                self.log(f"    [!] Failed to remove Windows.old: {e}")
        else:
            self.log("    [-] Windows.old not found.")

        self.log("[*] Running DISM WinSxS component cleanup (may take several minutes)...")
        try:
            subprocess.run("Dism /online /Cleanup-Image /StartComponentCleanup /ResetBase", capture_output=True, shell=True, timeout=600)
            self.log("    [+] WinSxS component cleanup completed.")
        except subprocess.TimeoutExpired:
            self.log("    [!] DISM timed out (still running in background).")
        except Exception as e:
            self.log(f"    [!] DISM cleanup failed: {e}")

        self.log("=== DEEP CLEANUP COMPLETE ===\n")
        self.root.after(0, lambda: self.btn_deep.config(state=tk.NORMAL))

    def dev_cleanup_worker(self):
        self.root.after(0, lambda: self.btn_dev.config(state=tk.DISABLED))
        self.log("\n=== STARTING DEV CACHE CLEANUP ===")
        
        
        self.log("    [i] Cleaning NuGet packages cache will require restoring all project packages.")
        self.clean_directory(r"%USERPROFILE%\.nuget\packages")
        
        
        commands = {
            "Python Pip": "pip cache purge",
            "Node NPM": "npm cache clean --force",
            ".NET NuGet": "dotnet nuget locals all --clear"
        }

        for name, cmd in commands.items():
            self.log(f"[*] Purging {name} Cache...")
            try:
                subprocess.run(cmd, capture_output=True, shell=True)
                self.log(f"    [+] {name} cache cleared.")
            except Exception as e:
                self.log(f"    [!] Failed to clear {name}: {e}")

        self.log("=== DEV CACHE CLEANUP COMPLETE ===\n")
        self.root.after(0, lambda: self.btn_dev.config(state=tk.NORMAL))

    def browser_cleanup_worker(self):
        self.root.after(0, lambda: self.btn_browser.config(state=tk.DISABLED))
        self.log("\n=== STARTING BROWSER CACHE CLEANUP ===")
        self.log("    [!] This will log you out of websites in Chrome, Edge, and Firefox.")

        browsers = [
            (r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache", "Chrome"),
            (r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache", "Edge"),
        ]
        for path, name in browsers:
            p = Path(os.path.expandvars(path))
            if p.exists():
                self.log(f"[*] Cleaning {name} cache...")
                self.clean_directory(str(p))
            else:
                self.log(f"    [-] {name} cache not found.")

        ff_profiles = Path(os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"))
        if ff_profiles.exists():
            for profile in ff_profiles.iterdir():
                cache2 = profile / "cache2"
                if cache2.exists():
                    self.log("[*] Cleaning Firefox cache...")
                    self.clean_directory(str(cache2))
                    break
            else:
                self.log("    [-] Firefox cache not found.")
        else:
            self.log("    [-] Firefox cache not found.")

        self.log("=== BROWSER CACHE CLEANUP COMPLETE ===\n")
        self.root.after(0, lambda: self.btn_browser.config(state=tk.NORMAL))

    def start_basic_cleanup(self):
        threading.Thread(target=self.basic_cleanup_worker, daemon=True).start()

    def start_deep_cleanup(self):
        threading.Thread(target=self.deep_cleanup_worker, daemon=True).start()

    def start_dev_cleanup(self):
        threading.Thread(target=self.dev_cleanup_worker, daemon=True).start()

    def start_browser_cleanup(self):
        threading.Thread(target=self.browser_cleanup_worker, daemon=True).start()

if __name__ == "__main__":
    
    if not is_admin():
       
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Administrator Rights Required", 
            "This cleanup utility must be run as Administrator to access system files.\n\nPlease right-click the script and select 'Run as Administrator'."
        )
        root.destroy()
    else:
       
        root = tk.Tk()
        app = CleanupApp(root)
        root.mainloop()