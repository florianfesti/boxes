__all__ = [
    "RobotArg",
    "RobotArmMM",
    "RobotArmMm",
    "RobotArmUU",
    "RobotArmUu",
    "RobotArmMu",
]

class RobotArg:

    def __init__(self, includenone=False):
        self.robotarms = [
            (name, globals()[name].__doc__[23:]) for name in __all__
            if name.startswith("RobotArm")]
        if includenone:
            self.robotarms[0:0] = [("none", "")]

    def __call__(self, arg):
        return str(arg)

    def choices(self):
        return [name for name, descr in self.robotarms]

    def html(self, name, default, translate):
        options = "\n".join(
            ("""<option value="%s"%s>%s %s</option>""" %
             (name, ' selected="selected"' if name == default else "",
              name, descr) for name, descr in self.robotarms))
        return """<select name="%s" size="1">\n%s</select>\n""" % (name, options)


class _RobotArm:

    def __init__(self, boxes, servo, servo2=None):
        self.boxes = boxes
        self.servo = servo
        self.servo2 = servo2 or servo

    def __getattr__(self, name):
        """Hack for easy access of Boxes methods"""
        return getattr(self.boxes, name)

class RobotArmMM(_RobotArm):
    """Robot arm segment with two parallel servos"""
    def __call__(self, length, move=None):
        t = self.thickness
        w = self.servo.height
        l = max(self.servo.length * 2, length + 2*self.servo.axle_pos)

        th = max(2 * t + l, 2*w + 4*t + self.spacing)
        tw = 5 * (w + 2*self.thickness + self.spacing)

        if self.move(tw, th, move, True):
            return

        self.rectangularWall(w, l, "FfFf", callback=[
            lambda:self.servo.top(w/2), None,
            lambda:self.servo.top(w/2)], move="right")
        self.rectangularWall(w, l, "FfFf", callback=[
            lambda:self.servo.bottom(w/2), None,
            lambda:self.servo.bottom(w/2)], move="right")
        self.rectangularWall(w, l, "FFFF", move="right")
        self.rectangularWall(w, l, "FFFF", move="right")
        self.rectangularWall(w, w, "ffff", callback=[
            lambda:self.servo.front(w/2)], move="up")
        self.rectangularWall(w, w, "ffff", callback=[
            lambda:self.servo.front(w/2)], move="")

        self.move(tw, th, move)

class RobotArmMm(_RobotArm):
    """Robot arm segment with two orthogonal servos"""
    def __call__(self, length, move=None):
        t = self.thickness
        w = self.servo.height
        w2 = self.servo2.height
        l = max(self.servo.length * 2, length + 2*self.servo.axle_pos)

        th = max(2 * self.thickness + l, w + w2 + 4*t + self.spacing)
        tw = 5 * (max(w, w2) + 2*self.thickness + self.spacing)

        if self.move(tw, th, move, True):
            return

        self.rectangularWall(w2, l, "FfFf", callback=[
            lambda:self.servo.top(w2/2)], move="right")
        self.rectangularWall(w2, l, "FfFf", callback=[
            lambda:self.servo.bottom(w2/2)], move="right")
        self.rectangularWall(w, l, "FFFF", callback=[
            None, None, lambda:self.servo2.top(w/2)], move="right")
        self.rectangularWall(w, l, "FFFF", callback=[
            None, None, lambda:self.servo2.bottom(w/2)], move="right")
        self.rectangularWall(w2, w, "ffff", callback=[
            lambda:self.servo.front(w2/2)], move="up")
        self.rectangularWall(w, w2, "ffff", callback=[
            lambda:self.servo2.front(w/2)], move="")

        self.move(tw, th, move)

class RobotArmUU(_RobotArm):
    """Robot arm segment with two parallel sets of hinge knuckles"""
    def __call__(self, length, move=None):
        t = self.thickness
        w = self.servo.hinge_width()
        l = max(4*self.thickness, length - 2*t - 2*self.servo.height)

        th = max(2 * self.servo._edges["m"].spacing() + l,
                 2*w + 4*t + self.spacing)
        tw = 5 * (w + 2*self.thickness + self.spacing)

        if self.move(tw, th, move, True):
            return

        iw = (0, 3, 4, 7)
        e = self.servo.edges
        self.rectangularWall(w, l, e("mFmF"), ignore_widths=iw, move="right")
        self.rectangularWall(w, l, e("MFMF"), ignore_widths=iw, move="right")
        self.rectangularWall(w, l, "FfFf", move="right")
        self.rectangularWall(w, l, "FfFf", move="right")
        self.rectangularWall(w, w, "ffff", callback=[
            lambda: self.hole(w/2, w/2, 6)], move="up")
        self.rectangularWall(w, w, "ffff", callback=[
            lambda: self.hole(w/2, w/2, 6)], move="")

        self.move(tw, th, move)

class RobotArmUu(_RobotArm):
    """Robot arm segment with two orthogonal sets of hinge knuckles"""
    def __call__(self, length, move=None):
        t = self.thickness
        w = self.servo.hinge_width()
        w2 = self.servo2.hinge_width()
        l = max(4*self.thickness, length - 2*t - 2*self.servo.height)

        th = max(self.thickness + self.servo._edges["m"].spacing() + l,
                 2*w + self.thickness + 4 * self.edges["f"].spacing())
        tw = 5 * (w + 2*self.thickness + self.spacing)

        if self.move(tw, th, move, True):
            return
        iw = (3, 4)
        e = self.servo.edges
        self.rectangularWall(w2, l, e("nfFf"), move="right")
        self.rectangularWall(w2, l, e("NfFf"), move="right")
        self.rectangularWall(w, l, e("FFmF"), ignore_widths=iw, move="right")
        self.rectangularWall(w, l, e("FFMF"), ignore_widths=iw, move="right")
        self.rectangularWall(w2, w, "ffff", callback=[
                        lambda: self.hole(w2/2, w/2, 6)], move="up")
        self.rectangularWall(w2, w, "ffff", callback=[
                        lambda: self.hole(w2/2, w/2, 6)], move="")

        self.move(tw, th, move)

class RobotArmMu(_RobotArm):
    """Robot arm segment with a servo and an orthogonal sets of hinge knuckles"""
    def __call__(self, length, move=None):
        t = self.thickness
        w = self.servo.height
        w2 = self.servo2.hinge_width()
        l = max(self.servo.length, length + self.servo.axle_pos - self.servo.height - t)

        th = max(t + l + self.servo2._edges["m"].spacing(),
                 w + w2 + self.thickness + 4 * self.edges["f"].spacing())
        tw = 5 * (w + 2*self.thickness + self.spacing)

        if self.move(tw, th, move, True):
            return

        e = self.servo2.edges
        iw = (3, 4)
        self.rectangularWall(w2, l, "FfFf", callback=[
            lambda:self.servo.top(w2/2)], move="right")
        self.rectangularWall(w2, l, "FfFf", callback=[
            lambda:self.servo.bottom(w2/2)], move="right")
        self.rectangularWall(w, l, e("FFmF"), ignore_widths=iw, move="right")
        self.rectangularWall(w, l, e("FFMF"), ignore_widths=iw, move="right")
        self.rectangularWall(w2, w, "ffff", callback=[
            lambda:self.servo.front(w2/2)], move="up")
        self.rectangularWall(w2, w, "ffff", callback=[
            lambda: self.hole(w2/2, w/2, 6)], move="")

        self.move(tw, th, move)

# class RobotArmMU(_RobotArm):
