import bpy
import os
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

bl_info = {
    "name": "Mixamo for UE5 Mannequin Animation Fixer",
    "description": "Fixes UE5 Mannequin Animations exported from Mixamo.",
    "author": "Spicy Game Ingridients",
    "version": (1, 0),
    "blender": (3, 6, 1),
    "location": "File > Export",
    "warning": "Overwrites the already converted animations!", # used for warning icon and text in addons panel
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Animation",
}

def show_message(message = "", title = "Error", icon = 'ERROR'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

class MixamoUE5MannequinFixer(Operator):

    bl_idname = "example.select_dir"
    bl_label = "Select this folder"
    bl_options = {'REGISTER'}
    # Tell 'fileselect_add' it should use a directoy
    directory: StringProperty(
        name="Outdir Path",
        description="Outdir Path"
        )
    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
        )
    output_filename_prefix: StringProperty(
        name="Prefix",
        description="Prefix of the fixed files",
        default="AS_")
    output_filename_suffix: StringProperty(
        name="Suffix",
        description="Suffix of the fixed files",
        default="_UE5M")

    def execute(self, context):
        for file in os.listdir(self.directory):
            if file.lower().endswith('.fbx'):
                self.process(file)
        #show_message(message = "Export has finished. You can find your fixed files in " + os.path.join(self.directory, "UE5"), title = "Finished", icon = 'INFO')
        self.report({'INFO'}, "Export has finished. You can find your fixed files in " + os.path.join(self.directory, "Fixed"))
        return {'FINISHED'}

    def invoke(self, context, event):
        # Open browser, take reference to 'self' read the path to selected file, put path in predetermined self fields.
        # See: https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        context.window_manager.fileselect_add(self)
        # Tell Blender to hang on for the slow user input
        return {'RUNNING_MODAL'}

    def process(self, filename):
        bpy.ops.scene.new(type='NEW') # Create a temporary scene to only 'mess' with it and delte it after the fix
        try:
            in_filepath = os.path.join(self.directory, filename)
            output_directory = os.path.join(self.directory, "Fixed")
            output_filename = self.output_filename_prefix + os.path.splitext(filename)[0] + self.output_filename_suffix + os.path.splitext(filename)[1]
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            output_filepath = os.path.join(output_directory, output_filename)
            bpy.ops.import_scene.fbx(filepath = in_filepath) # Load FBX in the temporary scene
            current_object = bpy.context.object
            armature = current_object.data
            bpy.ops.object.mode_set(mode = 'EDIT') # Switch to EDIT mode
            root_bone = None # Search for the root bone:
            for bone in armature.edit_bones:
                if(bone.parent == None):
                    root_bone = bone
            for bone in armature.edit_bones: # Make all children of the root bone parentless:
                if(bone.parent == root_bone):
                    bone.parent = None
            armature.edit_bones.remove(root_bone) # Remove the (meanwhile) childless root bone
            current_object.name = "root" # IMPORTANT: Rename the object itself to "root"
            bpy.ops.object.mode_set(mode = 'OBJECT')  # Switch to Object mode
            # Export the fixed FBX:
            bpy.ops.export_scene.fbx(filepath=output_filepath, check_existing=False, filter_glob='*.fbx', use_selection=True, use_visible=False, use_active_collection=False, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', use_space_transform=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF', colors_type='SRGB', prioritize_active_color=False, use_subsurf=False, use_mesh_edges=False, use_tspace=False, use_triangles=False, use_custom_props=False, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True, axis_forward='-Z', axis_up='Y')
        except:
            #show_message(output_filepath + " could not be converted. (Probably a wrong FBX format.)")
            self.report({'ERROR'}, output_filepath + " could not be converted. (Probably a wrong FBX format.)")
        bpy.ops.scene.delete() # Delete the temporary scene after the fix	

def menu_func_export(self, context):
    self.layout.operator(MixamoUE5MannequinFixer.bl_idname, text="Export Fixed Mixamo Animations for UE5 Mannequins")

def register():
    bpy.utils.register_class(MixamoUE5MannequinFixer)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(MixamoUE5MannequinFixer)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


# Invoke register if started from editor
if __name__ == "__main__":
    register()
    #bpy.ops.example.select_dir('INVOKE_DEFAULT')
