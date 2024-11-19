import os
import gdown
import requests
import ifcopenshell
from dt_config import CONFIG 
import tkinter
from tkinter import messagebox
from datetime import datetime
#from bonsai.bim.ifc import IfcStore
#import bonsai.tool as tool

def download_ifc_file(file_id,ifc_file_path):
    # Construct the download URL
    url = f"https://drive.google.com/uc?id={file_id}"

    # Initialize Tkinter
    root = tkinter.Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Check if the file exists
    if os.path.exists(ifc_file_path):
        # Check the last modification time of the existing file
        local_mod_time = os.path.getmtime(ifc_file_path) 
        readable_time = datetime.fromtimestamp(local_mod_time).strftime('%Y-%m-%d %H:%M:%S')     
        
        # Show a confirmation popup
        user_response = messagebox.askyesno(
            "File Download Confirmation",
            "Please compare the modification dates of the shared IFC file and the local IFC file.\n\n"
            "Click 'Yes' to download and replace the local file.\n"
            "Click 'No' to cancel the download and use the existing file."
        )
        
        if user_response:
            # Download the file and overwrite the existing one
            gdown.download(url, ifc_file_path, quiet=False)
            print("File downloaded and replaced successfully.")
        else:
            print("Using the existing local IFC file.")
            print(f"Last modified time: {readable_time}")
    else:
        # Download the file if it doesn't exist
        gdown.download(url, ifc_file_path, quiet=False)
        print("File downloaded successfully.")

def parse_ifc_file(ifc_file_path):
    # Load the IFC model opened in Blender Bonsai
    #model = IfcStore.get_file()
    # Open the temporary IFC file with ifcopenshell
    model = ifcopenshell.open(ifc_file_path)
    # Extract building geometry and sensor locations
    # Add code here
    # Return a data structure representing the building
    return model

if __name__ == '__main__':  
    # Google Drive file ID of the shared IFC model
    file_id = CONFIG['ifc_file_id']
    # Local path to store the IFC model
    ifc_file = CONFIG['ifc_file']
    download_ifc_file(file_id,ifc_file)  
    #model = parse_ifc_file(ifc_file)
    #walls = model.by_type('IfcWallStandardCase')
    #for wall in walls:
    #    print(wall.GlobalId)
