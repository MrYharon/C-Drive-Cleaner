# C-Drive-Cleaner
Simple 60 line python code that cleans your C: Drive for space


System Folders:
C:\Windows\System32\LogFiles **(System event and error logs)**
C:\Windows\Temp **(System-wide temporary files)**
C:\Windows\Prefetch **(Application launch caches)**
C:\Windows\logs\CBS **(Windows Update and Component-Based Servicing logs)**
C:\ProgramData\Microsoft\Windows Defender\Scans\History **(Windows Defender scan logs)**
C:\ProgramData\NVIDIA Corporation\Downloader **(Old NVIDIA driver installers)**

User Folders (e.g., C:\Users\Hugh\...):
...\AppData\Local\Temp **(Your local temporary application files)**
...\AppData\Local\Microsoft\Windows\INetCache **(Windows internet cache)**
...\AppData\Local\D3DSCache (**Direct3D Shader cache for gaming/graphics)**

Special Operations:
**The Recycle Bin:** Emptied completely via the native Windows API.
**Screenshots:** Deletes files in your Pictures\Screenshots folder.
