import bpy
import paho.mqtt.client as mqtt
import threading
from dt_config import CONFIG
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool
from mqtt_actuators import actuator_ifc_link, actuator_control, actuator_payload
from blender_visualization.topics import set_translucent_material

# MQTT settings from CONFIG
MQTT_BROKER = CONFIG["mqtt_broker"]
MQTT_PORT = CONFIG['mqtt_port']
ACTUATORS_TOPICS = list(actuator_ifc_link.keys())

# Group MQTT topics
actuator_keys = CONFIG["actuator_keys"]

ACTUATORS_AND_TOPICS = {}
for k in actuator_keys:
    ACTUATORS_AND_TOPICS[k] = list(filter(lambda s: k.lower() in s.lower(), ACTUATORS_TOPICS))

# Global variable to track the selected topics
selected_actuators = ACTUATORS_AND_TOPICS['Living room']  # Default to the Livingroom topics
# Global variable to store the latest payload
current_payload = ""
# Load the IFC model opened in Blender Bonsai
model = IfcStore.get_file()    
    
# Function to dynamically generate topic items based on the selected group
def get_dynamic_topic_items(self, context):
    selected_group = context.scene.selected_actuator_group
    group_topics = ACTUATORS_AND_TOPICS.get(selected_group, [])    
    return [(topic, topic, "") for topic in group_topics]

# Update function for the group selection
def update_selected_group(self, context):
    # Trigger a topic list update by reassigning the property
    context.scene.selected_mqtt_actuator = context.scene.selected_mqtt_actuator

# Function to update the selected topic and write it to a shared file
def update_selected_actuators(self, context):
    global selected_actuators
    selected_group = context.scene.selected_actuator_group
    selected_actuator = context.scene.selected_mqtt_actuator
    
    selected_actuators = [selected_actuator]

    print(f"Selected topics updated to: {selected_actuators}")

    # Select the IfcSpace entities by the selected_actuator
    for topic in selected_actuators:
        select_by_guid(model, topic)


# Custom panel for topic selection in the 3D View
class ActuatorSelectionPanel(bpy.types.Panel):
    bl_label = "MQTT Actuator Selection"
    bl_idname = "VIEW3D_PT_actuator_selection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Actuator Control'

    def draw(self, context):
        layout = self.layout

        # Dropdown for groups
        layout.prop(context.scene, "selected_actuator_group", text="Group")

        # Dropdown for topics
        layout.prop(context.scene, "selected_mqtt_actuator", text="Actuator")

        # Button to show current value
        layout.operator("wm.show_current_value")

        # Text input for payload
        layout.prop(context.scene, "payload_text", text="Payload")

        # Button to start visualization
        layout.operator("wm.publish_payload")

class ActuatorShowPayload(bpy.types.Operator):
    bl_idname = "wm.show_current_value"
    bl_label = "Show Current Value"   

    def execute(self, context):        
        topic = context.scene.selected_mqtt_actuator        
        current_value = actuator_payload(topic)
        # Display the value in a popup or a text block
        self.report({'INFO'}, f"Current value: {current_value}")
        return {'FINISHED'}        

class ActuatorPublishPayload(bpy.types.Operator):
    bl_idname = "wm.publish_payload"
    bl_label = "Publish Payload"

    def execute(self, context):
        topic = context.scene.selected_mqtt_actuator
        payload = context.scene.payload_text
        actuator_control(topic, payload)

        return {'FINISHED'}

# Add a global variable to track previously selected GUIDs
previous_guids = []

def select_by_guid(model, topic):
    global previous_guids
    current_guids = actuator_ifc_link[topic]

    # Revert the color of previously selected entities
    for guid in previous_guids:
        obj = tool.Ifc.get_object(model.by_guid(guid))
        if obj:
            set_translucent_material(obj, transparency=1)

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
            set_translucent_material(obj, color=[1, 0, 0, 1], transparency=1)

    # Update previous_guids
    previous_guids = current_guids

# Function to get the current topic for any Blender-specific functionality
def get_selected_actuator():
    return selected_actuators

# Register properties and classes
def register():
    # Properties for group and topics
    bpy.types.Scene.selected_actuator_group = bpy.props.EnumProperty(
        name="Actuator Groups",
        description="Select the Actuator group for topics",
        items=[(group, group, "") for group in ACTUATORS_AND_TOPICS.keys()],
        update=update_selected_group,  # Update topics when the group changes
    )

    bpy.types.Scene.selected_mqtt_actuator = bpy.props.EnumProperty(
        name="Actuator Topic",
        description="Select the Actuator topic for control",
        items=get_dynamic_topic_items,  # Dynamically generate items based on the selected group
        update=update_selected_actuators,  # Trigger topic selection logic
    )

    bpy.utils.register_class(ActuatorShowPayload)
    bpy.utils.register_class(ActuatorPublishPayload)
    bpy.utils.register_class(ActuatorSelectionPanel)
    bpy.types.Scene.payload_text = bpy.props.StringProperty()

def unregister():
    del bpy.types.Scene.selected_mqtt_actuator
    del bpy.types.Scene.selected_actuator_group
    bpy.utils.unregister_class(ActuatorShowPayload)
    bpy.utils.unregister_class(ActuatorPublishPayload)
    bpy.utils.unregister_class(ActuatorSelectionPanel)
    bpy.types.Scene.payload_text

if __name__ == "__main__":
    register()
