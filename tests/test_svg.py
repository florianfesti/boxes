from __future__ import annotations

import sys
from pathlib import Path

import pytest
from lxml import etree

try:
    import boxes
except ImportError:
    sys.path.append(Path(__file__).resolve().parent.parent.__str__())
    import boxes

import boxes.generators


class TestSVG:
    """Test SVG creation of box generators.
    Just test generators which have a default output without an input requirement.
    Uses files from examples folder as reference.
    """
    all_generators = boxes.generators.getAllBoxGenerators().values()

    # Ignore multistep generators and generators which require input.
    notTestGenerators = ('GridfinityTrayLayout', 'TrayLayout', 'TrayLayoutFile', 'TypeTray', 'Edges',)
    brokenGenerators = (
        'Console', # Generated svg is different on windows and linux.
    )
    avoidGenerator = notTestGenerators + brokenGenerators

    def test_generators_available(self) -> None:
        assert len(self.all_generators) != 0

    # svgcheck currently do not allow inkscape custom tags.
    # @staticmethod
    # def is_valid_svg(file_path: str) -> bool:
    #     result = subprocess.run(['svgcheck', file_path], capture_output=True, text=True)
    #     return "INFO: File conforms to SVG requirements." in result.stdout

    @staticmethod
    def is_valid_xml_by_lxml(xml_string: str) -> bool:
        try:
            etree.fromstring(xml_string)
            return True
        except etree.XMLSyntaxError:
            return False

    @staticmethod
    def idfunc(val) -> str:
        return f"{val.__name__}"

    @pytest.mark.parametrize(
        "generator",
        all_generators,
        ids=idfunc.__func__,
    )
    def test_generator(self, generator: type[boxes.Boxes], capsys) -> None:
        boxName = generator.__name__
        if boxName in self.avoidGenerator:
            pytest.skip("Skipped generator")
        box = generator()
        box.parseArgs("")
        box.metadata["reproducible"] = True
        box.open()
        box.render()
        boxData = box.close()

        out, err = capsys.readouterr()

        assert 100 < boxData.__sizeof__(), "No data generated."
        assert 0 == len(out), "Console output generated."
        assert 0 == len(err), "Console error generated."

        # Use external library lxml as cross-check.
        assert self.is_valid_xml_by_lxml(boxData.getvalue()) is True, "Invalid XML according to library lxml."

        file = Path(__file__).resolve().parent / 'data' / (boxName + '.svg')
        file.write_bytes(boxData.getvalue())

        # Use example data from repository as reference data.
        referenceData = Path(__file__).resolve().parent.parent / 'examples' / (boxName + '.svg')
        assert referenceData.exists() is True, "Reference file for comparison does not exist."
        assert referenceData.is_file() is True, "Reference file for comparison does not exist."
        assert referenceData.read_bytes() == boxData.getvalue(), "SVG files are not equal. If change is intended, please update example files."
