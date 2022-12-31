import importlib
import inspect
import pkgutil

import boxes

ui_groups_by_name = {}

class UIGroup:

    def __init__(self, name, title=None, description="", image=""):
        self.name = name
        self.title = title or name
        self.description = description
        self._image = image
        self.generators = []
        # register
        ui_groups_by_name[name] = self

    def add(self, box):
        self.generators.append(box)
        self.generators.sort(key=lambda b:getattr(b, '__name__', None) or b.__class__.__name__)

    @property
    def thumbnail(self):
        return self._image and f"{self._image}-thumb.jpg"

    @property
    def image(self):
        return self._image and f"{self._image}.jpg"

ui_groups = [
    UIGroup("Box", "Boxes", image="UniversalBox"),
    UIGroup("FlexBox", "Boxes with flex", image="RoundedBox"),
    UIGroup("Tray", "Trays and Drawer Inserts", image="TypeTray"),
    UIGroup("Shelf", "Shelves", image="DisplayShelf"),
    UIGroup("WallMounted", image="WallTypeTray"),
    UIGroup("Holes", "Hole patterns", image=""),
    UIGroup("Part", "Parts and Samples", image="BurnTest"),
    UIGroup("Misc", image="TrafficLight"),
    UIGroup("Unstable", description="Generators are still untested or need manual adjustment to be useful."),
    ]

def getAllBoxGenerators():
    generators = {}
    for importer, modname, ispkg in pkgutil.walk_packages(
            path=__path__,
            prefix=__name__+'.'):
        module = importlib.import_module(modname)
        if module.__name__.split('.')[-1].startswith("_"):
            continue
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

