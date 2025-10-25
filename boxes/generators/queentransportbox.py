# Copyright (C) 2013-2014 Florian Festi
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

from boxes import *
from boxes.lids import Lid, LidSettings, _TopEdge
import math
from typing import Callable


class Cutout:
    """Base class for cutouts"""
    DIMENSIONS = (0.0, 0.0)

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        pass


class CircleCutout(Cutout):
    RADIUS = 12.0 / 2.0
    DIMENSIONS = (RADIUS * 2.0, RADIUS * 2.0)

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        """
        Fügt den runden Käfig-Ausschnitt in die Platte ein.
        cx, cy = Mittelpunkt der Aussparung
        """
        with box.saved_context():
            box.set_source_color(color)
            box.circle(x, y, self.RADIUS)


class PolygonCutout(Cutout):
    PTS = ( (0.0, 0.0), )

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        """
        Fügt den Käfig-Ausschnitt (aus SVG umgewandelt) in die Platte ein.
        cx, cy = Mittelpunkt der Aussparung
        """
        with box.saved_context() as ctx:
            box.set_source_color(color)
            ctx.translate(x, y)
            if self.PTS:
                ipts = iter(self.PTS)
                # Move to first transformed point, then line_to the rest
                px, py = next(ipts)
                ctx.move_to(px, py)
                for px, py in ipts:
                    ctx.line_to(px, py)

                ctx.stroke()


class PathCutout(Cutout):
    """General SVG path cutout. Supports M(oveTo), L(ineTo), C(urveTo) commands."""
    # approximate size from SVG viewBox (mm)
    DIMENSIONS = (0., 0.)
    OFFSET = (0., 0.)

    # SVG path data and transform (from the provided SVG)
    SEGMENTS = [('M', (0., 0.)),
                 ('L', (0., 0.)),
                 ('C', (0., 0., 0., 0., 0., 0.))
               ]

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        with box.saved_context() as ctx:
            box.set_source_color(color)
            #
            ctx.translate(x, y)
            ctx.translate(*self.OFFSET)
            CMDS = {'M': ctx.move_to, 'L': ctx.line_to, 'C': ctx.curve_to}
            for command, params in self.SEGMENTS:
                CMDS[command](*params)
            ctx.stroke()


class MultiPathCutout(PathCutout):
    COLORS = [Color.INNER_CUT]
    SCALE = (1., 1.)
    DIMENSIONS = (100., 100.)

    def __init__(self, w=None, h=None):
        hs = ws = float('inf')
        if w is not None:
            ws = w / self.DIMENSIONS[0]
        if h is not None:
            hs = h / self.DIMENSIONS[1]
        if w is not None or h is not None:
            scale = min(ws, hs)
            self.SCALE = (scale, scale)

    def cutout(self, box, x, y, color=None):
        colors = color
        if colors is None:
            colors = self.COLORS
        elif isinstance(color[0], (float, int)):
            colors = [color]
        if len(colors) < len(self.SEGMENTS):
            colors = list(colors) + [colors[-1]] * (len(self.SEGMENTS) - len(colors))

        for color, segments in zip(colors, self.SEGMENTS):
            with box.saved_context() as ctx:
                box.set_source_color(color)
                #
                ctx.translate(x, y)
                ctx.scale(*self.SCALE)
                ctx.translate(*self.OFFSET)
                CMDS = {'M': ctx.move_to, 'L': ctx.line_to, 'C': ctx.curve_to, 'Z': ctx.stroke}
                for command, params in segments:
                    CMDS[command](*params)
                ctx.stroke()

class NoneCutout(Cutout):
    """No cutout"""


class NicotIncubatorCageCutout(CircleCutout):
    """Nicot incubator cage"""
    RADIUS = 21.35 / 2.0
    DIMENSIONS = (RADIUS * 2.0, RADIUS * 2.0)


class NicotTransportCageCutout(PathCutout):
    """Nicot transport and introduction cage"""
    DIMENSIONS = (36.2, 15.5)
    OFFSET = (-32.555031,-21.874992)
    SEGMENTS = [
        ('M', (40.305031, 27.125)),
        ('L', (40.305031, 29.625)),
        ('L', (43.555031, 29.625)),
        ('L', (43.555031, 27.125)),
        ('L', (46.555031, 27.125)),
        ('L', (49.555031, 17.125)),
        ('L', (50.055031, 17.125)),
        ('L', (50.655037, 17.125)),
        ('L', (50.655037, 14.125)),
        ('L', (41.805031, 14.125)),
        ('C', (41.805031, 14.401142, 41.581173, 14.700713, 41.305031, 14.700713)),
        ('C', (41.028889, 14.700713, 40.805031, 14.401142, 40.805031, 14.125)),
        ('L', (24.305031, 14.125)),
        ('C', (24.305031, 14.401142, 24.081173, 14.700713, 23.805031, 14.700713)),
        ('C', (23.528889, 14.700713, 23.305031, 14.401142, 23.305031, 14.125)),
        ('L', (15.055031, 14.125)),
        ('L', (14.455027, 14.125)),
        ('L', (14.455027, 17.125)),
        ('L', (15.555031, 17.125)),
        ('L', (18.555031, 27.125)),
        ('L', (21.555031, 27.125)),
        ('L', (21.555031, 29.625)),
        ('L', (24.805031, 29.625)),
        ('L', (24.805031, 27.125)),
        ('L', (40.305031, 27.125))

    ]

