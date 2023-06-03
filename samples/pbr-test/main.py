import sys, os, math

sys.path.append("../../")

import moss, glm, ctypes
import pyglet.gl as gl

class Light(moss.Model):
    def __init__(self, shader, position, brightness, color):
        super().__init__(shader, os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj"))
        self.transform.scaleVector = glm.vec3(1)
        self.transform.position = position
        self.brightness = brightness
        self.color = color

sphereVao = None
indexCount = None

def renderSphere():
    global sphereVao, indexCount

    if sphereVao == None:
        sphereVao = moss.VAO()
        vbo = moss.VBO()
        ibo = moss.IBO()

        positions = []
        uv = []
        normals = []
        indices = []

        X_SEGMENTS = 64
        Y_SEGMENTS = 64

        x = 0

        while x <= X_SEGMENTS:
            y = 0

            while y <= Y_SEGMENTS:
                xSegment = float(x) / float(X_SEGMENTS);
                ySegment = float(y) / float(Y_SEGMENTS);
                xPos = math.cos(xSegment * 2.0 * math.pi) * math.sin(ySegment * math.pi);
                yPos = math.cos(ySegment * math.pi);
                zPos = math.sin(xSegment * 2.0 * math.pi) * math.sin(ySegment * math.pi);

                positions.append(glm.vec3(xPos, yPos, zPos))
                uv.append(glm.vec2(xSegment, ySegment))
                normals.append(glm.vec3(xPos, yPos, zPos))

                y += 1

            x += 1

        oddRow = False
        
        for y in range(Y_SEGMENTS):
            if not oddRow:
                x = 0

                while x <= X_SEGMENTS:
                    indices.append(y       * (X_SEGMENTS + 1) + x)
                    indices.append((y + 1) * (X_SEGMENTS + 1) + x)
                    x += 1

            else:
                x = X_SEGMENTS

                while x >= 0:
                    indices.append((y + 1) * (X_SEGMENTS + 1) + x)
                    indices.append(y       * (X_SEGMENTS + 1) + x)
                    x -= 1

            oddRow = not oddRow

        indexCount = len(indices)

        data = []

        for i in range(len(positions)):
            data.append(positions[i].x)
            data.append(positions[i].y)
            data.append(positions[i].z)

            if len(uv) > 0:
                data.append(uv[i].x)
                data.append(uv[i].y)

            if len(normals) > 0:
                data.append(normals[i].x)
                data.append(normals[i].y)
                data.append(normals[i].z)

        data = moss.mkarr(ctypes.c_float, data)
        indices = moss.mkarr(ctypes.c_uint32, indices)

        sphereVao.bind()
        vbo.bind()
        vbo.bufferData(ctypes.sizeof(data), data)
        ibo.bind()
        ibo.bufferData(ctypes.sizeof(indices), indices)
        stride = (3 + 2 + 3) * 4
        sphereVao.enableAttrib(0, 3, stride, 0 * 4)
        sphereVao.enableAttrib(1, 2, stride, 3 * 4)
        sphereVao.enableAttrib(2, 3, stride, 5 * 4)

    sphereVao.bind()
    gl.glDrawElements(gl.GL_TRIANGLE_STRIP, indexCount, gl.GL_UNSIGNED_INT, 0)

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
            self.shader.setUniform3fv(f"lightPositions[{index}]", glm.value_ptr(i.transform.position))
            self.shader.setUniform3fv(f"lightColors[{index}]", glm.value_ptr(i.color))
            self.shader.setUniform1fv(f"lightBrightnesses[{index}]", ctypes.c_float(i.brightness))

        self.shader.unuse()

    def setup(self, window):
        self.shader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
        )

        self.lightShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.frag"))
        )

        brightness = 10.0

        self.lights = [
            Light(self.lightShader, glm.vec3(-10.0,  10.0, 10.0), brightness, glm.vec3(1.0, 1.0, 1.0)),
        ]

        self.camera = moss.FPSCamera(
            self.shader, fov = 90, far = 10000
        )

        self.albedoMap = moss.Texture(self.shader, "res/rustediron/rustediron2_basecolor.png", 0)
        self.roughnessMap = moss.Texture(self.shader, "res/rustediron/rustediron2_roughness.png", 1)
        self.metallicMap = moss.Texture(self.shader, "res/rustediron/rustediron2_metallic.png", 2)
        self.normalMap = moss.Texture(self.shader, "res/rustediron/rustediron2_normal.png", 3)

    def update(self, window):
        self.window.clear()
        self.updateLights()
        self.camera.proccessInputs()

        for i in [self.shader, self.lightShader]:
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
                renderSphere()
                col += 1
            
            row += 1

        for i in self.lights:
            self.lightShader.use()
            self.lightShader.setUniform4fv("color", glm.value_ptr(glm.vec4(i.color, 1.0)))
            self.lightShader.unuse()
            i.render()

    def exit(self, window):
        for i in self.lights:
            i.delete()

        self.shader.delete()
        self.lightShader.delete()

    def run(self):
        moss.run()

def main(argv):
    app = App()
    app.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))