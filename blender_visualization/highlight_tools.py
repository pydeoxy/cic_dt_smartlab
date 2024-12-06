import bpy
from mathutils import Vector, Matrix, Color
from math import radians
from bpy.props import FloatProperty, FloatVectorProperty

# Global lists to keep track of the created objects so that we can delete them later
created_label = []
created_legend = []

# Define useful functions to be used later 

# Function 1: Clear all highlight effects
def clear_highlight(obj):
    if obj is None:
        return
    
    # Reset material
    if obj.active_material:
        obj.active_material.use_nodes = False
    
    # Reset in-front display
    obj.show_in_front = False
    
# Function 2: Delete a list of objects
def delete_objects(obj_list):
    """Delete objects from the Blender scene."""
    for obj in obj_list:
        if obj and obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    obj_list.clear()  # Clear the list to avoid dangling references
    
# Function 3: Make selected object transparent
def make_transparent(obj):
    if obj.type == 'MESH':
        # Ensure the object has a material
        if not obj.data.materials:
            mat = bpy.data.materials.new(name="TransparentMaterial")
            obj.data.materials.append(mat)
        else:
            mat = obj.data.materials[0]
        
        # Set up the material
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)
        
        # Add necessary nodes
        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        output_node.location = (400, 0)
        
        principled_node = nodes.new(type="ShaderNodeBsdfPrincipled")
        principled_node.location = (0, 0)
        principled_node.inputs["Alpha"].default_value = 0.3  # Set transparency
        
        # Link nodes
        links.new(principled_node.outputs["BSDF"], output_node.inputs["Surface"])
        
        # Ensure the material uses alpha blending
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'HASHED'
        
# Function 4: Check if an object is within a bounding box
def is_within_bounding_box(bbox, obj):
    # Get the world space bounding box of the other object
    obj_bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    for corner in obj_bbox:
        if (bbox['min_x'] <= corner.x <= bbox['max_x'] or
            bbox['min_y'] <= corner.y <= bbox['max_y'] or
            bbox['min_z'] <= corner.z <= bbox['max_z']):
            return False  # At least one corner is inside the bounding box
    return True  # All corners are outside

# Define highlight methods

# Highlight method 1: Glow / Emission Material
class OBJECT_OT_HighlightGlow(bpy.types.Operator):
    """Apply Glow or Emission Material to the selected object"""
    bl_idname = "object.highlight_glow"
    bl_label = "Highlight Glow"

    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({'WARNING'}, "No object selected.")
            return {'CANCELLED'}
        
        # Define material
        mat = bpy.data.materials.new(name="GlowMaterial")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Create emission shader
        for node in nodes:
            nodes.remove(node)
        emission_node = nodes.new(type="ShaderNodeEmission")
        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        links.new(emission_node.outputs[0], output_node.inputs[0])
        
        # Set material properties
        emission_node.inputs[0].default_value = (1.0, 1.0, 0.0, 1.0)  # Yellow
        emission_node.inputs[1].default_value = 10  # Intensity
        
        # Apply created material
        obj.data.materials.clear()
        obj.data.materials.append(mat)

        self.report({'INFO'}, "Glow effect applied.")
        return {'FINISHED'}

# Highlight method 2: Pulsing Color Effect
class OBJECT_OT_HighlightPulse(bpy.types.Operator):
    """Apply Pulsing Color Effect to the selected object"""
    bl_idname = "object.highlight_pulse"
    bl_label = "Highlight Pulse"

    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({'WARNING'}, "No object selected.")
            return {'CANCELLED'}

        # Create a material with pulsing animation
        mat = bpy.data.materials.new(name="PulseMaterial")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Create emission shader
        for node in nodes:
            nodes.remove(node)
        emission_node = nodes.new(type="ShaderNodeEmission")
        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        math_node = nodes.new(type="ShaderNodeMath")
        math_node.operation = 'MULTIPLY'
        links.new(emission_node.outputs[0], output_node.inputs[0])
        links.new(math_node.outputs[0], emission_node.inputs[1])

        # Set node properties
        emission_node.inputs[0].default_value = (0.0, 1.0, 1.0, 1.0)  # Cyan
        math_node.inputs[1].default_value = 5.0

        # Apply created material
        obj.data.materials.clear()
        obj.data.materials.append(mat)

        # Animate pulsing
        frame_start = bpy.context.scene.frame_current
        math_node.inputs[0].default_value = 0.0
        math_node.inputs[0].keyframe_insert(data_path="default_value", frame=frame_start)
        math_node.inputs[0].default_value = 1.0
        math_node.inputs[0].keyframe_insert(data_path="default_value", frame=frame_start + 25)
        math_node.inputs[0].default_value = 0.0
        math_node.inputs[0].keyframe_insert(data_path="default_value", frame=frame_start + 50)

        # Add Cycles modifier to loop animation
        action = math_node.id_data.animation_data.action
        fcurve = action.fcurves.find("nodes[\"Math\"].inputs[0].default_value")
        if fcurve:
            fcurve.modifiers.new(type='CYCLES')
        
        # Start animation. It will be stopped later if the highlight effect is disabled
        if not bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()

        self.report({'INFO'}, "Pulsing color effect applied.")
        return {'FINISHED'}

