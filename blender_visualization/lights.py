import bpy
import bonsai.tool as tool

# Define UI properties for controlling lights
class LightProperties(bpy.types.PropertyGroup):
    toggle_lights: bpy.props.BoolProperty(
        name="Toggle Lights",
        description="Turn lights on/off",
        default=False
    )
    facade_1_color: bpy.props.FloatVectorProperty(
        name="Facade 1 Color",
        description="Color of the facade lights",
        subtype='COLOR',
        default=(1.0, 0.0, 0.0),  # Default red
        min=0.0,
        max=1.0
    )
    facade_2_color: bpy.props.FloatVectorProperty(
        name="Facade 2 Color",
        description="Color of the facade lights",
        subtype='COLOR',
        default=(0.0, 1.0, 0.0),  # Default green
        min=0.0,
        max=1.0
    )
    facade_3_color: bpy.props.FloatVectorProperty(
        name="Facade 3 Color",
        description="Color of the facade lights",
        subtype='COLOR',
        default=(0.0, 0.0, 1.0),  # Default blue
        min=0.0,
        max=1.0
    )

# Define the custom panel
class LIGHT_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Light Panel"
    bl_idname = "LIGHT_PT_CustomPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lights'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.light_toggle_props

        # Change the scenario settings
        layout.label(text="Step 1: Set the scene")
        layout.operator("view3d.set_rendered_world", text="Setup Rendered View")
        
        # Add Buttons to create the light objects in Blender
        layout.label(text="Step 2: Create lights")
        layout.operator("object.add_lights_from_ifc", text="Add Ceiling Lights")
        layout.operator("object.add_lights_for_facade", text="Add Facade Lights")

        # Toggle Lights Button
        layout.label(text="Step 3: Operate lights")
        layout.prop(props, "facade_1_color", text="Facade 1 Color")
        layout.prop(props, "facade_2_color", text="Facade 2 Color")
        layout.prop(props, "facade_3_color", text="Facade 3 Color")
        row = layout.row()
        row.prop(props, "toggle_lights", text="Lights On/Off")
        row.operator("object.toggle_lights", text="Update Lights")
        
        
# Function to delete existing lights based on their name
def delete_lights_starting_with(phrase):
    """Deletes light objects and their associated light data if their names start with the specified phrase."""
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name.startswith(phrase):
            # Remove the light data if it exists
            light_data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if light_data and light_data.name in bpy.data.lights:
                bpy.data.lights.remove(light_data, do_unlink=True)    

# Function to create a facade light
def add_facade_light(number,facade_color,location,self,scene):
    
    # Define light type
    light_data = bpy.data.lights.new(name=f"TempFacadeLightData_{number}", type='AREA')
    light_data.shape = 'RECTANGLE'
    light_data.energy = 100  # Set power to 100 W
    light_data.color = facade_color
    
    # Create the light object and position it
    light_obj = bpy.data.objects.new(name=f"TempFacadeLight_{number}", object_data=light_data) # Add "Temp" prefix for removing the light later
    light_obj.location = location
    scene.collection.objects.link(light_obj)
    
    self.report({'INFO'}, "Facade light added")
    #return {'FINISHED'}
            
            
# Operator to change the scene to rendered and change the background
class VIEW3D_OT_SetRenderedWorld(bpy.types.Operator):
    bl_idname = "view3d.set_rendered_world"
    bl_label = "Set Rendered Shading and Nishita"
    bl_description = "Set viewport shading to Rendered and change world background to Nishita Sky Texture"

    def execute(self, context):
        # Set the viewport shading to 'RENDERED'
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'RENDERED'

        # Ensure a world exists
        if not context.scene.world:
            context.scene.world = bpy.data.worlds.new("NewWorld")

        world = context.scene.world
        world.use_nodes = True

        # Set up Nishita Sky Texture in the world nodes
        node_tree = world.node_tree
        nodes = node_tree.nodes

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Add background and sky texture nodes
        bg_node = nodes.new(type="ShaderNodeBackground")
        sky_node = nodes.new(type="ShaderNodeTexSky")
        output_node = nodes.new(type="ShaderNodeOutputWorld")

        # Configure nodes
        sky_node.sky_type = 'NISHITA'
        sky_node.dust_density = 5.0  # Set Dust to 5
        bg_node.inputs[1].default_value = 0.05  # Set Strength to 0.05

        # Link nodes
        node_tree.links.new(bg_node.outputs[0], output_node.inputs[0])
        node_tree.links.new(sky_node.outputs[0], bg_node.inputs[0])

        # Arrange nodes
        bg_node.location = (0, 0)
        sky_node.location = (-200, 0)
        output_node.location = (200, 0)

        self.report({'INFO'}, "Viewport set to Rendered and world updated to Nishita Sky Texture")
        return {'FINISHED'}


