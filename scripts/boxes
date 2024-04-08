#!/usr/bin/env python3
"""boxes.py

Generate stencils for wooden boxes.

Usage:
  boxes <generator> [<args>...]
  boxes --list
  boxes --examples
  boxes (-h | --help)

Options:
  --list        List available generators.
  --examples    Generates an SVG for every generator into the "examples" folder.
  -h --help     Show this screen.
"""
from __future__ import annotations

import gettext
import os
import sys
from pathlib import Path

try:
    import boxes
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
    import boxes

import boxes.generators


def print_grouped_generators() -> None:
    class ConsoleColors:
        BOLD = '\033[1m'
        CLEAR = '\033[0m'
        ITALIC = '\033[3m'
        UNDERLINE = '\033[4m'

    print('Available generators:')
    for group in generator_groups():
        print('\n' + ConsoleColors.UNDERLINE + group.title + ConsoleColors.CLEAR)
        if group.description:
            print('\n' + group.description)
        print()
        for box in group.generators:
            description = box.__doc__ or ""
            description = description.replace("\n", "").replace("\r", "").strip()
            print(f' *  {box.__name__:<15} - {ConsoleColors.ITALIC}{description}{ConsoleColors.CLEAR}')


def create_example_every_generator() -> None:
    print("Generating SVG examples for every possible generator.")
    for group in generator_groups():
        for boxExample in group.generators:
            boxName = boxExample.__name__
            notTestGenerator = ('GridfinityTrayLayout', 'TrayLayout', 'TrayLayoutFile', 'TypeTray', 'Edges',)
            brokenGenerator = ()
            avoidGenerator = notTestGenerator + brokenGenerator
            if boxName in avoidGenerator:
                print(f"SKIP: {boxName}")
                continue
            print(f"Generate example for: {boxName}")

            box = boxExample()
            box.translations = get_translation()
            box.parseArgs("")
            box.metadata["reproducible"] = True
            box.open()
            box.render()
            boxData = box.close()

            file = Path('examples') / (boxName + '.svg')
            file.write_bytes(boxData.getvalue())


def get_translation():
    try:
        return gettext.translation('boxes.py', localedir='locale')
    except OSError:
        return gettext.translation('boxes.py', fallback=True)


def run_generator(name: str, args) -> None:
    generators = generators_by_name()
    lower_name = name.lower()

    if lower_name in generators.keys():
        box = generators[lower_name]()
        box.translations = get_translation()
        box.parseArgs(args)
        box.open()
        box.render()
        data = box.close()
        with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) if box.output == "-" else open(box.output, 'wb') as f:
            f.write(data.getvalue())
    else:
        msg = f"Unknown generator '{name}'. Use boxes --list to get a list of available commands.\n"
        sys.stderr.write(msg)


def generator_groups():
    generators = generators_by_name()
    return group_generators(generators)


def group_generators(generators):
    groups = boxes.generators.ui_groups
    groups_by_name = boxes.generators.ui_groups_by_name

    for name, generator in generators.items():
        group_for_generator = groups_by_name.get(generator.ui_group, groups_by_name['Misc'])
        group_for_generator.add(generator)

    return groups


def generators_by_name() -> dict[str, type[boxes.Boxes]]:
    all_generators = boxes.generators.getAllBoxGenerators()

    return {
        name.split('.')[-1].lower(): generator
        for name, generator in all_generators.items()
    }


def print_usage() -> None:
    print(__doc__)


def print_version() -> None:
    print("boxes does not use versioning.")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1].startswith("--id="):
        del sys.argv[1]
    if len(sys.argv) == 1 or sys.argv[1] == '--help' or sys.argv[1] == '-h':
        print_usage()
    elif sys.argv[1] == '--version':
        print_version()
    elif sys.argv[1] == '--list':
        print_grouped_generators()
    elif sys.argv[1] == '--examples':
        create_example_every_generator()
    else:
        name = sys.argv[1].lower()
        if name.startswith("--generator="):
            name = name[12:]
        run_generator(name, sys.argv[2:])


if __name__ == '__main__':
    main()
