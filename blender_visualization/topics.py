import bpy
import os
import sys
import json
import threading
import time
import paho.mqtt.client as mqtt
from dt_config import CONFIG, sensor_ifc_link, local_repository
import ifcopenshell
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool
import subprocess

"""
Run your own sys.path lines in Python Console in Blender before running this script.
(Replace the folder locations with your own Python folders and local Git repository)

import sys
sys.path.append('<path_to_your_own_python_Scripts>')
sys.path.append('<path_to_your_own_python_site-packages>')
sys.path.append('C<path_to_your_local_cic_dt_smartlab_repository>')

"""

# MQTT settings from CONFIG
MQTT_BROKER = CONFIG['mqtt_broker']
MQTT_PORT = CONFIG['mqtt_port']
MQTT_TOPICS = CONFIG['mqtt_topics']
TOPIC_FILE_PATH = CONFIG['TOPIC_FILE_PATH'] 
ifc_file = CONFIG['ifc_file']

# Group MQTT topics
group_keys = ['Livingroom',
              'Bedroom',
              'Bathroom',
              'Air-temperature',
              'Floor-temp',
              'CO2-ppm',
              'Rh',
              'M-bus',
              'KNX']

GROUPS_AND_TOPICS = {}
for k in group_keys:
    GROUPS_AND_TOPICS[k] = list(filter(lambda s: k.lower() in s.lower(), MQTT_TOPICS))

# Global variable to track the selected topics
selected_topics = GROUPS_AND_TOPICS['Livingroom']  # Default to the Livingroom topics
# Load the IFC model opened in Blender Bonsai
model = IfcStore.get_file()    

# Function to set up MQTT and subscribe to the selected topic
def setup_blender_mqtt():
    client = mqtt.Client()
    #client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(selected_topics)
    client.loop_start()

# Function to dynamically generate topic items based on the selected group
def get_dynamic_topic_items(self, context):
    selected_group = context.scene.selected_mqtt_group
    group_topics = GROUPS_AND_TOPICS.get(selected_group, [])
    if selected_group not in ['M-bus', 'KNX']:
        group_topics = ["all"] + group_topics  # Add 'all' option for specific groups
    return [(topic, topic, "") for topic in group_topics]

# Update function for the group selection
def update_selected_group(self, context):
    # Trigger a topic list update by reassigning the property
    context.scene.selected_mqtt_topic = context.scene.selected_mqtt_topic

# Function to update the selected topic and write it to a shared file
def update_selected_topics(self, context):
    global selected_topics
    selected_group = context.scene.selected_mqtt_group
    selected_topic = context.scene.selected_mqtt_topic
    
    if selected_topic == "all":
        selected_topics = GROUPS_AND_TOPICS.get(selected_group, [])
    else:
        selected_topics = [selected_topic]

    print(f"Selected topics updated to: {selected_topics}")

    # Select the IfcSpace entities by the selected_topic
    for topic in selected_topics:
        select_by_guid(model, topic)

    # Write the selected topic to the shared file
    with open(TOPIC_FILE_PATH, "w") as f:
        json.dump({"visual_topics": selected_topics}, f)

# Operator to start the Blender visualization (runs in a background thread)
class StartDataVisualizationOperator(bpy.types.Operator):
    bl_idname = "wm.start_data_visualization"
    bl_label = "Start Data Visualization"
    
    def execute(self, context):
        try:
            # Define the command to run the script in the new terminal
            # For Windows, using PowerShell or CMD
            if sys.platform == 'win32':
                # Open a new PowerShell or CMD window and run the script
                cmd = ['powershell', '-NoExit', '-Command', 'python main.py']
                subprocess.Popen(cmd, cwd=local_repository, creationflags=subprocess.CREATE_NEW_CONSOLE)

            # For macOS or Linux, you could use xterm or gnome-terminal, etc.
            else:
                cmd = ['gnome-terminal', '--', 'python', 'main.py']
                subprocess.Popen(cmd, cwd=cwd)

            self.report({'INFO'}, "Script executed successfully in a new terminal.")
        except Exception as e:
            self.report({'ERROR'}, f"Error executing script: {e}")

        return {'FINISHED'}
    
