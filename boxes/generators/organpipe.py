# Copyright (C) 2013-2018 Florian Festi
#
# Based on pipecalc by Christian F. Coors
# https://github.com/ccoors/pipecalc
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

from math import *

from boxes import *

pitches = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#' ,'b']

pressure_units = { 'Pa' : 1.0,
                   'mBar' : 100.,
                   'mmHg' : 133.322,
                   'mmH2O' : 9.80665,
}

class OrganPipe(Boxes): # Change class name!
    """Rectangular organ pipe based on pipecalc"""

    ui_group = "Unstable" # see ./__init__.py for names

    def getFrequency(self, pitch, octave, base_freq=440):
        steps = pitches.index(pitch) + (octave-4)*12 - 9
        return base_freq * 2**(steps/12.)

    def getRadius(self, pitch, octave, intonation):
        steps = pitches.index(pitch) + (octave-2)*12 + intonation
        return 0.5 * 0.15555 * 0.957458**steps
    
    def getAirSpeed(self, wind_pressure, air_density=1.2):
        return (2.0 * (wind_pressure / air_density))**.5

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=3.0, space=3.0,
                             surroundingspaces=1.0)
        
        """
    air_temperature: f64,
"""
        # Add non default cli params if needed (see argparse std lib)
        self.argparser.add_argument(
            "--pitch",  action="store", type=str, default="c",
            choices=pitches,
            help="pitch")
        self.argparser.add_argument(
            "--octave",  action="store", type=int, default=2,
            help="Octave in International Pitch Notation (2 == C)")
        self.argparser.add_argument(
            "--intonation",  action="store", type=float, default=2.0,
            help="Intonation Number. 2 for max. efficiency, 3 max.")
        self.argparser.add_argument(
            "--mouthratio",  action="store", type=float, default=0.25,
            help="mouth to circumference ratio (0.1 to 0.45). Determines the width to depth ratio")
        self.argparser.add_argument(
            "--cutup",  action="store", type=float, default=0.3,
            help="Cutup to mouth ratio")
        self.argparser.add_argument(
            "--mensur",  action="store", type=int, default=0,
            help="Distance in halftones in the Normalmensur by Töpfer")
        self.argparser.add_argument(
            "--windpressure",  action="store", type=float, default=588.4,
            help="uses unit selected below")
        self.argparser.add_argument(
            "--windpressure_units",  action="store", type=str, default='Pa',
            choices=pressure_units.keys(),
            help="in Pa")
        self.argparser.add_argument(
            "--stopped",  action="store", type=boolarg, default=False,
            help="pipe is closed at the top")


    def render(self):
        t = self.thickness
        f = self.getFrequency(self.pitch, self.octave, 440)

        self.windpressure *= pressure_units.get(self.windpressure_units, 1.0)
        
        speed_of_sound = 343.6 # XXX util::speed_of_sound(self.air_temperature); // in m/s
        air_density = 1.2
        air_speed = self.getAirSpeed(self.windpressure, air_density)

        i = self.intonation
        radius = self.getRadius(self.pitch, self.octave, i) * 1000
        cross_section = pi * radius**2
        circumference = pi * radius * 2.0
        mouth_width = circumference * self.mouthratio
        mouth_height = mouth_width * self.cutup
        mouth_area = mouth_height * mouth_width
        pipe_depth = cross_section / mouth_width
        base_length = max(mouth_width, pipe_depth)

        jet_thickness = (f**2 * i**2 * (.01 * mouth_height)**3) / air_speed**2
        sound_power = (0.001 * pi * (air_density / speed_of_sound) * f**2
                       * (1.7 * (jet_thickness * speed_of_sound * f * mouth_area * mouth_area**.5)**.5)**2)

        air_consumption_rate = air_speed * mouth_width * jet_thickness * 1E6

        wavelength = speed_of_sound / f * 1000

        if self.stopped:
            theoretical_resonator_length = wavelength / 4.0
            resonator_length = (-0.73 * (f * cross_section *1E-6 - 0.342466 * speed_of_sound * mouth_area**.5 * 1E-3)
            / (f * mouth_area**.5 * 1E-3))
        else:
            theoretical_resonator_length = wavelength / 2.0
            resonator_length = (-0.73 * (f * cross_section * 1E-6 + 0.465753 * f * mouth_area**.5 * cross_section**.5 * 1E-6 - 0.684932 * speed_of_sound * mouth_area**.5 * 1E-3)
                / (f * mouth_area**.5 * 1E-3)) * 1E3
        air_hole_diameter = 2.0 * ((mouth_width * jet_thickness * 10.0)**.5 / pi)

        total_length = resonator_length + base_length
        

        e = ["f", "e",
             edges.CompoundEdge(self, "fef", (resonator_length - mouth_height - 10*t, mouth_height + 10*t, base_length)), "f"]
        
        self.rectangularWall(total_length, pipe_depth, e, callback=[
            lambda: self.fingerHolesAt(base_length-0.5*t, 0, pipe_depth-jet_thickness)],
                             move="up")
        self.rectangularWall(total_length, pipe_depth, e, callback=[
            lambda: self.fingerHolesAt(base_length-0.5*t, 0, pipe_depth-jet_thickness)],
                             move="up")
        self.rectangularWall(total_length, mouth_width, "FeFF", callback=[
            lambda: self.fingerHolesAt(base_length-0.5*t, 0, mouth_width)],
                             move="up")
        e = [edges.CompoundEdge(self, "EF", (t*10, resonator_length - mouth_height - t*10)), 'e',
             edges.CompoundEdge(self, "FE", (resonator_length - mouth_height - t*10, t*10)), 'e']
        self.rectangularWall(resonator_length - mouth_height, mouth_width, e, move="up")
        self.rectangularWall(base_length, mouth_width, "FeFF", move="right")
        self.rectangularWall(mouth_width, pipe_depth, "fFfF", callback=[
            lambda:self.hole(mouth_width/2, pipe_depth/2, d=air_hole_diameter)], move="right")
        self.rectangularWall(mouth_width, pipe_depth - jet_thickness, "ffef", move="right")

