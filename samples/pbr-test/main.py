import sys, os, math

sys.path.append("../../")

import moss, glm, ctypes
import pyglet.gl as gl

class App:
    def __init__(self):
        self.window = moss.Window("PBR Test", 1200, 600, moss.Color(0.0, 0.0, 0.0), False)
        self.window.event(self.setup)
        self.window.event(self.update)
        self.window.event(self.exit)

    def updateLights(self):
        self.shader.use()
        self.shader.setUniform1i("enableShadows", 0)
        self.shader.setUniform1i("lightCount", len(self.lights))

        for index, i in enumerate(self.lights):
            self.shader.setUniform3fv(f"lightPositions[{index}]", glm.value_ptr(i.position))
            self.shader.setUniform3fv(f"lightColors[{index}]", glm.value_ptr(i.color))
            self.shader.setUniform1fv(f"lightBrightnesses[{index}]", ctypes.c_float(i.brightness))

        self.shader.unuse()

    def setup(self, window):
        self.shader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
        )

        self.basicShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/basic.frag"))
        )

        brightness = 10.0

        self.lights = [
            moss.Light(None, glm.vec3(-10.0,  10.0, 10.0), brightness, glm.vec3(1.0, 1.0, 1.0), shader = self.basicShader),
        ]

        self.camera = moss.FPSCamera(
            self.shader, fov = 90, far = 10000
        )

        self.albedoMap = moss.Texture(self.shader, os.path.join(os.path.split(moss.__file__)[0], "res/rusted_iron/rusted_iron_basecolor.png"), 0)
        self.roughnessMap = moss.Texture(self.shader, os.path.join(os.path.split(moss.__file__)[0], "res/rusted_iron/rusted_iron_roughness.png"), 1)
        self.metallicMap = moss.Texture(self.shader, os.path.join(os.path.split(moss.__file__)[0], "res/rusted_iron/rusted_iron_metallic.png"), 2)
        self.normalMap = moss.Texture(self.shader, os.path.join(os.path.split(moss.__file__)[0], "res/rusted_iron/rusted_iron_normal.png"), 3)

    def update(self, window):
        self.window.clear()
        self.updateLights()
        self.camera.proccessInputs()

        for i in [self.shader, self.basicShader]:
            self.camera.shader = i
            self.camera.updateMatrices()

        useTexture = True

        self.shader.use()
        self.shader.setUniform1i("textureScale", 1)
        self.shader.setUniform1i("rotateTexture", 0)
        self.shader.setUniform1i("inverseNormal", 0)
        self.shader.setUniform1i("useAlbedoMap", 1 if useTexture else 0)
        self.shader.setUniform1i("useRoughnessMap", 1 if useTexture else 0)
        self.shader.setUniform1i("useMetallicMap", 1 if useTexture else 0)
        self.shader.setUniform1i("useNormalMap", 1 if useTexture else 0)
        self.shader.setUniform1i("useSpecularMap", 0)
        self.shader.setUniform1i("useAmbientMap", 0)
        self.shader.setUniform3fv("albedoDefault", glm.value_ptr(glm.vec3(1.0, 0.0, 0.0)))
        self.shader.setUniform1f("ambientDefault", 1.0)

        if useTexture:
            self.albedoMap.bind()
            self.albedoMap.texUnit("albedoMap")
            self.roughnessMap.bind()
            self.roughnessMap.texUnit("roughnessMap")
            self.metallicMap.bind()
            self.metallicMap.texUnit("metallicMap")
            self.normalMap.bind()
            self.normalMap.texUnit("normalMap")

        gl.glEnable(gl.GL_DEPTH_TEST)

        nrRows = 7
        nrColumns = 7
        spacing = 2.5
        row = 0

        while row < nrRows:
            self.shader.setUniform1f("metallicDefault", float(row) / float(nrRows))
            col = 0

            while col < nrColumns:
                self.shader.setUniform1f("roughnessDefault", glm.clamp(float(col) / float(nrColumns), 0.05, 1.0))
                model = glm.mat4(1.0)
                model = glm.translate(model, glm.vec3((col - (nrColumns / 2)) * spacing, (row - (nrRows / 2)) * spacing, 0.0))
                self.shader.setUniformMatrix4fv("model", moss.valptr(model))
                self.shader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
                moss.renderSphere()
                col += 1
            
            row += 1

        for i in self.lights:
            self.basicShader.use()
            self.basicShader.setUniform4fv("color", glm.value_ptr(glm.vec4(i.color, 1.0)))
            self.basicShader.unuse()
            i.render()

    def exit(self, window):
        for i in self.lights:
            i.delete()

        self.shader.delete()
        self.basicShader.delete()

    def run(self):
        moss.run()

def main(argv):
    app = App()
    app.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))