# Highlight method 3: Enable In-Front Display
class OBJECT_OT_HighlightInFront(bpy.types.Operator):
    """Enable In-Front Display for the selected object"""
    bl_idname = "object.highlight_in_front"
    bl_label = "Highlight In Front"

    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({'WARNING'}, "No object selected.")
            return {'CANCELLED'}
        
        # Set object to be displayed in front of other objects (Only in Solid shading of the viewport)
        obj.show_in_front = True
        
        self.report({'INFO'}, "In-Front display enabled.")
        return {'FINISHED'}

# Highlight method 4: Make object transparent
class OBJECT_OT_MakeTransparent(bpy.types.Operator):
    """Make selected object transparent."""
    bl_idname = "object.make_transparent"
    bl_label = "Make Transparent"
    bl_description = "Make selected objects transparent"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for obj in context.selected_objects:
            
            # Use the predefined function (3) to make the selected object transparent
            make_transparent(obj)
        
        self.report({'INFO'}, "Selected objects made transparent")
        return {'FINISHED'}

    
# Disable highlight for the object
class OBJECT_OT_HighlightNone(bpy.types.Operator):
    """Disable highlight effects and reset the scene"""
    bl_idname = "object.highlight_none"
    bl_label = "Reset highlight effects"

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            
            # Use predefined function (1) to clear the highlight effects from the selected object
            clear_highlight(obj)
        
        # Stop animation in case it is running
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
        
        # Use predefined function (2) to delete any created objects
        delete_objects(created_label)
        delete_objects(created_legend)
        
        self.report({'INFO'}, "Highlights cleared")
        return {'FINISHED'}

# Add a label text for the selected object
class OBJECT_OT_AddTextAboveObject(bpy.types.Operator):
    """Show a label text for the selected object."""
    bl_idname = "object.add_text_above_object"
    bl_label = "Add Label Text"
    
    # Set a fixed location in 3D space (hard coded for now)
    fixed_location = Vector((6.0, -6.0, 7.0))

    def execute(self, context):
        # Get the active object
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        # Delete the existing label if it exists
        delete_objects(created_label)

        # Create new text object
        bpy.ops.object.text_add(location=self.fixed_location)
        text_obj = context.object
        text_obj.name = "FixedLocationText"
        text_obj.data.body = obj.name
        text_obj.data.align_x = 'CENTER'

        # Rotate the text to face a specific direction (hard coded direction for now)
        text_obj.rotation_euler = (radians(90), 0, radians(245))  
        
        # Add the label to the list of created label objects
        created_label.append(text_obj)

        self.report({'INFO'}, f"Text added at fixed location: {self.fixed_location}")
        return {'FINISHED'}
    
# Hide any objects outside the selected object's boundary
class OBJECT_OT_Isolate(bpy.types.Operator):
    """Hide any objects outside the selected object's boundary."""
    bl_idname = "object.isolate_object"
    bl_label = "Isolate objects"

    def execute(self, context):
        # Get all selected objects
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            print("No objects selected!")
            return
        
        # Compute bounding boxes for all selected objects
        bounding_boxes = []
        for obj in selected_objects:
            # Calculate the world space bounding box
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            bbox = {
                'min_x': min([v.x for v in bbox_corners]),
                'max_x': max([v.x for v in bbox_corners]),
                'min_y': min([v.y for v in bbox_corners]),
                'max_y': max([v.y for v in bbox_corners]),
                'min_z': min([v.z for v in bbox_corners]),
                'max_z': max([v.z for v in bbox_corners])
            }
            bounding_boxes.append(bbox)
        
        # Make all objects in the scene transparent
        for obj in bpy.context.scene.objects:
            make_transparent(obj)

        # Unhide objects within the selected objects' bounding boxes
        for obj in bpy.context.scene.objects:
            for bbox in bounding_boxes:
                if is_within_bounding_box(bbox, obj):
                    clear_highlight(obj)
                    break  # If one bounding box contains the object, no need to 
                
        # Set the visibility of the originally selected objects
        for obj in selected_objects:
            clear_highlight(obj) # Could be changed to something else
        return {'FINISHED'}
    
