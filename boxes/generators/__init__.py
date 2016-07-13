
__all__ = [
    "box",
    "box2",
    "box3",
    "castle",
    "drillbox",
    "flexbox",
    "flexbox2",
    "flexbox3",
    "flexbox4",
    "flextest",
    "flextest2",
    "folder",
    "lamp",
    "magazinefile",
    "pulley",
    "silverwarebox",
    "trayinsert",
    "traylayout",
    "typetray",
]

def getAllBoxGenerators():
    import importlib
    return {name: importlib.import_module("boxes.generators." + name)
            for name in __all__}
