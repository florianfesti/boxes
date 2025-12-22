#!/usr/bin/env python3
"""

Generate stencils for wooden boxes.

"""
from __future__ import annotations

import gettext
import os
import sys
import argparse
from pathlib import Path

try:
    import boxes
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
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


def print_version() -> None:
    print("boxes does not use versioning.")


def example_output_fname_formatter(box_type, name, box_idx, metadata, box_args):
    if not box_args:
        return f"{name}"
    else:
        args_hash = hashlib.sha1(" ".join(sorted(box_args)).encode("utf-8")).hexdigest()
        return f"{name}_{args_hash[0:8]}"


def main() -> None:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__, add_help=False)
    parser.allow_abbrev = False
    parser.add_argument("--generator", type=str, default=None)
    parser.add_argument("--id", type=str, default=None, help="ignored")
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--version", action="store_true", default=False)
    parser.add_argument("--list", action="store_true", default=False, help="List available generators.")
    parser.add_argument("--examples", action="store_true", default=False, help='Generates an SVG for every generator into the "examples" folder.')
    parser.add_argument("--help", action="store_true", default=False)
    args, extra = parser.parse_known_args()
    if args.generator and (args.examples or args.list):
        parser.error("cannot combine --generator with other commands")

    # if debug is True set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle various actions
    if args.version:
        print_version()
    elif args.list:
        print_grouped_generators()
    elif args.examples:
        create_example_every_generator()
    else:
        if args.generator:
            name = args.generator
        elif extra:
            name = extra.pop(0).lower()
        else:
            parser.print_help()
            sys.exit(0)
        if args.help:
            extra.append("--help")
        if args.debug:
            extra.append("--debug")
        run_generator(name, extra)

if __name__ == '__main__':
    # Setup basic logging
    import logging
    logging.basicConfig(level=logging.INFO)

    main()
