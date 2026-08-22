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

from boxes import *
from boxes import robot, servos


class RobotArm(Boxes): # change class name here and below
    """Segments of servo powered robot arm"""

    ui_group = "Part"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)
        for i in range(1, 6):
            ra = robot.RobotArg(True)
            sa = servos.ServoArg()
            self.argparser.add_argument(
                f"--type{i}", action="store", type=ra,
                default="none", choices=ra.choices(),
                help="type of arm segment")
            self.argparser.add_argument(
                f"--servo{i}a", action="store", type=sa, default="Servo9g",
                choices=sa.choices(), help="type of servo to use")
            self.argparser.add_argument(
                f"--servo{i}b", action="store", type=sa, default="Servo9g",
                choices=sa.choices(), help="type of servo to use on second side (if different is supported)")
            self.argparser.add_argument(
                f"--length{i}", action="store", type=float, default=50.,
                help="length of segment axle to axle")

    def render(self):

        for i in range(5, 0,-1):
            armtype = getattr(self, f"type{i}")
            length = getattr(self, f"length{i}")
            servoA = getattr(self, f"servo{i}a")
            servoB = getattr(self, f"servo{i}b")
            armcls = getattr(robot, armtype, None)
            if not armcls:
                continue
            servoClsA = getattr(servos, servoA)
            servoClsB = getattr(servos, servoB)
            armcls(self, servoClsA(self), servoClsB(self))(length, move="up")
