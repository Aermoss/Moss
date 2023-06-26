import sys, os, math, random, aerforge

sys.path.append("../../")

import moss, glm, ctypes, glfw
import pyglet.gl as gl

class App:
    def __init__(self):
        self.window = moss.Window(
            title = "IBL Test",
            width = moss.context.displayWidth,
            height = moss.context.displayHeight,
            backgroundColor = moss.Color(0.0, 0.0, 0.0),
            fullscreen = False, samples = 16
        )
        
        self.window.event(self.setup)
        self.window.event(self.update)
        self.window.event(self.exit)

    def setup(self, window):
        self.basicShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/basic.frag")),
            vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert"),
            fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/basic.frag")
        )

        self.renderer = moss.Renderer(self.window)
        self.renderer.loadHDRTexture(random.choice([os.path.join(os.path.split(moss.__file__)[0], f"res/hdr_textures/{i}") for i in os.listdir(os.path.join(os.path.split(moss.__file__)[0], "res/hdr_textures"))]))

        self.camera = moss.FPSCamera(
            self.renderer.shader, fov = 90, far = 1000
        )

        brightness = 10.0

        self.renderer.lights = [
            moss.Light(self.renderer, glm.vec3(-10.0,  10.0, 10.0), brightness, glm.vec3(1.0, 1.0, 1.0)),
            # Light(self.renderer, glm.vec3( 10.0,  10.0, 10.0), brightness, glm.vec3(1.0, 1.0, 1.0)),
            # Light(self.renderer, glm.vec3( 10.0, -10.0, 10.0), brightness, glm.vec3(1.0, 1.0, 1.0)),
            # Light(self.renderer, glm.vec3(-10.0, -10.0, 10.0), brightness, glm.vec3(1.0, 1.0, 1.0))
        ]

        self.textures = {}

        for texture in ["gold_scuffed", "copper_scuffed", "aluminum_Scuffed", "iron_scuffed", "titanium_scuffed"]:
            self.textures[texture] = {
                "albedoMap": moss.Texture(self.renderer.shader, os.path.join(os.path.split(moss.__file__)[0], f"res/{texture}/{texture}_basecolor.png"), 0),
                "roughnessMap": moss.Texture(self.renderer.shader, os.path.join(os.path.split(moss.__file__)[0], f"res/{texture}/{texture}_roughness.png"), 1),
                "metallicMap": moss.Texture(self.renderer.shader, os.path.join(os.path.split(moss.__file__)[0], f"res/{texture}/{texture}_metallic.png"), 2),
                "normalMap": moss.Texture(self.renderer.shader, os.path.join(os.path.split(moss.__file__)[0], f"res/{texture}/{texture}_normal.png"), 3)
            }

        self.model = moss.Model(
            shader = self.renderer.shader,
            filePath = os.path.join(os.path.split(moss.__file__)[0], "res/deagle.obj")
        )

        self.ground = moss.Model(
            shader = self.renderer.shader,
            filePath = os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")
        )

    def update(self, window):
        self.window.clear()
        self.renderer.updateLights()
        self.camera.proccessInputs()
        self.renderer.renderBackground()
        self.renderer.bindTextures()
        self.renderer.showLights = True

        self.renderer.shader.use()
        self.renderer.shader.setUniform1i("textureScale", 1)
        self.renderer.shader.setUniform1i("rotateTexture", 0)
        self.renderer.shader.setUniform1i("inverseNormal", 0)
        self.renderer.shader.setUniform1i("useAlbedoMap", 1)
        self.renderer.shader.setUniform1i("useRoughnessMap", 1)
        self.renderer.shader.setUniform1i("useMetallicMap", 1)
        self.renderer.shader.setUniform1i("useNormalMap", 1)
        self.renderer.shader.setUniform1i("useSpecularMap", 0)
        self.renderer.shader.setUniform1i("useAmbientMap", 0)
        self.renderer.shader.setUniform1f("ambientDefault", 1.0)
        
        model = glm.translate(glm.mat4(1.0), glm.vec3(-2.5 * len(self.textures) / 2 - 1.25, 0.0, 0.0))

        for texture in self.textures:
            self.textures[texture]["albedoMap"].bind()
            self.textures[texture]["albedoMap"].texUnit("albedoMap")
            self.textures[texture]["roughnessMap"].bind()
            self.textures[texture]["roughnessMap"].texUnit("roughnessMap")
            self.textures[texture]["metallicMap"].bind()
            self.textures[texture]["metallicMap"].texUnit("metallicMap")
            self.textures[texture]["normalMap"].bind()
            self.textures[texture]["normalMap"].texUnit("normalMap")

            model = glm.translate(model, glm.vec3(2.5, 0.0, 0.0))
            self.renderer.shader.setUniformMatrix4fv("model", moss.valptr(model))
            self.renderer.shader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
            moss.renderSphere()

        self.model.transform.position = glm.vec3(0.0, 0.0, 10.0)
        self.model.transform.scaleVector = glm.vec3(5.0)
        self.model.transform.pivotx = self.model.transform.position
        self.model.transform.pivoty = self.model.transform.position
        self.model.transform.pivotz = self.model.transform.position
        self.model.transform.rotation = glm.vec3(35.0, 35.0, 0.0)
        self.ground.transform.position = glm.vec3(0.0, -12.0, 0.0)
        self.ground.transform.scaleVector = glm.vec3(100.0, 1.0, 100.0)
        self.renderer.submit(self.ground)
        self.renderer.submit(self.model)
        self.renderer.render(self.camera, renderBackground = False)

    def exit(self, window):
        self.ground.delete()
        self.model.delete()
        self.renderer.delete()

    def run(self):
        moss.run()

def main(argv):
    app = App()
    app.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))