# Add a color legend for the coloring of objects
class OBJECT_OT_AddLegend(bpy.types.Operator):
    """Show a color legend for the color scale of objects."""
    bl_idname = "object.add_color_legend"
    bl_label = "Add Legend"
    
    # Set fixed locations in 3D space (hard coded locations for now)
    fixed_location_1 = Vector((6.0, -6.0, 5)) # Gradient
    fixed_location_2 = Vector((4.5, -9, 5.9)) # Min value
    fixed_location_3 = Vector((7.4, -2.9, 5.9)) # Max value
    
    
    def execute(self, context):
        
        # Delete the existing legend if it exists
        delete_objects(created_legend)
        
        # Access properties from the panel
        min_val = context.scene.color_legend_min
        max_val = context.scene.color_legend_max
        min_color = context.scene.color_legend_min_color
        max_color = context.scene.color_legend_max_color
        
        # Set the dimensions for the legend
        width = 10
        height = 2
        
        # Create min value text object
        bpy.ops.object.text_add(location=self.fixed_location_3)
        text_obj = context.object
        text_obj.name = "MinText"
        text_obj.data.body = str(min_val)
        text_obj.data.align_x = 'CENTER'
        text_obj.rotation_euler = (radians(90), 0, radians(245)) # Rotate the text to face a specific direction
        
        created_legend.append(text_obj) # Add the text to created objects
        
        # Create max value text object
        bpy.ops.object.text_add(location=self.fixed_location_2)
        text_obj = context.object
        text_obj.name = "MaxText"
        text_obj.data.body = str(max_val)
        text_obj.data.align_x = 'CENTER'
        text_obj.rotation_euler = (radians(90), 0, radians(245)) # Rotate the text to face a specific direction
        
        created_legend.append(text_obj) # Add the text to created objects

        # Create a plane for the legend
        bpy.ops.mesh.primitive_plane_add(size=1.5, location=self.fixed_location_1)
        plane = bpy.context.object
        plane.scale.x = width / 2
        plane.scale.y = height / 2
        plane.name = "Color Legend"
        
        # Rotate the legend to face a specific direction
        plane.rotation_euler = (radians(90), 0, radians(245)) 
        
        # Add a material with a gradient texture
        mat = bpy.data.materials.new(name="ColorLegendMaterial")
        mat.use_nodes = True
        plane.data.materials.append(mat)
        
        created_legend.append(plane) # Add the plane to created objects

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Add shader nodes
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (400, 0)

        shader_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        shader_node.location = (200, 0)

        gradient_node = nodes.new(type='ShaderNodeTexGradient')
        gradient_node.location = (-200, 0)

        mapping_node = nodes.new(type='ShaderNodeMapping')
        mapping_node.location = (-400, 0)

        texture_coord_node = nodes.new(type='ShaderNodeTexCoord')
        texture_coord_node.location = (-600, 0)

        color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
        color_ramp_node.location = (0, 0)

        # Set gradient colors
        color_ramp_node.color_ramp.elements[0].color = (*min_color, 1.0)  # Min color
        color_ramp_node.color_ramp.elements[1].color = (*max_color, 1.0)  # Max color

        # Connect nodes
        links.new(texture_coord_node.outputs['Generated'], mapping_node.inputs['Vector'])
        links.new(mapping_node.outputs['Vector'], gradient_node.inputs['Vector'])
        links.new(gradient_node.outputs['Fac'], color_ramp_node.inputs['Fac'])
        links.new(color_ramp_node.outputs['Color'], shader_node.inputs['Base Color'])
        links.new(shader_node.outputs['BSDF'], output_node.inputs['Surface'])

        self.report({'INFO'}, "Color Legend Created!")
        return {'FINISHED'}

# Interpolate to get the correct color between min and max hues
class OBJECT_OT_Color(bpy.types.Operator):
    """Change the color of the selected object"""
    bl_idname = "object.color"
    bl_label = "Set Color"
    bl_description = "Set object color based on the value"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        # Access properties from the panel
        min_val = context.scene.color_legend_min
        max_val = context.scene.color_legend_max
        min_color = context.scene.color_legend_min_color
        max_color = context.scene.color_legend_max_color
        input_val = context.scene.color_value
        
        obj = context.active_object
        
        # Check that an object is selected
        if obj is None:
            self.report({'WARNING'}, "No object selected.")
            return {'CANCELLED'}
        
        # Get color range
        min_color = Color(min_color[:3])  # Convert to Color type
        max_color = Color(max_color[:3])  # Convert to Color type
        
        # Determine color based on input value
        if input_val < min_val:
            result_color = min_color
        elif input_val > max_val:
            result_color = max_color
        else:
            # Interpolate between min_color and max_color
            t = (input_val - min_val) / (max_val - min_val)
            result_color = Color((
                (1 - t) * min_color.r + t * max_color.r,
                (1 - t) * min_color.g + t * max_color.g,
                (1 - t) * min_color.b + t * max_color.b
            ))
        

        # Apply the color to the active object
        if obj and obj.type == 'MESH':  # Ensure there's an active mesh object
            if not obj.data.materials:
                mat = bpy.data.materials.new(name="CustomMaterial")
                obj.data.materials.append(mat)
            else:
                mat = obj.data.materials[0]

            # Setup material
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            # Clear existing nodes
            for node in nodes:
                nodes.remove(node)

            # Add necessary nodes
            output_node = nodes.new(type="ShaderNodeOutputMaterial")
            output_node.location = (400, 0)

            bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
            bsdf_node.location = (0, 0)

            # Link nodes
            links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

            # Set color and ensure no transparency
            bsdf_node.inputs["Base Color"].default_value = (result_color.r, result_color.g, result_color.b, 1.0)
            bsdf_node.inputs["Alpha"].default_value = 1.0
            mat.blend_method = 'OPAQUE'
            mat.shadow_method = 'OPAQUE'
            
        self.report({'INFO'}, "Selected object's color adjusted")
        return {'FINISHED'}


