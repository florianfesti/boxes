import bpy
import sys
import os

parentFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

try:
    import boxes
except ImportError:
    sys.path.append(parentFolder)
    try:
        import boxes
        import boxes.generators
    except ImportError:
        print("ERROR IMPORTING BOXES")
        print(parentFolder)

import argparse

class Generators(bpy.types.PropertyGroup):
    pass


bpy.utils.register_class(Generators)

allGen = {
    name.split(".")[-1].lower(): generator
    for name, generator in boxes.generators.getAllBoxGenerators().items()
}

listboxes = list(allGen.values())

ui_groups = [("All", "All", "")]

for box in listboxes:
    if (box.ui_group, box.ui_group, "") not in ui_groups:
        ui_groups.append((box.ui_group,box.ui_group, ""))

    class MyBox(bpy.types.PropertyGroup):
        pass

    bpy.utils.register_class(MyBox)

    setattr(MyBox, "box", box)

    for group in box().argparser._action_groups:

        class MyGroup(bpy.types.PropertyGroup):
            pass

        bpy.utils.register_class(MyGroup)

        setattr(MyGroup, "name", bpy.props.StringProperty(default=group.title))
        for param in group._group_actions:
            dest = param.dest
            type = param.type
            help = str(param.help) or "No Description"
            default = param.default
            if not (
                isinstance(param, argparse._HelpAction)
                and isinstance(param, argparse._StoreAction)
            ):
                match dest:
                    case "input" | "output" | "format" | "layout":
                        pass
                    case _:
                        if type is float:
                            setattr(
                                MyGroup,
                                dest,
                                bpy.props.FloatProperty(default=float(default), description=help),
                            )
                        if type is int:
                            setattr(
                                MyGroup, dest, bpy.props.IntProperty(default=default)
                            )
                        if type is str:
                            if param.choices:
                                list_of_choices = []
                                default_index = 0
                                for index, choice in enumerate(param.choices):
                                    list_of_choices.append((choice, choice, ""))
                                    if choice == default:
                                        default_index = index
                                setattr(
                                    MyGroup,
                                    dest,
                                    bpy.props.EnumProperty(
                                        items=list_of_choices, default=default_index
                                    ),
                                )
                            else:
                                setattr(
                                    MyGroup,
                                    dest,
                                    bpy.props.StringProperty(default=default),
                                )

                        if isinstance(type, boxes.BoolArg):
                            setattr(
                                MyGroup,
                                dest,
                                bpy.props.BoolProperty(default=bool(default)),
                            )
        setattr(
            MyBox,
            group.title.replace(" ", "").lower(),
            bpy.props.PointerProperty(type=MyGroup),
        )
    setattr(Generators, box.__name__, bpy.props.PointerProperty(type=MyBox))
setattr(bpy.types.Scene, "generators", bpy.props.PointerProperty(type=Generators))
setattr(bpy.types.Scene, "replace", bpy.props.BoolProperty(name="Replace same previous box"))
setattr(bpy.types.Scene, "category", bpy.props.EnumProperty(items=ui_groups, name=""))




