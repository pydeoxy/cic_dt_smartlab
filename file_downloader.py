import os
import gdown
import requests
import ifcopenshell
from dt_config import CONFIG 
import tkinter
from tkinter import messagebox
from datetime import datetime

def download_shared_file(file_id,file_path):
    # Construct the download URL
    url = f"https://drive.google.com/uc?id={file_id}"

    # Initialize Tkinter
    root = tkinter.Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Check if the file exists
    if os.path.exists(file_path):
        # Check the last modification time of the existing file
        local_mod_time = os.path.getmtime(file_path) 
        readable_time = datetime.fromtimestamp(local_mod_time).strftime('%Y-%m-%d %H:%M:%S')     
        
        # Show a confirmation popup
        user_response = messagebox.askyesno(
            f"{os.path.basename(file_path)} File Download Confirmation",
            "Please compare the modification dates of the shared file and the local file.\n\n"
            "Click 'Yes' to download and replace the local file.\n"
            "Click 'No' to cancel the download and use the existing file."
        )
        
        if user_response:
            # Download the file and overwrite the existing one
            gdown.download(url, file_path, quiet=False)
            print("File downloaded and replaced successfully.")            
        else:
            print("Using the existing local file.")
        print(f"{os.path.basename(file_path)} last modified time: {readable_time}")
    else:
        # Download the file if it doesn't exist
        gdown.download(url, file_path, quiet=False)
        print("File downloaded successfully.")

if __name__ == '__main__':  
    # Download or update IFC file
    download_shared_file(CONFIG['ifc_file_id'], CONFIG['ifc_file'])  
    # Download or update Excel file
    download_shared_file(CONFIG['mqtt_excel_id'], CONFIG["mqtt_excel"])