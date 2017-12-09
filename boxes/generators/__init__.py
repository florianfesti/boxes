import pkgutil
import inspect
import importlib
import boxes

ui_groups_by_name = {}

class UIGroup:

    def __init__(self, name, title=None, description=""):
        self.name = name
        self.title = title or name
        self.description = description
        self.generators = []
        # register
        ui_groups_by_name[name] = self

    def add(self, box):
        self.generators.append(box)
        self.generators.sort(key=lambda b:getattr(b, '__name__', None) or b.__class__.__name__)

ui_groups = [
    UIGroup("Box", "Boxes"),
    UIGroup("FlexBox", "Boxes with flex"),
    UIGroup("Tray", "Trays and Drawer Inserts"),
    UIGroup("Shelf", "Shelves"),
    UIGroup("Part", "Parts and Samples"),
    UIGroup("Misc"),
    UIGroup("Unstable", description="Generators are still untested or need manual adjustment to be useful."),
    ]

def getAllBoxGenerators():
    generators = {}
    for importer, modname, ispkg in pkgutil.walk_packages(
            path=__path__,
            prefix=__name__+'.',
            onerror=lambda x: print(x)):
        module = importlib.import_module(modname)
        for k, v in module.__dict__.items():
            if v is boxes.Boxes:
                continue
            if (inspect.isclass(v) and issubclass(v, boxes.Boxes) and
                v.__name__[0] != '_'):
                generators[modname + '.' + v.__name__] = v
    return generators

def getAllGeneratorModules():
    generators = {}
    for importer, modname, ispkg in pkgutil.walk_packages(
            path=__path__,
            prefix=__name__+'.',
            onerror=lambda x: None):
        module = importlib.import_module(modname)
        generators[modname.split('.')[-1]] = module
    return generators

