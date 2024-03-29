bl_info = {
    "name": "Batch Image Seq to GP",
    "description": "Automation script to Create a grease pencil object from image sequence",
    "author": "MercuryRaven",
    "version": (0, 0, 2 ),
    "blender": (2, 80, 0),
    "location": "Image Editor > Sidebar > Image",
    "warning": "Prone to crashing, not production ready..", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": ""
}
import bpy
import socket
import sys
import mathutils
import math
import bpy.ops
#import bpy.data

from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       Scene
                       )
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )

class ImgSetting(PropertyGroup):
    gp_name : StringProperty(
        name="Grease pencil name",
        description = "insert name of the new grease pencil here",
        default = 'Sprite'

    )

    newlyr_name : StringProperty(
        name="new layer name",
        description = "insert name of the layer here here",
        default = 'Frames'

    )

    seq_length : IntProperty(
        name= "Sequence length",
        description = "set length here",
        default = 10
    )

    start_frame : IntProperty(
        name= "Start Frame",
        description = "set length here",
        default = 1
    )

    gp_target : PointerProperty(type=bpy.types.GreasePencil,name="")
    gpo_target : PointerProperty(type=bpy.types.Object,name="")

class createGP(bpy.types.Operator):
    """Operator that creates the grease pencil sequence from image sequence"""
    bl_idname = "sqgp.create_gp"
    bl_label = "Create grease pencil"


    @classmethod
    def poll (cls,context):
        scene = context.scene
        props = scene.add_properties
        start = props.start_frame
        gpo = props.gpo_target
        gpo_name = props.gp_name
        try:
            return gpo_name != ""
        except Exception:
            pass



    def execute (self,context):
        scene = context.scene
        props = scene.add_properties
        gp_list = []
        gpo = props.gpo_target
        start = props.start_frame
        gpo_name = props.gp_name
        area = bpy.context.area
        old_type = area.type
        wmp = context.window_manager
        prog=0;

        wmp.progress_begin(0,props.seq_length*2+17)


        bpy.ops.palette.extract_from_image()






        for i in range(start,props.seq_length):
            bpy.context.scene.frame_set(i)
            bpy.ops.gpencil.image_to_grease_pencil()
            gp_list.append(context.object)
            prog+=1
            wmp.progress_update(prog)


        area.type = 'VIEW_3D'
        bpy.ops.object.select_all(action='DESELECT')
        print(gp_list)
        

        for i in gp_list:
            i.select_set(True)



        
        bpy.ops.object.join()

        context.object.name = gpo_name
        gp = context.object.data
        gp.name = gpo_name


        lyr = gp.layers.new(props.newlyr_name,set_active=True)
        bpy.ops.gpencil.editmode_toggle()
        bpy.context.object.data.use_multiedit = True
        bpy.ops.gpencil.select_all(action='SELECT')
        bpy.ops.gpencil.move_to_layer(layer=gp.layers.active_index)
        prog+=3

        for i in gp.layers:
            if i != lyr:
                gp.layers.remove(i)
                prog+=1
                wmp.progress_update(prog)


        bpy.ops.gpencil.select_all(action='DESELECT')
        bpy.context.object.data.use_multiedit = False
        bpy.ops.gpencil.editmode_toggle(False)
        bpy.ops.gpencil.stroke_merge_material()
        bpy.ops.object.material_slot_remove_unused()
        area.type = old_type
        prog+=4
        wmp.progress_update(prog)
        wmp.progress_end()
        return {"FINISHED"}


class SEQ_PT_pan(Panel):
    bl_label = "Batch Image Sequence to GP"
    bl_idname = "SEQ_PT_pan"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Image"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.add_properties
        layout.label(text="Select a grease pencil object to add the sequence")
        layout.prop(props,"gp_name")
        layout.prop(props,"start_frame")
        layout.prop(props,"seq_length")
        layout.label(text="Remember to set ""Start Frame"" as ""Start"" number")
        layout.operator("sqgp.create_gp")




classes = (ImgSetting,createGP,SEQ_PT_pan)


def register():


    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.add_properties = PointerProperty(type=ImgSetting)




def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.add_properties


if __name__ == "__main__":
    register()