# Operator to add ceiling lights for ifc objects
class OBJECT_OT_AddLightsFromIfc(bpy.types.Operator):
    """Create Blender light objects for ceiling lights in the IFC"""
    bl_idname = "object.add_lights_from_ifc"
    bl_label = "Add Lights from Ifc"

    def execute(self, context):
        scene = context.scene
        ifc = tool.Ifc.get()
        
        # Check that IFC data is found
        if ifc is None:
            self.report({'ERROR'}, "IFC data not available. Ensure the correct IFC file is loaded.")
            return {'CANCELLED'}
        
        # Collection of GUID data for the IfcLightFixture objects. Only ceiling lights for now
        light_guids = [
            "16X2fcwl585Ae$Kzb6g9Lt", 
            "16X2fcwl585Ae$Kzb6g9vQ",
            "16X2fcwl585Ae$Kzb6g9vD",
            "16X2fcwl585Ae$Kzb6g93c",
            "3Ofyv0fg57CegNBKT8C5Ye"
        ]
        
        # Delete any previously created lights
        delete_lights_starting_with("TempLight_")
        
        # Create a light in blender for each listed IFC light object
        for guid in light_guids:
        
            # Search for objects named "IfcLightFixture"
            for obj in scene.objects:
                ifc_element = tool.Ifc.get_entity(obj)
                
                # Check if the IFC element exists
                if ifc_element is None:
                    continue  # Skip objects with no IFC entity
                
                # Check that the GlobalId in Blender matches with the GUID of the object in IFC
                global_id = ifc_element.GlobalId
                if global_id == guid:

                    # Create a light at the object's location
                    light_data = bpy.data.lights.new(name=f"TempLight_{guid}", type='POINT')
                    light_data.energy = 100  # Set power to 100 W
                    light_data.color = (1.0, 0.8, 0.6)  # Warm hue (soft orange)

                    # Create the light object and position it
                    light_obj = bpy.data.objects.new(name=f"TempLight_{guid}", object_data=light_data)
                    light_obj.location = obj.location
                    light_obj.location.z -= 0.2 # Offset in Z direction
                    scene.collection.objects.link(light_obj)

        self.report({'INFO'}, "Lights added!")
        return {'FINISHED'}
    
# Operator to add fixed lights for the facade
class OBJECT_OT_AddLightsForFacade(bpy.types.Operator):
    """Create Blender light objects for the facade"""
    bl_idname = "object.add_lights_for_facade"
    bl_label = "Add Lights for facade"

    def execute(self, context):
        scene = context.scene
        props = scene.light_toggle_props
        props.facade_1_color

        # Facade light locations. Hard coded for now
        facade_1_location = (0.744,-0.920,2.894)
        facade_2_location = (-0.267,-2.031,2.894)
        facade_3_location = (-0.267,-4.104,2.894)
        
        # Delete any previously created lights
        delete_lights_starting_with("TempFacadeLight_")
        
        # Add facade lights in the locations
        add_facade_light(1,props.facade_1_color,facade_1_location,self,scene)
        add_facade_light(2,props.facade_2_color,facade_2_location,self,scene)
        add_facade_light(3,props.facade_3_color,facade_3_location,self,scene)

        self.report({'INFO'}, "Lights added!")
        return {'FINISHED'}

# Operator to update the lights
class OBJECT_OT_ToggleLights(bpy.types.Operator):
    """Update the color and the visibility of the lights"""
    bl_idname = "object.toggle_lights"
    bl_label = "Toggle Lights"

    def execute(self, context):
        scene = context.scene
        props = scene.light_toggle_props
        state = props.toggle_lights

        # Update visibility and color of light objects
        for obj in scene.objects:
            if obj.type == 'LIGHT':
                if obj.name.startswith("TempFacadeLight_"):
                    # Update colors of facade lights
                    if "1" in obj.name:
                        obj.data.color = props.facade_1_color
                    elif "2" in obj.name:
                        obj.data.color = props.facade_2_color
                    elif "3" in obj.name:
                        obj.data.color = props.facade_3_color
                
                # Toggle light visibility
                obj.hide_render = not state
                obj.hide_viewport = not state

        self.report({'INFO'}, f"Lights {'on' if state else 'off'}!")
        return {'FINISHED'}
        
# Register and Unregister Classes
classes = [
    LightProperties,
    LIGHT_PT_CustomPanel,
    VIEW3D_OT_SetRenderedWorld,
    OBJECT_OT_AddLightsFromIfc,
    OBJECT_OT_AddLightsForFacade,
    OBJECT_OT_ToggleLights
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.light_toggle_props = bpy.props.PointerProperty(type=LightProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.light_toggle_props

if __name__ == "__main__":
    register()
