import ctypes
import os
import shutil

# Function to delete files and folders in a specified directory
def delete_files_and_folders(folder_path):
    for item_name in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item_name)
        try:
            
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"Deleted file: {item_name}")
                
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Deleted folder: {item_name}")
                
        except Exception as e:
            print(f"Skipped {item_name} (Locked or Access Denied)")

def empty_recycle_bin():
    print("Starting cleanup for: Recycle Bin...\n")
    try:
        # SHEmptyRecycleBinW flags:
        # 1 = No confirmation dialog
        # 2 = No progress UI
        # 4 = No sound
        # 1 + 2 + 4 = 7
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        
        if result == 0:
            print("Successfully emptied the Recycle Bin!")
        else:
            print("Recycle Bin was already empty.")
    except Exception as e:
        print(f"Skipped Recycle Bin: {e}")
    print("\n")
    
if __name__ == "__main__":

    # deletion of the system Logs & Caches

   import os

# System folders
delete_files_and_folders(r"C:\Windows\System32\LogFiles")
delete_files_and_folders(r"C:\Windows\Temp") 
delete_files_and_folders(r"C:\Windows\Prefetch")
delete_files_and_folders(r"C:\Windows\logs\CBS")
delete_files_and_folders(r"C:\ProgramData\Microsoft\Windows Defender\Scans\History")


# User folders 
delete_files_and_folders(os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\Temp"))
delete_files_and_folders(os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\Microsoft\Windows\INetCache"))
delete_files_and_folders(os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\D3DSCache")) 
delete_files_and_folders(os.path.expandvars(r"C:\Users\%USERNAME%\Pictures\Screenshots"))

# Recycle Bin
empty_recycle_bin()