class NicotHatchingCageCutout(PathCutout):
    """Nicot hatching cage"""
    DIMENSIONS = (27.0, 27.0)
    SEGMENTS = [('M', (-9.721000000000004, -8.771999999999998)),
                 ('L', (-10.155346182387007, -8.265839332298988)),
                 ('C', (-13.886551020012014, -3.6821541920039706, -14.084879200641005, 2.832221276653023, -10.639422029363011, 7.634389722454024)),
                 ('L', (-13.888039878829005, 10.883002977682018)),
                 ('L', (-10.873861961053002, 13.897185158154024)),
                 ('L', (-7.625244111587008, 10.648571902926015)),
                 ('L', (-7.201256192106008, 10.944120092323026)),
                 ('C', (-1.3706305347910046, 14.78343744577301, 6.446125932330986, 13.377937282497022, 10.574118665392987, 7.747997846391023)),
                 ('C', (13.498296778466994, 3.7572195214790085, 13.925493259226002, -1.5399073009179816, 11.678636480890987, -5.947701805147979)),
                 ('C', (12.248662344696001, -7.575763913767979, 11.834613878094999, -9.385966038929986, 10.614878655487004, -10.605702986505982)),
                 ('C', (9.395143432878982, -11.825439934081977, 7.584941893271996, -12.239490960695981, 5.956878978515, -11.669467399319963)),
                 ('C', (0.6772758573989961, -14.36253149263198, -5.7526862178120055, -13.174189825958983, -9.721000000000004, -8.771999999999998))]


