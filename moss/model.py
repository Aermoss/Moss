import moss

class Model:
    def __init__(self, shader, filePath = None, meshes = {}, materials = {}):
        self.shader = shader
        self.transform = moss.Transform()
        self.deleteMaterials = False

        if filePath != None:
            self.deleteMaterials = True

            meshes, self.materials = \
                moss.loadOBJ(shader, filePath)

        else:
            self.materials = materials

        self.meshes = {}

        for i in meshes:
            self.meshes[i] = moss.Mesh(self.shader, meshes[i], self.materials, self.transform)

    def render(self, useTexture = True):
        for i in self.meshes:
            self.meshes[i].render(useTexture)

    def delete(self):
        if self.deleteMaterials:
            for i in self.materials:
                self.materials[i].delete()
                
        for i in self.meshes:
            self.meshes[i].delete()