# Custom panel for topic selection in the 3D View
class TopicSelectionPanel(bpy.types.Panel):
    bl_label = "MQTT Topic Selection"
    bl_idname = "VIEW3D_PT_topic_selection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MQTT Visualization'

    def draw(self, context):
        layout = self.layout

        # Dropdown for groups
        layout.prop(context.scene, "selected_mqtt_group", text="Group")

        # Dropdown for topics
        layout.prop(context.scene, "selected_mqtt_topic", text="Topic")

        # Button to start visualization
        layout.operator("wm.start_data_visualization")

# Add a global variable to track previously selected GUIDs
previous_guids = []

def set_translucent_material(obj, color=None, transparency=0.2):
    """Set the material of an object to translucent."""
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="IfcSpaceMaterial")
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    for node in nodes:
        nodes.remove(node)

    # Create new nodes for transparency
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (300, 0)

    mix_shader = nodes.new(type="ShaderNodeMixShader")
    mix_shader.location = (100, 0)

    transparent_node = nodes.new(type="ShaderNodeBsdfTransparent")
    transparent_node.location = (-200, 100)

    diffuse_node = nodes.new(type="ShaderNodeBsdfDiffuse")
    diffuse_node.location = (-200, -100)

    if color:
        diffuse_node.inputs['Color'].default_value = color  # RGBA
    else:
        diffuse_node.inputs['Color'].default_value = [0.8, 0.8, 0.8, 1]

    links.new(transparent_node.outputs[0], mix_shader.inputs[1])
    links.new(diffuse_node.outputs[0], mix_shader.inputs[2])
    links.new(mix_shader.outputs[0], output_node.inputs[0])

    mix_shader.inputs[0].default_value = transparency

def set_all_ifcspaces_translucent(model):
    """Set all IfcSpace entities to translucent."""
    for entity in model.by_type("IfcSpace"):
        obj = tool.Ifc.get_object(entity)
        if obj:
            set_translucent_material(obj)

def select_by_guid(model, topic):
    global previous_guids
    current_guids = sensor_ifc_link[topic]

    # Revert the color of previously selected entities
    for guid in previous_guids:
        obj = tool.Ifc.get_object(model.by_guid(guid))
        if obj:
            set_translucent_material(obj)

    # Select and set color for the new GUIDs
    bpy.ops.object.select_all(action='DESELECT')
    for guid in current_guids:
        obj = tool.Ifc.get_object(model.by_guid(guid))
        if obj:
            # Set the object as active and selected
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            print(f"Object with GUID {guid} selected: {obj.name}")

            # Change color to red with transparency
            set_translucent_material(obj, color=[1, 0, 0, 1])

    # Update previous_guids
    previous_guids = current_guids

# Function to get the current topic for any Blender-specific functionality
def get_selected_topic():
    return selected_topics

# Register properties and classes
def register():
    # Properties for group and topics
    bpy.types.Scene.selected_mqtt_group = bpy.props.EnumProperty(
        name="MQTT Groups",
        description="Select the MQTT group for topics",
        items=[(group, group, "") for group in GROUPS_AND_TOPICS.keys()],
        update=update_selected_group,  # Update topics when the group changes
    )

    bpy.types.Scene.selected_mqtt_topic = bpy.props.EnumProperty(
        name="MQTT Topics",
        description="Select the MQTT topic for visualization",
        items=get_dynamic_topic_items,  # Dynamically generate items based on the selected group
        update=update_selected_topics,  # Trigger topic selection logic
    )

    bpy.utils.register_class(StartDataVisualizationOperator)
    bpy.utils.register_class(TopicSelectionPanel)

def unregister():
    del bpy.types.Scene.selected_mqtt_topic
    del bpy.types.Scene.selected_mqtt_group
    bpy.utils.unregister_class(StartDataVisualizationOperator)
    bpy.utils.unregister_class(TopicSelectionPanel)

if __name__ == "__main__":
    register()
