import moss

class Color:
    def __init__(self, r, g, b, a = 255):
        self.r, self.g, self.b, self.a = r, g, b, a

    def get(self):
        return self.r / 255, self.g / 255, self.b / 255, self.a / 255