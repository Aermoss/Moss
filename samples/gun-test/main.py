import sys, os, math

sys.path.append("../../")

import moss, glm, time, ctypes
import pyglet.gl as gl

class Gun(moss.Model):
    def __init__(self, shader, camera, mixer):
        super().__init__(
            shader = shader,
            filePath = os.path.join(os.path.split(moss.__file__)[0], "res/ak-12.obj")
        )

        self.camera = camera
        self.mixer = mixer
        self.sound = self.mixer.load(os.path.join(os.path.split(moss.__file__)[0], "res/ak-12.mp3"))

        self.meshes["bolt_carrier_Circle.004"].transform = moss.Transform()
        self.bolt_carrier = self.meshes["bolt_carrier_Circle.004"].transform

        self.bolt_carrier.scale(glm.vec3(0.2, 0.2, 0.2))
        self.transform.scale(glm.vec3(0.2, 0.2, 0.2))

        self.last = 0
        self.gun_pos = glm.vec3(0.05, -0.02, -0.05)
        self.gun_std_pos = glm.vec3(0.05, -0.02, -0.05)
        self.bolt_carrier_pos = glm.vec3(0.0, 0.0, 0.0)
        self.rot_t = 0.1
        self.pos_t = 0.1
        self.rpm = 600

    def update(self):
        self.gun_pos = glm.lerp(self.gun_pos, self.gun_std_pos, self.pos_t)
        self.transform.position = self.camera.position + self.gun_pos

        self.transform.pivotx = self.transform.position
        self.transform.pivoty = self.camera.position
        self.transform.pivotz = self.camera.position
        self.transform.rotation.y = glm.lerp(self.transform.rotation.y, -self.camera.yaw - 90, 0.2)

        self.bolt_carrier_pos = glm.lerp(self.bolt_carrier_pos, glm.vec3(0.0, 0.0, 0.0), 0.2)
        self.bolt_carrier.position = self.transform.position + self.bolt_carrier_pos
        self.bolt_carrier.rotation = self.transform.rotation
        self.bolt_carrier.pivotx = self.transform.pivotx
        self.bolt_carrier.pivoty = self.transform.pivoty
        self.bolt_carrier.pivotz = self.transform.pivotz

        if window.input.getMouseButton(moss.glfw.MOUSE_BUTTON_LEFT) \
            and self.last + 1 / (self.rpm / 60) < time.time():
                self.mixer.play(self.sound)
                self.last = time.time()
                self.bolt_carrier_pos = glm.vec3(0.0, 0.0, 0.03)

                if self.gun_std_pos.x == 0.0:
                    self.gun_pos = self.gun_std_pos + glm.vec3(0.0, 0.0, 0.002)

                else:
                    self.gun_pos = self.gun_std_pos + glm.vec3(0.0, 0.01, 0.03)

        if window.input.getKey(moss.glfw.KEY_E):
            self.gun_std_pos = glm.vec3(-0.02, -0.02, -0.03)
            self.transform.rotation.z = glm.lerp(self.transform.rotation.z, 45.0, self.rot_t)

        elif window.input.getMouseButton(moss.glfw.MOUSE_BUTTON_RIGHT):
            self.gun_std_pos = glm.vec3(0.00, -0.012, -0.05)
            self.transform.rotation.z = glm.lerp(self.transform.rotation.z, 0.0, self.rot_t)

        else:
            self.gun_std_pos = glm.vec3(0.05, -0.02, -0.05)
            self.transform.rotation.z = glm.lerp(self.transform.rotation.z, 0.0, self.rot_t)

def setup(window):
    global shader, camera, gun, model, mixer, light, lightShader

    shader = moss.Shader(
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
    )

    camera = moss.FPSCamera(shader)
    mixer = moss.Mixer()

    gun = Gun(shader, camera, mixer)

    lightShader = moss.Shader(
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/basic.frag"))
    )

    light = moss.Model(
        shader = lightShader,
        filePath = os.path.join(os.path.split(moss.__file__)[0], "res/sphere.obj")
    )

    model = moss.Model(
        shader = shader,
        filePath = os.path.join(os.path.split(moss.__file__)[0], "res/deagle.obj")
    )

    light.transform.position = glm.vec3(35, 35, -10)
    light.transform.scaleVector = glm.vec3(10, 10, 10)
    model.transform.translate(glm.vec3(1.0, 0.0, 0.0))

def update(window):
    global shader, lightShader, state

    camera.proccessInputs()
    gun.update()

    if window.input.getKey(moss.glfw.KEY_R):
        if state:
            start = time.time()
            lightShader.delete()
            shader.delete()

            shader = moss.Shader(
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
            )

            lightShader = moss.Shader(
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.vert")),
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.frag"))
            )

            model.shader = shader
            light.shader = lightShader
            state = False
            print(f"shaders are reloaded in: {time.time() - start}")

    else:
        state = True

    model.transform.pivotx = model.transform.position
    model.transform.pivoty = model.transform.position
    model.transform.pivotz = model.transform.position
    model.transform.rotate(glm.vec3(0.05, 0.1, 0.02))

    window.clear()

    for i in [shader, lightShader]:
        camera.shader = i
        camera.updateMatrices()

    shader.use()
    shader.setUniform1i("enableShadows", 0)
    shader.setUniform1i("lightCount", 1)

    for i in range(1):
        shader.setUniform3fv(f"lightPositions[{i}]", glm.value_ptr(light.transform.position))
        shader.setUniform3fv(f"lightColors[{i}]", glm.value_ptr(glm.vec3(1.0, 1.0, 1.0)))
        shader.setUniform1fv(f"lightBrightnesses[{i}]", ctypes.c_float(1000.0))

    shader.unuse()

    lightShader.use()
    lightShader.setUniform3fv("albedoDefault", glm.value_ptr(glm.vec3(1.0, 1.0, 1.0)))
    lightShader.unuse()

    gun.render()
    model.render()
    light.render()

def exit(window):
    model.delete()
    shader.delete()
    lightShader.delete()

def main(argv):
    global window, popup
    window = moss.Window("Gun Test", 1920, 1080, moss.Color(0, 0, 0), True, 16)
    window.event(setup)
    window.event(update)
    window.event(exit)
    moss.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))