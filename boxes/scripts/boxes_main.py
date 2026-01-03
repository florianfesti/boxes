#!/usr/bin/env python3
"""

Generate stencils for wooden boxes.

"""
from __future__ import annotations

import gettext
import os
import sys
import copy
import argparse
import logging
import hashlib
from pathlib import Path
from typing import TextIO
try:
    import boxes
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
    import boxes

import boxes.generators
import boxes.svgmerge

import yaml


class ArgumentParserError(Exception): pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

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

def multi_generate(config_path : Path|str|TextIO, output_path : Path|str, output_name_formater=None, format="svg") -> list[str]:
    if isinstance(config_path, str) or isinstance(config_path, Path):
        with open(config_path) as ff:
            config_data = yaml.safe_load(ff)
    else:
        config_data = yaml.safe_load(config_path)

    all_generators = boxes.generators.getAllBoxGenerators()
    generators_by_name = {b.__name__: b for b in all_generators.values()}

    generated_files = []
    defaults = config_data.get("Defaults", {})

    for ii, box_settings in enumerate(config_data.get("Boxes", [])):
        # Allow for skipping generation
        if box_settings.get("generate") == False:
            continue

        # Get the box generator
        box_type = box_settings.pop("box_type", None)
        if box_type is None:
            raise ValueError("box_type must be provided for each cut")

        # __ALL__ is a special case
        box_classes: tuple|None = None
        if box_type != "__ALL__":
            box_classes = ( generators_by_name.get(box_type, None), )
            if box_classes is None:
                raise ValueError("invalid generator '%s'" % box_type)
        else:
            skipGenerators = set(box_settings.get("skipGenerators", []))
            brokenGenerators = set(box_settings.get("brokenGenerators", []))
            avoidGenerators = skipGenerators | brokenGenerators
            box_classes = tuple(filter(lambda x: x.__name__ not in avoidGenerators, all_generators.values()))

        for box_cls in box_classes:
            box_cls_name = box_cls.__name__

            # Instantitate the box object
            box = box_cls()
            box.translations = get_translation()

            # Create the settings for the generator
            settings = copy.deepcopy(defaults)
            settings.update(box_settings.get("args", {}))

            # Handle layout separately
            if hasattr(box, "layout") and "layout" in settings:
                if os.path.exists(settings["layout"]):
                    with open(settings["layout"]) as ff:
                        settings["layout"] = ff.read()
                else:
                    box.layout = settings["layout"]

            # Turn the settings into arguments, but ignore format
            # in the YAML file if provided and use the argument to the function
            box_args = []
            for kk, vv in settings.items():
                # Handle format separately
                if kk in ("format","layout"):
                    continue
                box_args.append(f"--{kk}={vv}")

            # Layout has three options:
            #  - provided verbatim in the YAML file
            #  - provided as a path to a file in the YAML file
            #  - using the special placeholder __GENERATE__ which will invoke the default
            if "layout" in settings:
                if os.path.exists(settings["layout"]):
                    with open(settings["layout"]) as ff:
                        layout = ff.read()
                else:
                    layout = settings["layout"]
                box_args.append(f"--layout={layout}")

            # SVG is default, only apply argument if changing default
            if format != "svg":
                box_args.append(f"--format={format}")

            # Parse the box arguments - because we allow arguments at the
            # top-level defaults, we ignore unknown arguments
            try:
                # Ignore unknown arguments by pre-parsing. This two stage
                # approach was performed to avoid modifying parseArgs and
                # changing it's behavior.  A long-term better solution
                # might be to allow parseArgs to take a 'strict' argument
                # the can enable/disable strict parsing of arguments
                args, argv = box.argparser.parse_known_args(box_args)
                if len(argv) > 0:
                    for unknown_arg in argv:
                        box_args.remove(unknown_arg)
                box.parseArgs(box_args)
            except ArgumentParserError:
                print("Error parsing box args for box %s : %s", ii, box_cls_name)
                continue

            # handle __GENERATE__ which must be called after parseArgs
            if getattr(box, "layout", None) == "__GENERATE__":
                if hasattr(box, "generate_layout") and callable(box.generate_layout):
                    box.layout = box.generate_layout()
                else:
                    print("Error box %s : %s requires manual layout", ii, box_cls_name)
                    continue

            box.metadata["reproducible"] = True

            # Render the box SVG
            box.open()
            box.render()
            data = box.close()

            if callable(output_name_formater):
                output_fname = output_name_formater(
                    box_type=box_cls_name,
                    name=box_settings.get("name", box_cls_name),
                    box_idx=ii,
                    metadata=box.metadata,
                    box_args=box_args
                )
            else:
                output_fname = output_name_formater.format(
                    box_type=box_cls_name,
                    name=box_settings.get("name", box_cls_name),
                    box_idx=ii,
                    metadata=box.metadata,
                )

            # Write the output - if count is provided generate multiple copies
            if box_settings.get("count") is not None:
                for jj in range(int(box_settings.get("count"))):
                    output_file = os.path.join(output_path, f"{output_fname}_{jj}.{format}")
                    print(f"Writing {output_file}")
                    with open(output_file, "wb") as ff:
                        ff.write(data.read())
                        data.seek(0)
                    generated_files.append(output_file)

            else:
                output_file = os.path.join(output_path, f"{output_fname}.{format}")
                print(f"Writing {output_file}")
                with open(output_file, "wb") as ff:
                    ff.write(data.read())
                generated_files.append(output_file)

    return generated_files

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
    parser.add_argument("--debug", type=boxes.boolarg, default=False)
    parser.add_argument("--version", action="store_true", default=False)
    parser.add_argument("--list", action="store_true", default=False, help="List available generators.")
    parser.add_argument("--examples", action="store_true", default=False, help='Generates an SVG for every generator into the "examples" folder.')
    parser.add_argument("--help", action="store_true", default=False)
    parser.add_argument("--multi-generator", type=argparse.FileType('r', encoding='UTF-8'), help="Generate multiple boxes from a configuration YAML")
    parser.add_argument("--merge", action="store_true", default=False, help="Merge multiple SVG files into optimal cuts for a given panel size")
    args, extra = parser.parse_known_args()
    if args.generator and (args.examples or args.multi_generator or args.list):
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
        print("Generating SVG examples for every possible generator.")
        config_path = Path(__file__).parent.parent.parent / 'examples.yml'
        output_path = Path("examples")
        multi_generate(config_path, output_path, example_output_fname_formatter)
    elif args.multi_generator:
        try:
            if os.path.isdir(extra[0]):
                # if the output path is a folder assume the default name format
                # and write all files to the sub-folder
                output_path = Path(extra[0])
                output_fname_format = "{name}_{box_idx}"
            elif "{" not in extra[0] and "}" not in extra[0]:
                # if substitution brackets aren't found, assume that isn't
                # the desired behavior since it would cause every file to overwrite previous files
                # so use this as a prefix with box index
                output_path = Path(os.path.dirname(extra[0]))
                output_fname_format = extra[0] + "_{box_idx}"
            else:
                # The user has provided a full path template, so use it as-is
                output_path =Path(os.path.dirname(extra[0]))
                output_fname_format = os.path.basename(extra[0])
        except IndexError:
            # No template has been provided, use defaults
            output_path = Path(".")
            output_fname_format = "{name}_{box_idx}"
        multi_generate(args.multi_generator, output_path, output_fname_format)
    elif args.merge:
        merger = boxes.svgmerge.SvgMerge()
        merger.parseArgs(extra)
        merger.render(extra)
        data = merger.close()
        with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) if merger.output == "-" else open(merger.output, 'wb') as f:
            f.write(data.getvalue())
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
            extra.extend(["--debug", "1"])
        run_generator(name, extra)

if __name__ == '__main__':
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)

    main()
