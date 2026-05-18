class ScanCapture:
    def __init__(self, lasers=2):
        self.theta = 0
        self.texture = None
        self.lasers = [None] * (lasers + 1)
        self.depth = None
        self.depth_scale = 1.0