class QueenIconCutout(MultiPathCutout):
    """Queen icon cutout"""
    DIMENSIONS = (56.59, 47.)
    OFFSET = (-28.295, 23.5-2.)
    SEGMENTS_BEEBODY = [
        ('M', (36.173954, -1.204572)),
        ('C', (35.517052, -1.456605, 34.539562, -2.115699, 32.831482, -3.46267)),
        ('C', (32.131233, -4.009852, 32.009636, -4.090586, 31.027628, -4.590359)),
        ('C', (30.139717, -5.044017, 29.937389, -5.166808, 29.656359, -5.420141)),
        ('L', (29.452248, -5.609223)),
        ('L', (29.16152, -5.402364)),
        ('C', (28.37141, -4.854754, 27.685467, -4.871614, 27.041822, -5.451272)),
        ('C', (26.910316, -5.571545, 26.766272, -5.664952, 26.722088, -5.663759)),
        ('C', (26.602758, -5.660537, 25.987635, -5.347628, 25.48324, -5.028856)),
        ('C', (25.248287, -4.885419, 24.414343, -4.323355, 23.62388, -3.789006)),
        ('C', (21.713034, -2.490267, 21.456718, -2.319712, 20.821524, -1.93107)),
        ('C', (19.89035, -1.366386, 19.355968, -1.175058, 19.231638, -1.357445)),
        ('C', (19.153536, -1.465898, 19.2598, -1.787191, 19.427893, -1.950937)),
        ('C', (19.678009, -2.187658, 20.842571, -2.953236, 24.142872, -5.041317)),
        ('C', (24.895119, -5.51714, 25.577612, -5.955714, 25.655731, -6.010891)),
        ('L', (25.798943, -6.112058)),
        ('L', (25.590393, -6.137422)),
        ('C', (25.164593, -6.183383, 24.717545, -6.525136, 24.578764, -6.914986)),
        ('C', (24.526186, -7.059507, 24.517273, -7.063689, 24.296288, -7.057722)),
        ('C', (23.699686, -7.041614, 23.315456, -7.513294, 23.289444, -8.313069)),
        ('C', (23.267059, -8.81221, 23.356722, -9.097672, 23.627363, -9.392441)),
        ('C', (23.812029, -9.596436, 23.845709, -9.65927, 23.915951, -10.006123)),
        ('C', (24.034206, -10.540014, 24.11187, -11.103768, 24.105188, -11.351244)),
        ('L', (24.099463, -11.563374)),
        ('L', (23.931757, -11.386359)),
        ('C', (23.454462, -10.882575, 22.394306, -10.508995, 22.153162, -10.758997)),
        ('C', (22.075775, -10.840965, 22.071505, -10.836451, 21.917866, -10.628817)),
        ('C', (21.700111, -10.339898, 21.367941, -10.030197, 20.878107, -9.663168)),
        ('C', (20.167181, -9.130966, 19.191938, -8.56066, 18.718355, -8.410776)),
        ('C', (18.538601, -8.352846, 18.538601, -8.352846, 18.468243, -8.010422)),
        ('C', (18.253338, -6.960913, 17.756804, -6.023205, 17.045753, -5.331779)),
        ('C', (16.545763, -4.849492, 15.829, -4.370209, 14.716994, -3.787367)),
        ('L', (13.688, -3.242151)),
        ('L', (13.657471, -3.391695)),
        ('C', (13.616872, -3.585191, 13.507813, -3.692803, 13.271084, -3.779281)),
        ('C', (13.163948, -3.816168, 13.087393, -3.867214, 13.100047, -3.889657)),
        ('C', (13.150831, -3.97509, 13.516542, -4.188359, 14.488801, -4.705507)),
        ('C', (15.984331, -5.497713, 16.243765, -5.717002, 16.811598, -6.634529)),
        ('C', (17.392109, -7.574503, 17.809937, -8.642766, 17.796215, -9.150975)),
        ('C', (17.790846, -9.349849, 17.811724, -9.394632, 18.008711, -9.634345)),
        ('C', (18.496883, -10.226871, 19.190847, -10.732088, 20.54221, -11.458481)),
        ('C', (21.636297, -12.049678, 21.679768, -12.077393, 21.706408, -12.23732)),
        ('C', (21.717777, -12.3084, 21.767956, -12.415881, 21.814751, -12.483487)),
        ('C', (21.908745, -12.605421, 22.409451, -12.897568, 22.842432, -13.077317)),
        ('C', (24.3374, -15.647369, 24.10181, -14.838931, 24.570028, -17.723356)),
        ('C', (24.669905, -18.119656, 24.687462, -18.45182, 24.617012, -18.604698)),
        ('C', (24.555758, -18.744568, 24.524315, -18.761412, 24.213779, -18.797251)),
        ('C', (23.75238, -18.851168, 23.1448, -19.077974, 22.81539, -19.321154)),
        ('C', (22.621185, -19.470705, 22.436899, -19.744354, 22.391155, -19.964233)),
        ('C', (22.360506, -20.118204, 22.347109, -20.122263, 22.040007, -20.193571)),
        ('C', (19.877434, -20.683578, 18.298223, -21.352961, 17.888319, -21.956623)),
        ('C', (17.777723, -22.121698, 17.749054, -22.200525, 17.757912, -22.364403)),
        ('L', (17.765579, -22.572458)),
        ('L', (17.26598, -23.058712)),
        ('C', (16.734486, -23.579485, 16.395407, -24.017004, 16.239428, -24.388706)),
        ('C', (16.102552, -24.707857, 16.059685, -25.148941, 16.135433, -25.456141)),
        ('C', (16.202797, -25.745428, 16.207308, -25.741127, 15.724814, -26.08633)),
        ('C', (14.66062, -26.844809, 12.872028, -27.734081, 11.999649, -27.940496)),
        ('C', (11.84378, -27.980482, 11.714305, -28.025669, 11.713827, -28.043348)),
        ('C', (11.71335, -28.061014, 11.734943, -28.079275, 11.757107, -28.079874)),
        ('C', (11.863169, -28.082737, 12.206918, -28.291019, 12.266289, -28.385494)),
        ('C', (12.30007, -28.443872, 12.327958, -28.559629, 12.32569, -28.643606)),
        ('C', (12.323304, -28.731998, 12.351769, -28.82563, 12.386409, -28.85309)),
        ('C', (12.541928, -28.989983, 13.492299, -28.679537, 14.394303, -28.195301)),
        ('C', (15.341211, -27.685745, 16.064041, -27.121485, 16.395357, -26.643961)),
        ('C', (16.515141, -26.465862, 16.719625, -26.263531, 16.999712, -26.045547)),
        ('C', (17.433384, -25.707872, 17.780104, -25.314781, 17.889618, -25.025864)),
        ('C', (17.927351, -24.938421, 17.980082, -24.625845, 18.005568, -24.33466)),
        ('C', (18.031116, -24.043467, 18.079706, -23.71751, 18.113655, -23.607864)),
        ('L', (18.167667, -23.410316)),
        ('L', (18.523352, -23.340353)),
        ('C', (19.20368, -23.203936, 20.693081, -22.421553, 22.161566, -21.430761)),
        ('L', (22.891335, -20.937458)),
        ('L', (22.968094, -21.041245)),
        ('C', (23.211645, -21.357395, 22.910282, -22.034748, 21.639524, -24.056898)),
        ('C', (20.341032, -26.122541, 19.792238, -27.284101, 19.510265, -28.554598)),
        ('C', (19.490562, -28.629242, 19.395008, -28.728386, 19.223976, -28.838743)),
        ('C', (18.507828, -29.319159, 18.003328, -29.822966, 17.723732, -30.350546)),
        ('C', (17.565245, -30.651417, 17.555571, -30.682117, 17.573378, -31.005436)),
        ('L', (17.590782, -31.342012)),
        ('L', (16.946178, -31.957035)),
        ('C', (16.564941, -32.318233, 15.981131, -32.811054, 15.525355, -33.148125)),
        ('C', (15.100994, -33.468357, 14.721304, -33.772114, 14.680099, -33.824062)),
        ('C', (14.597273, -33.941216, 14.639501, -34.017555, 14.815069, -34.066517)),
        ('C', (15.030185, -34.125412, 15.129314, -34.220947, 15.125378, -34.366772)),
        ('L', (15.121678, -34.503769)),
        ('L', (15.381824, -34.369274)),
        ('C', (16.346415, -33.860199, 17.170763, -33.139477, 17.859304, -32.207226)),
        ('C', (18.171387, -31.786671, 18.299063, -31.644173, 18.383398, -31.633186)),
        ('C', (18.667299, -31.601074, 19.250515, -31.130327, 19.644537, -30.623528)),
        ('C', (19.983612, -30.186008, 20.259033, -29.649469, 20.396011, -29.162271)),
        ('C', (20.425224, -29.06135, 20.476139, -28.978697, 20.50708, -28.979532)),
        ('C', (20.630825, -28.982874, 20.978628, -28.71364, 21.157654, -28.470823)),
        ('C', (21.44215, -28.089321, 21.713505, -27.539412, 22.10297, -26.546009)),
        ('L', (22.458874, -25.649004)),
        ('L', (22.459421, -25.958603)),
        ('C', (22.47122, -27.980005, 22.318005, -30.876537, 23.059479, -35.680527)),
        ('C', (23.974567, -40.450001, 25.976158, -46.742531, 28.317249, -47.000053)),
        ('C', (31.359238, -46.838863, 32.96664, -39.323856, 33.684227, -36.258587)),
        ('C', (33.981937, -34.082207, 34.695244, -27.314993, 34.659618, -26.177446)),
        ('L', (34.644474, -25.756889)),
        ('L', (34.759869, -26.06958)),
        ('C', (35.249134, -27.4405, 36.351353, -28.876614, 36.925869, -28.892126)),
        ('C', (37.058449, -28.895706, 37.066929, -28.909204, 37.092842, -29.095648)),
        ('C', (37.215775, -30.111725, 38.158791, -31.384333, 38.825146, -31.437698)),
        ('C', (38.97958, -31.450775, 39.066071, -31.523863, 39.824169, -32.273994)),
        ('C', (40.776024, -33.219582, 41.155968, -33.561523, 41.598621, -33.874191)),
        ('C', (41.919678, -34.103992, 42.246113, -34.298561, 42.316826, -34.300468)),
        ('C', (42.338898, -34.301067, 42.371872, -34.22678, 42.392078, -34.134441)),
        ('C', (42.41785, -33.998035, 42.48204, -33.915752, 42.785385, -33.654167)),
        ('C', (42.989025, -33.482769, 43.143826, -33.318878, 43.135693, -33.292122)),
        ('C', (43.127518, -33.265411, 43.031544, -33.21854, 42.921894, -33.184624)),
        ('C', (42.382019, -33.032951, 40.075352, -31.489138, 39.659447, -31.004696)),
        ('C', (39.487923, -30.805473, 39.468334, -30.71207, 39.573563, -30.582233)),
        ('C', (39.889462, -30.183886, 39.190731, -29.364559, 37.893463, -28.599817)),
        ('L', (37.575634, -28.414337)),
        ('L', (37.581718, -28.188951)),
        ('C', (37.604233, -27.190069, 36.956268, -25.965231, 35.540501, -24.348169)),
        ('C', (35.248917, -24.008606, 34.919147, -23.610518, 34.812595, -23.461695)),
        ('C', (34.54422, -23.082966, 34.263859, -22.491631, 34.152058, -22.04636)),
        ('C', (34.035706, -21.605389, 33.957573, -20.895676, 34.016575, -20.839769)),
        ('C', (34.08469, -20.775238, 34.423046, -20.855194, 34.706581, -20.999929)),
        ('C', (34.85051, -21.074589, 35.337116, -21.397284, 35.792801, -21.719168)),
        ('C', (36.990322, -22.574083, 37.745556, -22.939434, 38.503643, -23.03508)),
        ('L', (38.781223, -23.073523)),
        ('L', (38.77335, -23.365194)),
        ('C', (38.751545, -24.337557, 39.412891, -25.558332, 40.16811, -25.923685)),
        ('C', (40.272869, -25.975185, 40.404243, -26.022934, 40.457275, -26.024364)),
        ('C', (40.528004, -26.026276, 40.588058, -26.094267, 40.684456, -26.29143)),
        ('C', (41.062019, -27.04903, 41.805317, -27.692671, 42.888538, -28.195124)),
        ('C', (43.368923, -28.420368, 44.41058, -28.824408, 44.442356, -28.794312)),
        ('C', (44.451611, -28.78129, 44.453762, -28.701735, 44.442799, -28.612993)),
        ('C', (44.420498, -28.4576, 44.434307, -28.435863, 44.765152, -28.139647)),
        ('C', (44.95541, -27.972307, 45.109859, -27.821695, 45.110218, -27.808434)),
        ('C', (45.110577, -27.795172, 45.06218, -27.785049, 45.000324, -27.783381)),
        ('C', (44.783794, -27.777534, 44.333607, -27.579639, 43.295887, -27.029772)),
        ('C', (42.223186, -26.465679, 41.475002, -26.003227, 41.216412, -25.753008)),
        ('C', (41.074268, -25.61208, 41.070091, -25.603121, 41.056335, -25.129532)),
        ('C', (41.024097, -24.031885, 40.645771, -23.137167, 39.913231, -22.423067)),
        ('C', (39.667534, -22.186459, 39.620831, -22.114437, 39.653679, -22.044569)),
        ('C', (39.719925, -21.882721, 39.703213, -21.683262, 39.613632, -21.561438)),
        ('C', (39.425762, -21.31312, 39.001263, -21.146877, 37.99855, -20.938478)),
        ('C', (36.727589, -20.674187, 35.946568, -20.44525, 35.313156, -20.15395)),
        ('C', (34.719063, -19.881409, 34.425339, -19.621387, 34.24176, -19.213984)),
        ('C', (34.141781, -18.985741, 34.128757, -18.976536, 33.830761, -18.875631)),
        ('C', (33.664249, -18.818056, 33.308792, -18.715591, 33.04089, -18.646442)),
        ('C', (32.566475, -18.527498, 32.557747, -18.522831, 32.569698, -18.408165)),
        ('C', (32.58157, -18.29792, 32.52813, -17.80278, 32.558498, -17.212297)),
        ('C', (32.663059, -14.947853, 32.611317, -15.189217, 33.583523, -13.094082)),
        ('C', (33.741093, -12.925749, 33.905624, -12.827523, 34.198975, -12.609893)),
        ('C', (34.523964, -12.366582, 34.721512, -12.093303, 34.827808, -11.76006)),
        ('C', (34.900814, -11.514372, 34.905216, -11.51449, 35.154823, -11.441621)),
        ('C', (35.511341, -11.340681, 36.129917, -11.034545, 36.490501, -10.783346)),
        ('C', (37.099159, -10.353111, 37.887432, -9.494317, 38.203938, -8.910247)),
        ('C', (38.245842, -8.831815, 38.414391, -8.650586, 38.57766, -8.500199)),
        ('C', (38.935745, -8.178177, 39.249008, -7.71343, 39.415497, -7.280095)),
        ('C', (39.50618, -7.034888, 39.546986, -6.83255, 39.581608, -6.369123)),
        ('C', (39.608238, -6.038152, 39.651958, -5.729761, 39.679836, -5.681864)),
        ('C', (39.855995, -5.381461, 40.734463, -4.786028, 41.895996, -4.189394)),
        ('C', (42.649418, -3.802873, 42.979309, -3.542001, 42.985157, -3.325458)),
        ('C', (42.989334, -3.170784, 42.894138, -3.093037, 42.695267, -3.087667)),
        ('C', (42.593616, -3.084923, 42.537243, -3.043622, 42.431057, -2.88152)),
        ('C', (42.299427, -2.678952, 42.150723, -2.617434, 42.050869, -2.712039)),
        ('C', (42.023682, -2.737795, 41.732086, -2.88918, 41.400414, -3.052707)),
        ('C', (40.046696, -3.723757, 39.300564, -4.331607, 38.922321, -5.073222)),
        ('C', (38.828796, -5.260862, 38.727402, -5.412915, 38.700893, -5.412199)),
        ('C', (38.630169, -5.41029, 38.429642, -5.630421, 38.327175, -5.822251)),
        ('C', (38.196503, -6.075227, 38.097511, -6.466151, 37.945961, -7.328871)),
        ('C', (37.872681, -7.751456, 37.800987, -8.11216, 37.78714, -8.1339)),
        ('C', (37.773281, -8.155613, 37.671177, -8.170534, 37.556263, -8.167432)),
        ('C', (37.109917, -8.15538, 36.610546, -8.469161, 35.486652, -9.473688)),
        ('C', (34.458046, -10.387909, 34.412785, -10.426489, 34.258121, -10.422314)),
        ('C', (34.06366, -10.417063, 33.723984, -10.549403, 33.261398, -10.81111)),
        ('C', (33.032421, -10.937635, 32.808361, -11.04656, 32.759514, -11.05409)),
        ('C', (32.697453, -11.061312, 32.624313, -10.984064, 32.471298, -10.754429)),
        ('C', (32.360931, -10.583385, 32.268715, -10.395146, 32.270145, -10.342121)),
        ('C', (32.271698, -10.284692, 32.369049, -10.119246, 32.492535, -9.967786)),
        ('C', (33.096649, -9.21459, 33.291428, -8.06115, 32.944061, -7.330901)),
        ('C', (32.785202, -6.990504, 32.637104, -6.906902, 32.164356, -6.889707)),
        ('C', (31.735802, -6.873692, 31.328154, -6.738877, 30.989529, -6.504192)),
        ('C', (30.833181, -6.398253, 30.658436, -6.154728, 30.66118, -6.05308)),
        ('C', (30.661776, -6.031009, 30.851204, -5.894581, 31.0804, -5.759244)),
        ('C', (31.885294, -5.267969, 34.361954, -3.464113, 35.487904, -2.548093)),
        ('C', (35.976395, -2.145567, 36.59317, -1.578457, 36.748669, -1.388059)),
        ('C', (36.863091, -1.245206, 36.867744, -1.236484, 36.785362, -1.17677)),
        ('C', (36.668438, -1.085147, 36.469212, -1.093066, 36.174313, -1.204541)),
        ('L', (36.173954, -1.204572))
    ]
    SEGMENTS_BEEBODY_CIRCLE = [
        ('Z', ()),
        ('M', (31.452539, -15.104019)),
        ('C', (31.497332, -13.445015, 30.188753, -12.063812, 28.529749, -12.01902)),
        ('C', (26.870743, -11.974228, 25.489542, -13.282806, 25.44475, -14.941811)),
        ('C', (25.399958, -16.600819, 26.708536, -17.982019, 28.367542, -18.026812)),
        ('C', (30.026546, -18.071604, 31.407747, -16.763025, 31.452539, -15.104019))
    ]
    SEGMENTS_RINGS = [
        ('M', (22.737341, -25.976702)),
        ('C', (25.809727, -27.552916, 31.010199, -27.767921, 34.371002, -26.366888)),
        ('M', (23.917017, -21.928125)),
        ('C', (26.693502, -21.004694, 30.186104, -21.220146, 32.984138, -22.134012)),
        ('M', (22.867329, -31.515833)),
        ('C', (25.369101, -32.762085, 31.522942, -32.784451, 33.897713, -31.827881)),
        ('M', (23.605927, -36.805847)),
        ('C', (26.107697, -38.052105, 30.506796, -38.117798, 33.189774, -37.063282)),
        ('M', (24.930559, -41.292728)),
        ('C', (27.229265, -41.869137, 29.605104, -41.992916, 31.893511, -41.499496)),
    ]
    SEGMENTS_CROWN = [
        ('M', (28.292725, -3.40377)),
        ('L', (28.037292, -3.408754)),
        ('L', (27.78186, -3.40377)),
        ('L', (27.534744, -3.389053)),
        ('L', (27.284531, -3.363651)),
        ('L', (27.049286, -3.32947)),
        ('L', (26.819016, -3.28484)),
        ('L', (26.602753, -3.23024)),
        ('L', (26.404068, -3.167332)),
        ('L', (26.223648, -3.09564)),
        ('L', (26.206772, -3.084961)),
        ('L', (26.197983, -3.074751)),
        ('L', (26.192291, -3.062883)),
        ('L', (26.189377, -3.042707)),
        ('L', (26.189377, -2.210186)),
        ('L', (26.191315, -2.185261)),
        ('L', (26.197006, -2.162474)),
        ('L', (26.578247, -1.018501)),
        ('L', (26.934799, -2.088409)),
        ('L', (26.978699, -2.148468)),
        ('L', (27.064407, -2.178616)),
        ('L', (27.151291, -2.153452)),
        ('L', (27.198547, -2.096003)),
        ('L', (28.036758, --0.000134)),
        ('L', (28.874969, -2.096003)),
        ('L', (28.92247, -2.153688)),
        ('L', (29.009583, -2.178614)),
        ('L', (29.094818, -2.148466)),
        ('L', (29.138718, -2.088408)),
        ('L', (29.49527, -1.018499)),
        ('L', (29.876511, -2.162472)),
        ('L', (29.882202, -2.185259)),
        ('L', (29.88414, -2.210186)),
        ('L', (29.88414, -3.042706)),
        ('L', (29.881226, -3.06217)),
        ('L', (29.87529, -3.074991)),
        ('L', (29.866486, -3.085201)),
        ('L', (29.850586, -3.095173)),
        ('L', (29.671829, -3.166628)),
        ('L', (29.47171, -3.230009)),
        ('L', (29.25592, -3.284372)),
        ('L', (29.024231, -3.329712)),
        ('L', (28.789688, -3.363657)),
        ('L', (28.539719, -3.389059)),
        ('L', (28.292725, -3.40377))
    ]
    SEGMENTS_WING_RIGHT = [
        ('M', (32.530521, -17.573362)),
        ('C', (32.396538, -17.8936, 33.355881, -17.79258, 33.857777, -18.04051)),
        ('C', (37.514843, -19.855181, 39.478458, -20.673286, 40.964424, -21.000877)),
        ('C', (41.399658, -21.096695, 41.505608, -21.103958, 41.842663, -21.068762)),
        ('C', (42.707409, -20.981548, 43.693031, -20.676472, 44.987011, -20.087833)),
        ('C', (47.136082, -19.115421, 48.739887, -17.862921, 48.759216, -17.146999)),
        ('C', (48.765182, -16.926043, 48.711197, -16.796331, 48.564262, -16.66853)),
        ('L', (48.460606, -16.577271)),
        ('L', (48.982201, -16.586901)),
        ('C', (50.13158, -16.604662, 52.087509, -16.069273, 52.849514, -15.528199)),
        ('C', (53.079552, -15.361928, 54.056911, -14.379986, 54.599983, -13.757813)),
        ('C', (56.105602, -12.047149, 56.831638, -10.709038, 56.583191, -10.083183)),
        ('C', (56.508793, -9.891013, 56.383568, -9.777075, 55.995869, -9.558744)),
        ('C', (54.057678, -8.453864, 50.805088, -8.366046, 46.618382, -9.296663)),
        ('C', (44.184563, -9.841254, 42.030354, -10.51281, 38.019482, -11.974506)),
        ('C', (36.902847, -12.382182, 35.795528, -12.772429, 35.563702, -12.841352)),
        ('C', (34.783524, -13.072369, 33.719185, -13.397408, 33.501328, -13.276538)),
        ('C', (32.407406, -15.800676, 32.630482, -15.419465, 32.53051, -17.573372)),
        ('L', (32.530521, -17.573362)),
    ]
    SEGMENTS_WING_LEFT = [
        ('M', (23.539158, -14.179784)),
        ('C', (22.675388, -13.110837, 23.575832, -14.311259, 22.978552, -13.300768)),
        ('C', (22.43601, -13.234628, 23.213654, -13.250943, 22.986689, -13.302304)),
        ('C', (22.488024, -13.425939, 19.685472, -12.885914, 18.327419, -12.406995)),
        ('C', (15.913641, -11.554621, 11.940078, -10.487658, 9.168577, -9.944035)),
        ('C', (7.034884, -9.528204, 5.571148, -9.360426, 3.992511, -9.353188)),
        ('C', (2.590877, -9.34193, 1.991412, -9.431835, 1.248386, -9.761151)),
        ('C', (0.223484, -10.21111, -0.2257, -11.286922, 0.104582, -12.485494)),
        ('C', (0.431401, -13.648589, 1.50903, -15.013285, 2.863268, -15.960888)),
        ('C', (4.677482, -17.234913, 6.555089, -17.634968, 7.867358, -17.024714)),
        ('C', (7.988228, -16.970497, 8.091179, -16.924623, 8.100021, -16.924862)),
        ('C', (8.101342, -16.924898, 8.102164, -16.925589, 8.102494, -16.926846)),
        ('C', (8.105895, -16.938936, 8.070649, -17.003836, 8.020485, -17.086294)),
        ('C', (7.868207, -17.321007, 7.870959, -17.710247, 8.026042, -18.028431)),
        ('C', (8.532495, -19.09025, 10.750173, -20.326502, 13.328659, -20.975481)),
        ('C', (14.101685, -21.173252, 14.683116, -21.259705, 15.346013, -21.277603)),
        ('C', (16.097292, -21.297888, 16.346437, -21.242743, 16.854172, -20.94684)),
        ('C', (18.175138, -20.177599, 22.394899, -18.186426, 23.766176, -17.683899)),
        ('C', (24.538824, -17.404036, 24.137623, -17.502926, 24.454489, -17.524492)),
        ('C', (24.295069, -15.216845, 24.339058, -16.639975, 24.08506, -15.412374)),
        ('L', (23.539158, -14.179784))
    ]
    SEGMENTS_WING_RIGHT_INNER = [
        ('M', (48.57967, -16.60989)),
        ('C', (47.047802, -16.40626, 45.931446, -16.090261, 42.571247, -15.756836)),
        ('C', (33.444118, -15.240843, 33.887115, -15.38158, 33.124851, -15.289225)),
        ('L', (32.80624, -15.280622)),
    ]
    SEGMENTS_WING_LEFT_INNER = [
        ('M', (8.050785, -16.950422)),
        ('C', (10.225066, -16.132313, 14.153243, -15.988667, 16.281616, -15.886717)),
        ('C', (21.896767, -15.560055, 21.310425, -15.926777, 23.954018, -15.440171)),
        ('L', (24.060944, -15.416491))
    ]
    COLORS = [Color.ETCHING_DEEP, Color.ETCHING_DEEP,  # Filled darker
              Color.ETCHING, Color.ETCHING,  # Filled lighter
              Color.YELLOW  # Outlines
              ]
    SEGMENTS = [SEGMENTS_BEEBODY + SEGMENTS_BEEBODY_CIRCLE, SEGMENTS_CROWN, SEGMENTS_WING_RIGHT, SEGMENTS_WING_LEFT,  # Fillings
                SEGMENTS_BEEBODY, SEGMENTS_CROWN, SEGMENTS_WING_RIGHT, SEGMENTS_WING_LEFT,  # Outlines
                SEGMENTS_WING_RIGHT_INNER, SEGMENTS_WING_LEFT_INNER, SEGMENTS_RINGS]        # Outlines


