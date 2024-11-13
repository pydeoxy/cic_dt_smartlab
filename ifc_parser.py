import os
import gdown
import requests
import ifcopenshell
from dt_config import CONFIG 
#from bonsai.bim.ifc import IfcStore
#import bonsai.tool as tool

# Google Drive file ID of the shared IFC model
file_id = "1Pc9irGXb5AJkfKpWgLCcPK7qiSLApx70"
# Local path to store the IFC model
ifc_file = CONFIG['ifc_file']

def download_ifc_file(file_id,ifc_file_path):
    # Construct the download URL
    url = f"https://drive.google.com/uc?id={file_id}"

    # Check if the file exists
    if os.path.exists(ifc_file_path):
        # Check the last modification time of the existing file
        local_mod_time = os.path.getmtime(ifc_file_path)
        
        # Request the file metadata from Google Drive to get the modification date
        # Using gdown to get metadata directly isn't supported, so we can either compare indirectly
        # or if access is granted use Google API, here we prompt the user directly.
        
        # Ask for user input to confirm download
        user_input = input(
            "Please compare the modification dates of the shared file and the local file. "
            "Enter 'Y' to download and replace the local file, or any other input to cancel the download "
            "and use the existing file: "
        )
        
        if user_input.strip().upper() == 'Y':
            # Download the file and overwrite the existing one
            gdown.download(url, ifc_file_path, quiet=False)
            print("File downloaded and replaced successfully.")
        else:
            print("Using the existing local file.")
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
    download_ifc_file(file_id,ifc_file)  
    model = parse_ifc_file(ifc_file)
    walls = model.by_type('IfcWallStandardCase')
    for wall in walls:
        print(wall.GlobalId)
