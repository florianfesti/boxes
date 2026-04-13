from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
from types import ModuleType
from typing import Any

import boxes

_Boxes = boxes.Boxes  # cache before subpackage imports overwrite the 'boxes' name

ui_groups_by_name = {}


class UIGroup:

    def __init__(self, name: str, title: str | None = None, description: str = "", image: str = "") -> None:
        self.name = name
        self.title = title or name
        self.description = description
        self._image = image
        self.generators: list[Any] = []
        # register
        ui_groups_by_name[name] = self

    def add(self, box) -> None:
        self.generators.append(box)
        self.generators.sort(key=lambda b: getattr(b, '__name__', None) or b.__class__.__name__)

    @property
    def thumbnail(self) -> str:
        return self._image and f"{self._image}-thumb.jpg"

    @property
    def image(self) -> str:
        return self._image and f"{self._image}.jpg"


ui_groups: list[UIGroup] = [
    UIGroup("Box", title="Boxes", image="UniversalBox"),
    UIGroup("FlexBox", title="Boxes with flex", image="RoundedBox"),
    UIGroup("Tray", title="Trays and Drawer Inserts", image="TypeTray"),
    UIGroup("Shelf", title="Shelves", image="DisplayShelf"),
    UIGroup("WallMounted", title="WallMounted", image="WallTypeTray"),
    UIGroup("Holes", title="Hole patterns", image=""),
    UIGroup("Part", title="Parts and Samples", image="BurnTest"),
    UIGroup("Electronic", title="Electronic"),
    UIGroup("Toy", title="Toy"),
    UIGroup("Game", title="Game",
            description="Laser-cut accessories for board games and tabletop gaming."),
    UIGroup("Display", title="Display",
            description="Decorative flat pieces, labels and signs."),
    UIGroup("Misc", title="Misc", description="Parts that don't fit into the other categories."),
]


def getAllBoxGenerators() -> dict[str, type[boxes.Boxes]]:
    generators = {}
    path = __path__
    if "BOXES_GENERATOR_PATH" in os.environ:
        path.extend(os.environ.get("BOXES_GENERATOR_PATH", "").split(":"))
    for importer, modname, ispkg in pkgutil.walk_packages(path=path, prefix=__name__ + '.'):
        module = importlib.import_module(modname)
        if module.__name__.split('.')[-1].startswith("_"):
            continue
        for k, v in module.__dict__.items():
            if v is _Boxes:
                continue
            if inspect.isclass(v) and issubclass(v, _Boxes) and v.__name__[0] != '_':
                generators[modname + '.' + v.__name__] = v
    return generators


def getAllGeneratorModules() -> dict[str, ModuleType]:
    generators = {}
    path = __path__
    if "BOXES_GENERATOR_PATH" in os.environ:
        path.extend(os.environ.get("BOXES_GENERATOR_PATH", "").split(":"))
    for importer, modname, ispkg in pkgutil.walk_packages(
            path=path,
            prefix=__name__ + '.',
            onerror=lambda x: None):
        module = importlib.import_module(modname)
        generators[modname.split('.')[-1]] = module
    return generators