class AirHolesForNicotTransportCageCutout(Cutout):
    """Air hole cutout for Nicot transport cage"""
    DIMENSIONS = NicotTransportCageCutout.DIMENSIONS
    SIZE = (25., 3.)
    OFFSET = (0., -1.250)

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        aw = box.aw
        ah = box.ah
        with box.saved_context():
            box.set_source_color(color)
            l, h = self.SIZE
            ox, oy = self.OFFSET
            box.rectangularHole(x + ox, y + oy - h, l, h, h/2., True, True)
            box.rectangularHole(x + ox, y + oy + h, l, h, h/2., True, True)


class HexHolesCutout(Cutout):
    """Hexagonal hole pattern cutout"""
    DIMENSIONS = (20., 20.)
    RADIUS = 10.
    OFFSET = (0., 0.)
    IRADIUS = 2.
    LEVELS = 3

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        with box.saved_context() as ctx:
            box.set_source_color(color)
            ctx.translate(x, y)
            ctx.translate(*self.OFFSET)
            draw = box.regularPolygonHole
            draw(0., 0., self.IRADIUS)
            cxy = [ (math.cos(a), math.sin(a)) for a in (math.radians(angle) for angle in range(30, 360, 60)) ]
            r = 2.5 * self.IRADIUS
            for cx, cy in cxy:
                draw(r * cx, r * cy, self.IRADIUS)
            if self.LEVELS > 2:
                r = 5. * self.IRADIUS
                for cx, cy in cxy:
                    draw(r * cx, r * cy, self.IRADIUS)
                    lx, ly = cxy[-1]
                r *= .5
                for cx, cy in cxy:
                    draw(r * (cx + lx), r * (cy + ly), self.IRADIUS)
                    lx, ly = cx, cy


