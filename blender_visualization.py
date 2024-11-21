import bpy
import os
import json
import threading
import time
import paho.mqtt.client as mqtt
from dt_config import CONFIG, sensor_ifc_link
import ifcopenshell
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool

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

# Global variable to track the selected topic
selected_topic = MQTT_TOPICS[0]  # Default to the first topic
# Load the IFC model opened in Blender Bonsai
model = IfcStore.get_file()    

# Function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    if msg.topic == selected_topic:
        try:
            sensor_data = json.loads(msg.payload.decode('utf-8'))
            value = float(sensor_data["value"])

            # Map value to color
            color = [min(value / 100, 1), 0.2, 1 - min(value / 100, 1), 1]  # Example RGB mapping
            print(f"Changing color to: {color} for value: {value}")

            # Change color of an object in Blender (adjust 'Cube' to your object name)
            bpy.data.objects['Cube'].active_material.diffuse_color = color
        except Exception as e:
            print(f"Failed to update color: {e}")


# Function to set up MQTT and subscribe to the selected topic
def setup_blender_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(selected_topic)
    client.loop_start()

# Operator to start the Blender visualization (runs in a background thread)
class StartBlenderVisualizationOperator(bpy.types.Operator):
    bl_idname = "wm.start_blender_visualization"
    bl_label = "Start Blender Visualization"
    _timer = None
    client = None

    def execute(self, context):
        # Set up MQTT in a background thread
        threading.Thread(target=setup_blender_mqtt, daemon=True).start()
        self._timer = context.window_manager.event_timer_add(1.0, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            # Check for real-time updates
            pass
        return {'PASS_THROUGH'}

    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)

# Custom panel for topic selection in the 3D View
class TopicSelectionPanel(bpy.types.Panel):
    bl_label = "MQTT Topic Selection"
    bl_idname = "VIEW3D_PT_topic_selection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MQTT Visualization'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, "selected_mqtt_topic", text="MQTT Topic")
        row = layout.row()
        row.operator("wm.start_blender_visualization")

def select_by_guid(model, topic):
    guids = sensor_ifc_link[topic]
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Find the object with the specified GUID    
    for guid in guids:
        obj = tool.Ifc.get_object(model.by_guid(guid))
        # Set the object as active and selected
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        print(f"Object with GUID {guid} selected: {obj.name}")
    else:
        print(f"No object found with GUID: {guid}")

# Function to update the selected topic and write it to a shared file
def update_selected_topic(self, context):
    global selected_topic
    selected_topic = context.scene.selected_mqtt_topic
    print(f"Selected topic updated to: {selected_topic}")

    # Select the IfcSpace entities by the selected_topic
    select_by_guid(model, selected_topic)

    # Write the selected topic to the shared file
    with open(TOPIC_FILE_PATH, "w") as f:
        json.dump({"visual_topic": selected_topic}, f)

# Function to get the current topic for any Blender-specific functionality
def get_selected_topic():
    return selected_topic

# Register properties and classes
def register():
    bpy.types.Scene.selected_mqtt_topic = bpy.props.EnumProperty(
        name="MQTT Topics",
        description="Select the MQTT topic for visualization",
        items=[(topic, topic, "") for topic in MQTT_TOPICS],
        update=update_selected_topic,
    )
    bpy.utils.register_class(StartBlenderVisualizationOperator)
    bpy.utils.register_class(TopicSelectionPanel)

def unregister():
    del bpy.types.Scene.selected_mqtt_topic
    bpy.utils.unregister_class(StartBlenderVisualizationOperator)
    bpy.utils.unregister_class(TopicSelectionPanel)

if __name__ == "__main__":
    register()
