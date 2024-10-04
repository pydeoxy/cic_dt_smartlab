import ifcopenshell
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool

def parse_ifc_file():
    # Load the IFC model opened in Blender Bonsai
    model = IfcStore.get_file()
    # Extract building geometry and sensor locations
    # Add code here
    # Return a data structure representing the building
    return model


if __name__ == '__main__':    
    model = parse_ifc_file()
    walls = model.by_type('IfcWallStandardCase')
    for wall in walls:
        print(wall.GlobalId)