class GiantHexHoleCutout(Cutout):
    """Giant hexagonal hole pattern cutout"""
    DIMENSIONS = (20., 20.)
    RADIUS = 10.
    OFFSET = (0., 0.)
    IRADIUS = 1.5
    NUMBER = 6

    def __init__(self, number=None, w=None, h=None):
        if number is not None:
            self.number = number
        elif w is not None or h is not None:
            if w is not None:
                nw = int(w / (2 * 2.5 * self.IRADIUS))
            else:
                nw = float('inf')
            if h is not None:
                nh = int(h / (math.sqrt(3) * 2.5 * self.IRADIUS))
            else:
                nh = float('inf')
            self.number = min(nw, nh)

    def get_circumcircle(self):
        return 2.5 * self.IRADIUS * (self.number - 1)

    def get_incircle(self):
        return 2.5 * self.IRADIUS * (self.number - 2)

    def cutout(self, box, x, y, color=Color.INNER_CUT):
        with box.saved_context() as ctx:
            box.set_source_color(color)
            ctx.translate(x, y)
            ctx.translate(*self.OFFSET)
            draw = lambda x, y: box.regularPolygonHole(x, y, self.IRADIUS, a=30)
            number = self.number - 1
            length = number * 2.5 * self.IRADIUS
            a = math.radians(120)
            cx = length * math.cos(a)
            cy = length * math.sin(a)
            dx = self.IRADIUS * 2.5
            for _ in range(6):
                for row in range(number):
                    draw(cx + dx * row, cy)
                ctx.rotate(math.radians(60))

