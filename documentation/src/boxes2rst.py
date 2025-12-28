#!/usr/bin/env python3
# Copyright (C) 2017 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from pathlib import Path

try:
    import boxes.generators
except ImportError:
    sys.path.append(Path(__file__).resolve().parent.parent.__str__())
    import boxes.generators


class Boxes2rst:
    def __init__(self) -> None:
        self.boxes = {b.__name__: b() for b in boxes.generators.getAllBoxGenerators().values() if b.webinterface}
        self.groups = boxes.generators.ui_groups
        self.groups_by_name = boxes.generators.ui_groups_by_name

        for name, box in self.boxes.items():
            self.groups_by_name.get(box.ui_group, self.groups_by_name["Misc"]).add(box)

    def write(self, targetFile: str) -> None:
        pathToImages: Path = Path(__file__).resolve().parent.parent / "static" / "samples"
        with Path(targetFile).open("w") as f:
            for name, group in self.groups_by_name.items():
                f.write(f"{name}\n----------------\n\n")
                for box in group.generators:
                    f.write(box.__class__.__name__)
                    f.write("\n..........................................\n\n")
                    f.write(f"\n\n.. autoclass:: {box.__class__.__module__}.{box.__class__.__name__}")
                    f.write("\n\n")
                    if (pathToImages / f"{box.__class__.__name__}.jpg").exists():
                        f.write(f".. image:: ../../static/samples/{box.__class__.__name__}.jpg\n\n")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: boxes2rst.py TARGETFILE")
        return
    b = Boxes2rst()
    b.write(sys.argv[1])


if __name__ == "__main__":
    main()
