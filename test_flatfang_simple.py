#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

from boxes import Boxes

def test_flatfang():
    b = Boxes()
    b.thickness = 3.0
    b.x = 80
    b.y = 60
    b.lidSettings.style = "flatfang"
    b.lid(b.x, b.y)
    b.close()

if __name__ == "__main__":
    test_flatfang()