class AirHolesForNicotIncubatorCageCutout(HexHolesCutout):
    """Air hole cutout for Nicot incubator cage"""
    RADIUS = NicotIncubatorCageCutout.RADIUS * 0.8
    DIMENSIONS = NicotIncubatorCageCutout.DIMENSIONS
    OFFSET = (0., 0.)
    IRADIUS = 2.
    LEVELS = 2

class AirHolesCover(HexHolesCutout):
    """Air hole cutout for lid cover"""
    RADIUS = NicotIncubatorCageCutout.RADIUS * 0.8
    DIMENSIONS = NicotIncubatorCageCutout.DIMENSIONS
    OFFSET = (0., 0.)
    IRADIUS = 2.
    LEVELS = 2

class AirHolesForNicotHatchingCageCutout(HexHolesCutout):
    """Air hole cutout for Nicot hatching cage"""
    DIMENSIONS = NicotHatchingCageCutout.DIMENSIONS
    RADIUS = min(NicotHatchingCageCutout.DIMENSIONS) / 2.
    OFFSET = (0., 0.)
    IRADIUS = 2.
    LEVELS = 3


class QueenTransportBoxLidSettings(LidSettings):
    """Lid settings for Queen Transport Box"""
    absolute_params = LidSettings.absolute_params.copy() | {"cover": ("none", "airholes", "queenicon", "queenicon_airholes"), "queeniconscale": 75.}


