import bpy
import boxes  # in blender scripts/startup
import boxes.generators

import argparse

class Generators(bpy.types.PropertyGroup):
    pass


bpy.utils.register_class(Generators)

allGen = {
    name.split(".")[-1].lower(): generator
    for name, generator in boxes.generators.getAllBoxGenerators().items()
}

listboxes = list(allGen.values())

for box in listboxes:

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
                                bpy.props.FloatProperty(default=float(default)),
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





