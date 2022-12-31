#!/usr/bin/env python3
# Copyright (C) 2018 Sebastian Reichel
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

from boxes.generators.rack19box import Rack19Box

class Rack10Box(Rack19Box):
    """Closed box with screw on top for mounting in a 10" rack."""

    def render(self):
        self._render(type=10)