# Create the UI panel
class OBJECT_PT_HighlightPanel(bpy.types.Panel):
    """Panel for Visualization features"""
    bl_label = "Visualization tools"
    bl_idname = "OBJECT_PT_highlight_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Visualization tools'

    def draw(self, context):
        layout = self.layout
        
        # Section 1: Highlight Options
        box = layout.box()
        box.label(text="Highlight Options", icon='LIGHT')
        col = box.column(align=True)
        col.operator("object.highlight_glow", text="Glow")
        col.operator("object.highlight_pulse", text="Pulse")
        col.operator("object.highlight_in_front", text="In Front")
        col.operator("object.make_transparent", text="Transparent")
        
        # Section 2: Object Manipulation
        box = layout.box()
        box.label(text="Object Manipulation", icon='MODIFIER')
        col = box.column(align=True)
        col.operator("object.add_text_above_object", text="Add Label Text")
        col.operator("object.isolate_object", text="Isolate Object(s)")
        
        # Section 3: Color Legend
        box = layout.box()
        box.label(text="Color Legend", icon='COLOR')
        
        # Add input fields for minimum and maximum values
        row = box.row()
        row.prop(context.scene, "color_legend_min_color", text="Min Color")
        row.prop(context.scene, "color_legend_min", text="Min Value")
        row = box.row()
        row.prop(context.scene, "color_legend_max_color", text="Max Color")
        row.prop(context.scene, "color_legend_max", text="Max Value")
        box.operator("object.add_color_legend", text="Add Color Legend")
        
        # Section 4: Set object color
        box = layout.box()
        box.label(text="Coloring test", icon='SHADERFX')
        box.label(text="Set object color based on input value")
        row = box.row()
        row.prop(context.scene, "color_value") # Add value input field
        row.operator("object.color")
        row = layout.row()
        
        # Reset button
        row.operator("object.highlight_none", text="Reset scene")
        

# Registration
classes = [
    OBJECT_OT_HighlightGlow,
    OBJECT_OT_HighlightPulse,
    OBJECT_OT_HighlightInFront,
    OBJECT_OT_MakeTransparent,
    OBJECT_OT_HighlightNone,
    OBJECT_OT_AddTextAboveObject,
    OBJECT_OT_Isolate,
    OBJECT_OT_AddLegend,
    OBJECT_OT_Color,
    OBJECT_PT_HighlightPanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # Add custom properties to the scene
    bpy.types.Scene.color_legend_min = FloatProperty(
        name="Min Value",
        description="Minimum value for the color legend",
        default=0.0
    )
    bpy.types.Scene.color_legend_max = FloatProperty(
        name="Max Value",
        description="Maximum value for the color legend",
        default=1.0
    )
    bpy.types.Scene.color_legend_min_color = FloatVectorProperty(
        name="Min Color",
        description="RGB color for the minimum value",
        subtype='COLOR',
        default=(0.0, 0.0, 1.0),
        min=0.0, max=1.0
    )
    bpy.types.Scene.color_legend_max_color = FloatVectorProperty(
        name="Max Color",
        description="RGB color for the maximum value",
        subtype='COLOR',
        default=(1.0, 0.0, 0.0),
        min=0.0, max=1.0
    )
    bpy.types.Scene.color_value = FloatProperty(
        name="Input",
        description="Value for coloring the object",
        default=1.0
    )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    # Remove custom properties
    del bpy.types.Scene.color_legend_min
    del bpy.types.Scene.color_legend_max
    del bpy.types.Scene.color_legend_min_color
    del bpy.types.Scene.color_legend_max_color

if __name__ == "__main__":
    register()