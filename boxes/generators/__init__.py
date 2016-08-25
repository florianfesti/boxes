import pkgutil
import inspect
import importlib
import boxes

def getAllBoxGenerators():
    generators = {}
    for importer, modname, ispkg in pkgutil.walk_packages(
            path=__path__,
            prefix=__name__+'.',
            onerror=lambda x: None):
        module = importlib.import_module(modname)
        for k, v in module.__dict__.items():
            if v is boxes.Boxes:
                continue
            if inspect.isclass(v) and issubclass(v, boxes.Boxes):
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