class QueenTransportBoxLid(Lid):

    def handleCB(self, x: float, y: float) -> Callable:
        if self.handle == 'none':
            airholes = self.cover in ("airholes", "queenicon_airholes")
            queenicon = self.cover in ("queenicon", "queenicon_airholes")
            return self.render_cover(x, y, airholes, queenicon)
        else:
            return super().handleCB(x, y)

    def render_cover(self, x: float, y: float, airholes: bool, queenicon: bool) -> Callable:
        def cover():
            if airholes:
                with self.saved_context() as ctx:
                    ctx.translate(.5 * x, .5 * y)
                    cutout = AirHolesCover()
                    dx = .5 * x - 2. * cutout.RADIUS
                    dy = .5 * y - 2. * cutout.RADIUS
                    cutout.cutout(self, dx, dy)
                    cutout.cutout(self, dx, -dy)
                    cutout.cutout(self, -dx, -dy)
                    cutout.cutout(self, -dx, dy)

            if queenicon:
                with self.saved_context() as ctx:
                    k = self.settings.queeniconscale / 100.
                    cutout = GiantHexHoleCutout(w=k*x, h=k*y)
                    cutout.cutout(self, .5 * x, .5 * y)
                    r = 2. * .7 * cutout.get_incircle()
                    QueenIconCutout(w=r, h=r).cutout(self, .5 * x, .5 * y)
        return cover

