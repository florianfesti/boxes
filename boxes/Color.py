class Color:
    BLACK   = [ 0.0, 0.0, 0.0 ]
    BLUE    = [ 0.0, 0.0, 1.0 ]
    GREEN   = [ 0.0, 1.0, 0.0 ]
    RED     = [ 1.0, 0.0, 0.0 ]
    CYAN    = [ 0.0, 1.0, 1.0 ]
    YELLOW  = [ 1.0, 1.0, 0.0 ]
    MAGENTA = [ 1.0, 0.0, 1.0 ]
    WHITE   = [ 1.0, 1.0, 1.0 ]

    # TODO: Make this configurable
    OUTER_CUT = BLACK
    INNER_CUT = BLUE
    ANNOTATIONS = RED
    ETCHING = GREEN
    ETCHING_DEEP = CYAN
    CUT = [  # Even steps from INNER_CUT to OUTER_CUT
        [0.0, 0.0, 1.0 - i/4.0] for i in range(5)
    ]
