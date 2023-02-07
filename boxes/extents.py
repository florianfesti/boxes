class Extents:
    __slots__ = "xmin ymin xmax ymax".split()

    def __init__(self, xmin: float = float('inf'), ymin: float = float('inf'), xmax: float = float('-inf'), ymax: float = float('-inf')) -> None:
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def add(self, x: float, y: float) -> None:
        self.xmin = min(self.xmin, x)
        self.xmax = max(self.xmax, x)
        self.ymin = min(self.ymin, y)
        self.ymax = max(self.ymax, y)

    def extend(self, l) -> None:
        for x, y in l:
            self.add(x, y)

    def __add__(self, extent):
        # todo: why can this happen?
        if extent == 0:
            return Extents(self.xmin, self.ymin, self.xmax, self.ymax)
        return Extents(
            min(self.xmin, extent.xmin), min(self.ymin, extent.ymin),
            max(self.xmax, extent.xmax), max(self.ymax, extent.ymax)
        )

    def __radd__(self, extent):
        if extent == 0:
            return Extents(self.xmin, self.ymin, self.xmax, self.ymax)
        return self.__add__(extent)

    @property
    def width(self) -> float:
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        return self.ymax - self.ymin

    def __repr__(self) -> str:
        return f'Extents ({self.xmin},{self.ymin})-({self.xmax},{self.ymax})'
