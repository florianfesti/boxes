class Extents:
    __slots__ = "xmin ymin xmax ymax".split()

    def __init__(self,xmin=float('inf'),ymin=float('inf'),xmax=float('-inf'),ymax=float('-inf')):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def add(self,x,y):
        self.xmin = min(self.xmin,x)
        self.xmax = max(self.xmax,x)
        self.ymin = min(self.ymin,y)
        self.ymax = max(self.ymax,y)

    def extend(self,l):
        for x,y in l:
            self.add(x,y)

    def __add__(self,extent):
        #todo: why can this happen?
        if extent == 0:
            return Extents(self.xmin,self.ymin,self.xmax,self.ymax)
        return Extents(
            min(self.xmin,extent.xmin),min(self.ymin,extent.ymin),
            max(self.xmax,extent.xmax),max(self.ymax,extent.ymax)
        )

    def __radd__(self,extent):
        if extent == 0:
            return Extents(self.xmin,self.ymin,self.xmax,self.ymax)
        return self.__add__(extent)

    def get_width(self):
        return self.xmax-self.xmin

    def get_height(self):
        return self.ymax-self.ymin

    width = property(get_width)
    height = property(get_height)

    def __repr__(self):
        return f'Extents ({self.xmin},{self.ymin})-({self.xmax},{self.ymax})'