class QueenTransportBox(_TopEdge):
    """Box for Bee Queen Transport Cages"""

    description = "Queen Transport Box"

    ui_group = "Box"

    CUTOUTS = (NicotTransportCageCutout, NicotHatchingCageCutout, NicotIncubatorCageCutout, AirHolesForNicotTransportCageCutout, AirHolesForNicotIncubatorCageCutout, AirHolesForNicotHatchingCageCutout, NoneCutout)
    LAYERS = (NoneCutout, NicotTransportCageCutout, NoneCutout)
    DEFAULT = dict(sx="5:45*3:5", sy="5:30*3:5", sh="25:75", aw=3.0, ah="70:20", ax="10:20:10:20:10:20:10", ay="20:60:20", bottom_edge="s", top_edge="e")
    CHOICES = dict(top_edge="eStG", bottom_edge="Fhsše")
    LIDSETTINGS = dict(style="overthetop")

    def _buildObjects(self):
        super()._buildObjects()
        self.lidSettings = QueenTransportBoxLidSettings(self.thickness, True, **self.edgesettings.get("QueenTransportBoxLid", {}))
        self.lid = QueenTransportBoxLid(self, self.lidSettings)

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.addSettingsArgs(QueenTransportBoxLidSettings, **self.LIDSETTINGS)
        self.addSettingsArgs(edges.StackableSettings)
        self.argparser.add_argument(
            "--top_edge", action="store",
            type=ArgparseEdgeType(self.CHOICES["top_edge"]),
            choices=list(self.CHOICES["top_edge"]),
            default=self.DEFAULT["top_edge"],
            help="edge type for top edge")
        self.argparser.add_argument(
            "--bottom_edge", action="store",
            type=ArgparseEdgeType(self.CHOICES["bottom_edge"]),
            choices=list(self.CHOICES["bottom_edge"]),
            default=self.DEFAULT["bottom_edge"],
            help="edge type for bottom edge")
        self.buildArgParser(sx=self.DEFAULT["sx"], sy=self.DEFAULT["sy"], sh=self.DEFAULT["sh"])
        self.argparser.add_argument(
            "--aw", action="store", type=float,
            default=self.DEFAULT["aw"],
            help="""air hole slot width in mm""")
        self.argparser.add_argument(
            "--ah", action="store", type=argparseSections,
            default=self.DEFAULT["ah"],
            help="""air hole sections bottom to top in mm""")
        self.argparser.add_argument(
            "--ax", action="store", type=argparseSections,
            default=self.DEFAULT["ax"],
            help="""air hole sections sections left to right in %% of the box width""")
        self.argparser.add_argument(
            "--ay", action="store", type=argparseSections,
            default=self.DEFAULT["ay"],
            help="""air hole sections back to front in %% of the box depth""")

        # add cutout selection based on CUTOUTS; use class names as keys and first docline as descriptions
        cutout_choices = [c.__name__.removesuffix('Cutout') for c in self.CUTOUTS]
        cutout_descriptions = "; ".join(
            f"{c.__name__}: {((c.__doc__ or '').strip().splitlines()[0]) if (c.__doc__ or '').strip() else ''}"
            for c in self.CUTOUTS
        )
        layers = [c.__name__.removesuffix('Cutout') for c in self.LAYERS]
        for n, default in enumerate(layers):
            layer = len(layers) - 1 - n
            self.argparser.add_argument(
                f"--layer{layer}", action="store",
                choices=cutout_choices, default=default,
                help=f"select cutout type for layer {layer}{" (bottom)" if layer == 0 else ""}." )

    def get_cutout(self, cutout_name):
        for cutout_class in self.CUTOUTS:
            if cutout_class.__name__.removesuffix('Cutout') == cutout_name:
                return cutout_class()
        raise ValueError(f"Cutout '{cutout_name}' not found.")

    def cutouts(self, layer=0):
        y = 0.
        cutout = self.get_cutout(getattr(self, f"layer{layer}"))
        for dy in self.sy:
            x = 0.
            for dx in self.sx:
                if dx > cutout.DIMENSIONS[0] and dy > cutout.DIMENSIONS[1]:
                    cutout.cutout(self, x + dx / 2., y + dy / 2.)
                x += dx
            y += dy

    def sideholes(self, l):
        t = self.thickness
        h = -0.5 * t
        for d in self.sh[:-1]:
            h += d + t
            self.fingerHolesAt(0, h, l, angle=0)

    def airholes(self, l, sections):
        aw = self.aw
        total = sum(sections)
        pl = l / 100.
        y = 0.0
        with self.saved_context():
            self.ctx.rotate(math.pi / -2.0)
            for h in self.ah:
                y += h
                px = 0.0
                for n, s in enumerate(sections):
                    if n % 2 == 1:
                        self.rectangularHole(px * pl - l, y, pl * s, aw, aw/2., False, True)
                    px += s

    def render(self):
        x = sum(self.sx)
        y = sum(self.sy)

        h = sum(self.sh) + self.thickness * (len(self.sh)-1)
        b = self.bottom_edge
        t_left, t_back, t_right, t_front = self.topEdges(self.top_edge)

        # Walls
        with self.saved_context():
            self.rectangularWall(
                x, h, [b, "F", t_back, "F"],
                ignore_widths=[1, 6],
                callback=[lambda: self.sideholes(x), lambda: self.airholes(x, self.ax)],
                move="right", label='Back')
            self.rectangularWall(
                x, h, [b, "F", t_front, "F"],
                ignore_widths=[1, 6],
                callback=[lambda: self.sideholes(x), lambda: self.airholes(x, self.ax)],
                move="right", label='Front')
            self.rectangularWall(
                y, h, [b, "f", t_left, "f"],
                ignore_widths=[1, 6],
                callback=[lambda: self.sideholes(y), lambda: self.airholes(y, self.ay)],
                move="right", label='Left')
            self.rectangularWall(
                y, h, [b, "f", t_right, "f"],
                ignore_widths=[1, 6],
                callback=[lambda: self.sideholes(y), lambda: self.airholes(y, self.ay)],
                move="right", label='Right')

        # Move up
        self.rectangularWall(
            x, h, [b, "F", t_back, "F"],
            ignore_widths=[1, 6],
            move="up only")

        # Inner Layers
        if b not in "eš":
            self.rectangularWall(
                x, y, "ffff", callback=[lambda: self.cutouts(layer=0)],
                move="right", label=f'Bottom Layer')
        for layer in range(1, len(self.sh)):
            self.rectangularWall(
                x, y, "ffff", callback=[lambda: self.cutouts(layer)],
                move="right", label=f'Layer {layer}')

        # Lid
        self.lid(x, y, self.top_edge)
