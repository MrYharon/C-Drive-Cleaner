# C-Drive-Cleaner

A simple, ~60-line Python utility script designed to automate the cleanup of your Windows C: Drive and free up storage space.

## What It Cleans

### System Folders
*(Note: These directories require the script to be run with Administrator privileges)*
* **`C:\Windows\System32\LogFiles`**: System event and error logs
* **`C:\Windows\Temp`**: System-wide temporary files
* **`C:\Windows\Prefetch`**: Application launch caches
* **`C:\Windows\logs\CBS`**: Windows Update and Component-Based Servicing logs
* **`C:\ProgramData\Microsoft\Windows Defender\Scans\History`**: Windows Defender scan logs
* **`C:\ProgramData\NVIDIA Corporation\Downloader`**: Old NVIDIA driver installers

### User Folders
*(Specific to the current logged-in user, e.g., `C:\Users\MrYayyeT\...`)*
* **`...\AppData\Local\Temp`**: Your local temporary application files
* **`...\AppData\Local\Microsoft\Windows\INetCache`**: Windows internet cache
* **`...\AppData\Local\D3DSCache`**: Direct3D Shader cache for gaming and graphics

### Special Operations
* **The Recycle Bin**: Emptied completely via the native Windows API.
* **Screenshots**: Deletes files located in your `Pictures\Screenshots` folder.
