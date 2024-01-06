from bpy.types import Panel, Operator, WindowManager
import bpy
import sys
import os
import webbrowser
import bpy.utils.previews

parentFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

try:
    import boxes
except ImportError:
    sys.path.append(parentFolder)
    import boxes
 
import boxes.generators

def boxes_pictures_items(self, context):
    # Icons Directory
    directory = os.path.join(parentFolder, "static/samples")

    pcoll = preview_collections["main"]

    if directory and os.path.exists(directory):
    # Scan the directory for png files
        image_paths = []   

        for fn in os.listdir(directory):
            if fn.lower().endswith("-thumb.jpg"):
                image_paths.append(fn)

        boxes = []

        selectedGroup = context.scene.category
        categ = context.scene.categ


        if selectedGroup == "All":
            for box in categ.values():
                for box2 in box:
                    boxes.append(box2)
        else :
            for box in categ[selectedGroup]:
                boxes.append(box)


        boxes_items = []

        for box in boxes:
                filename = f"{box}-thumb.jpg"
                if filename in image_paths:
                    filepath = os.path.join(directory, filename)

                    if filepath in pcoll:
                        boxes_items.append((box, box, "", pcoll[filepath].icon_id, len(boxes_items)))
                    else:
                        thumb = pcoll.load(filepath, filepath, "IMAGE")
                        boxes_items.append((box, box, "", thumb.icon_id, len(boxes_items))) 

    if context is None:
        return boxes_items

    boxes_items.sort()  # Alphabetically
    pcoll.my_previews = boxes_items
    pcoll.my_previews_dir = directory
    return pcoll.my_previews


class Object_OT_AddButton(Operator):
    bl_idname = "add.object"
    bl_label = "Add Object"

    def execute(self, context):
        scene = context.scene
        selectedBox = context.window_manager.my_previews.replace("-thumb.jpg", "")
        args = context.scene.args

        allGen = {
            name.split(".")[-1].lower(): generator
            for name, generator in boxes.generators.getAllBoxGenerators().items()
        }

        box = allGen[selectedBox.lower()]()

        directory = os.path.join(parentFolder, "blenderboxes/boxe.svg")

        args.append("--output=" + directory)
        box.parseArgs(args)
        box.open()
        box.render()
        box.close()


        previouscollection = bpy.data.collections.get(selectedBox)

        if scene.replace and previouscollection is not None :
            bpy.data.collections.remove(previouscollection)


        bpy.ops.import_curve.svg(filepath=directory)
        collection = bpy.data.collections.get("boxe.svg")
        collection.name = selectedBox

        return {"FINISHED"}
    
class Object_OT_OnlineButton(Operator):
    bl_idname = "online.documentation"
    bl_label = "Online Box"

    def execute(self, context):
        selectedBox = context.window_manager.my_previews.replace("-thumb.jpg", "")

        webbrowser.open(f'https://www.festi.info/boxes.py/{selectedBox}?language=en')
        
        return {"FINISHED"}


class Diffuseur_SideBar(Panel):
    """Diffuseur options panel"""

    bl_label = "Boxes"
    bl_idname = "BOXES_PT_Boxes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Boxes"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        generators = scene.generators

        wm = context.window_manager

        selectedBox = context.window_manager.my_previews.replace("-thumb.jpg", "")

        row = layout.row(align=True)
        row.alignment = "CENTER"
        row.label(text=selectedBox)

        row = layout.column()
        row.prop(scene, "category")
        row.template_icon_view(wm, "my_previews", show_labels=True)

        col = layout.column(align=True)
        col.operator("add.object", icon="RESTRICT_RENDER_OFF", text=("Add"))
        col.separator()
        col.operator("online.documentation", icon="URL", text=("Online"))
        col.separator()
        col.prop(scene, "replace")
        args = []

        boxe = getattr(generators, selectedBox)
        box_attributes_names = tuple(
            p
            for p in boxe.bl_rna.properties.keys()
            if p not in {"rna_type", "name", "positionalarguments"}
        )

        for (
            attributeName
        ) in box_attributes_names:  # ABox Settings / Default Settings / ...
            box_group_attributes = getattr(boxe, attributeName)

            box = layout.box()
            box.label(text=box_group_attributes.name)

            group_params_name = tuple(
                p
                for p in box_group_attributes.bl_rna.properties.keys()
                if p not in {"rna_type", "name"}
            )

            for paramName in group_params_name:  # x / y / outside ...
                box.prop(box_group_attributes, paramName)
                value = getattr(box_group_attributes, paramName)
                args.append("--" + paramName + "=" + str(value))

        bpy.types.Scene.args = args


ui_classes = [Diffuseur_SideBar, Object_OT_AddButton, Object_OT_OnlineButton]

preview_collections = {}


def register():
    for cls in ui_classes:
        bpy.utils.register_class(cls)

    WindowManager.my_previews_dir = bpy.props.StringProperty(
        name="Folder Path", subtype="DIR_PATH", default=""
    )

    WindowManager.my_previews = bpy.props.EnumProperty(
        items=boxes_pictures_items,
    )

    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()

    preview_collections["main"] = pcoll


def unregister():
    for cls in ui_classes:
        bpy.utils.unregister_class(cls)

    del WindowManager.my_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    preview_collections.clear()
