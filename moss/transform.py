import moss, glm, ctypes
import pyglet.gl as gl

class Transform:
    def __init__(self):
        self.scaleVector = glm.vec3(1, 1, 1)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.pivotx = glm.vec3(0.0, 0.0, 0.0)
        self.pivoty = glm.vec3(0.0, 0.0, 0.0)
        self.pivotz = glm.vec3(0.0, 0.0, 0.0)
        self.matrix = glm.mat4(1.0)

    def translate(self, position):
        self.position += position

    def rotate(self, rotation):
        self.rotation += rotation

    def scale(self, scale):
        self.scaleVector *= scale

    def get(self):
        matrix = self.matrix
        matrix = glm.translate(matrix, self.pivotx)
        matrix = glm.rotate(matrix, glm.radians(self.rotation.x), glm.vec3(1.0, 0.0, 0.0))
        matrix = glm.translate(matrix, -self.pivotx)
        matrix = glm.translate(matrix, self.pivoty)
        matrix = glm.rotate(matrix, glm.radians(self.rotation.y), glm.vec3(0.0, 1.0, 0.0))
        matrix = glm.translate(matrix, -self.pivoty)
        matrix = glm.translate(matrix, self.pivotz)
        matrix = glm.rotate(matrix, glm.radians(self.rotation.z), glm.vec3(0.0, 0.0, 1.0))
        matrix = glm.translate(matrix, -self.pivotz)
        matrix = glm.translate(matrix, self.position)
        matrix = glm.scale(matrix, self.scaleVector)
        return matrix