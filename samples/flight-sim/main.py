import sys

sys.path.append("../../")

import moss, os, glm, sys, ctypes, data, ai, imgui, random
import moss.physics as phi
import pyglet.gl as gl

from imgui.integrations.glfw import GlfwRenderer
from flight_model import Airplane, Airfoil, Wing, SimpleEngine

class Light(moss.Model):
    def __init__(self, shader, position, brightness, color):
        self.depthShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.frag")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.geom"))
        )

        self.lightShader = shader
    
        super().__init__(
            shader = self.lightShader,
            filePath = os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")
        )
    
        self.SHADOW_WIDTH = self.SHADOW_HEIGHT = 8192 * 2

        self.color = color
        self.brightness = brightness

        self.depthMapFBO = ctypes.c_uint32()
        gl.glGenFramebuffers(1, ctypes.byref(self.depthMapFBO))
        self.depthCubemap = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.depthCubemap))
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.depthCubemap)

        for i in range(6):
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_DEPTH_COMPONENT, self.SHADOW_WIDTH, self.SHADOW_HEIGHT, 0, gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, 0)

        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.depthMapFBO)
        gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, self.depthCubemap, 0)
        gl.glDrawBuffer(gl.GL_NONE)
        gl.glReadBuffer(gl.GL_NONE)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def begin(self):
        near_plane = 1.0
        far_plane = 1000.0
        shadowProj = glm.perspective(glm.radians(90.0), self.SHADOW_WIDTH / self.SHADOW_HEIGHT, near_plane, far_plane)
        shadowTransforms = []
        shadowTransforms.append(shadowProj * glm.lookAt(self.transform.position, self.transform.position + glm.vec3(1.0, 0.0, 0.0), glm.vec3(0.0, -1.0, 0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.transform.position, self.transform.position + glm.vec3(-1.0, 0.0, 0.0), glm.vec3(0.0, -1.0, 0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.transform.position, self.transform.position + glm.vec3(0.0, 1.0, 0.0), glm.vec3(0.0, 0.0, 1.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.transform.position, self.transform.position + glm.vec3(0.0, -1.0, 0.0), glm.vec3(0.0, 0.0, -1.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.transform.position, self.transform.position + glm.vec3(0.0, 0.0, 1.0), glm.vec3(0.0, -1.0, 0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.transform.position, self.transform.position + glm.vec3(0.0, 0.0, -1.0), glm.vec3(0.0, -1.0, 0.0)))

        gl.glViewport(0, 0, self.SHADOW_WIDTH, self.SHADOW_HEIGHT)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.depthMapFBO)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        self.depthShader.use()

        for i in range(6):
            self.depthShader.setUniformMatrix4fv(f"shadowMatrices[{i}]", glm.value_ptr(shadowTransforms[i]))

        self.depthShader.setUniform3fv("lightPosition", glm.value_ptr(self.transform.position))

        self.lightShader.use()
        self.lightShader.setUniform3fv("albedoDefault", glm.value_ptr(glm.vec3(1.0, 1.0, 1.0)))
        self.lightShader.unuse()

    def end(self):
        window = moss.context.getCurrentWindow()
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glViewport(0, 0, window.width, window.height)

    def update(self, shader):
        shader.use()
        gl.glActiveTexture(gl.GL_TEXTURE0 + 6)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.depthCubemap)
        shader.setUniform1i("depthMap", 6)
        shader.unuse()

# class Light(moss.Model):
#     def __init__(self, shader, position, brightness, color):
#         super().__init__(shader, "res/cube.obj")
#         self.transform.scaleVector = glm.vec3(1)
#         self.transform.position = position
#         self.brightness = brightness
#         self.color = color

class Falcon(Airplane, moss.Model):
    def __init__(self, shader, model):
        mass = 10000.0
        wing_offset = -1.0
        tail_offset = -6.6

        masses = [
            phi.cubeElement(glm.vec3(wing_offset,  0.0, -2.7), glm.vec3(6.96, 0.10, 3.50), mass * 0.25),
            phi.cubeElement(glm.vec3(wing_offset,  0.0,  2.7), glm.vec3(6.96, 0.10, 3.50), mass * 0.25),
            phi.cubeElement(glm.vec3(tail_offset, -0.1,  0.0), glm.vec3(6.54, 0.10, 2.70), mass * 0.10),
            phi.cubeElement(glm.vec3(tail_offset,  0.0,  0.0), glm.vec3(5.31, 3.10, 0.10), mass * 0.10),
            phi.cubeElement(glm.vec3(0.0, 0.0, 0.0), glm.vec3(8.0, 2.0, 2.0), mass * 0.5)
        ]

        NACA_0012 = Airfoil(data.NACA_0012_data)
        NACA_2412 = Airfoil(data.NACA_2412_data)

        wings = [
            Wing(glm.vec3(wing_offset,  0.0, -2.7), 6.96, NACA_2412, chord = 2.50),
            Wing(glm.vec3(wing_offset - 1.5,  0.0, -2.0), 3.80, NACA_0012, chord = 1.26),
            Wing(glm.vec3(wing_offset - 1.5,  0.0,  2.0), 3.80, NACA_0012, chord = 1.26),
            Wing(glm.vec3(wing_offset,  0.0,  2.7), 6.96, NACA_2412, chord = 2.50),
            Wing(glm.vec3(tail_offset, -0.1,  0.0), 6.54, NACA_0012, chord = 2.70),
            Wing(glm.vec3(tail_offset,  0.0,  0.0), 5.31, NACA_0012, chord = 3.10, normal = phi.right)
        ]

        Airplane.__init__(self, mass, phi.tensorElement(masses, True), wings, SimpleEngine(thrust = 50000.0 * 3))
        moss.Model.__init__(self, shader, meshes = model[0], materials = model[1])

        self.transform.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.transform.scaleVector = glm.vec3(1.0)

class PrivateJet(Airplane, moss.Model):
    def __init__(self, shader, model):
        mass = 10000.0
        wing_offset = -1.0
        tail_offset = -6.6

        masses = [
            phi.cubeElement(glm.vec3(wing_offset,  0.0, -2.7), glm.vec3(6.96, 0.10, 3.50), mass * 0.25),
            phi.cubeElement(glm.vec3(wing_offset,  0.0,  2.7), glm.vec3(6.96, 0.10, 3.50), mass * 0.25),
            phi.cubeElement(glm.vec3(tail_offset, -0.1,  0.0), glm.vec3(6.54, 0.10, 2.70), mass * 0.10),
            phi.cubeElement(glm.vec3(tail_offset,  0.0,  0.0), glm.vec3(5.31, 3.10, 0.10), mass * 0.10),
            phi.cubeElement(glm.vec3(0.0, 0.0, 0.0), glm.vec3(8.0, 2.0, 2.0), mass * 0.5)
        ]

        NACA_0012 = Airfoil(data.NACA_0012_data)
        NACA_2412 = Airfoil(data.NACA_2412_data)

        wings = [
            Wing(glm.vec3(wing_offset,  0.0, -2.7), 6.96, NACA_2412, chord = 2.50),
            Wing(glm.vec3(wing_offset - 1.5,  0.0, -2.0), 3.80, NACA_0012, chord = 1.26),
            Wing(glm.vec3(wing_offset - 1.5,  0.0,  2.0), 3.80, NACA_0012, chord = 1.26),
            Wing(glm.vec3(wing_offset,  0.0,  2.7), 6.96, NACA_2412, chord = 2.50),
            Wing(glm.vec3(tail_offset, -0.1,  0.0), 6.54, NACA_0012, chord = 2.70),
            Wing(glm.vec3(tail_offset,  0.0,  0.0), 5.31, NACA_0012, chord = 3.10, normal = phi.right)
        ]

        Airplane.__init__(self, mass, phi.tensorElement(masses, True), wings, SimpleEngine(thrust = 50000.0 * 2))
        moss.Model.__init__(self, shader, meshes = model[0], materials = model[1])

        self.transform.rotation = glm.vec3(0.0, 180.0, 0.0)
        self.transform.scaleVector = glm.vec3(5.0)

class App:
    def __init__(self):
        self.window = moss.Window("Flight Simulator", 1200, 600, moss.Color(0.0, 0.0, 0.0), False)
        self.window.event(self.setup)
        self.window.event(self.update)
        self.window.event(self.exit)

    def updateLights(self):
        self.shader.use()
        self.shader.setUniform1i("enableShadows", 1)
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

        self.basicShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/basic.frag"))
        )

        self.lights = [
            Light(self.basicShader, glm.vec3(0.0, 0.0, 0.0), 1000.0, glm.vec3(1.0, 1.0, 1.0))
        ]

        self.tpsCamera = moss.TPSCamera(
            self.shader, fov = 130, far = 10000
        )

        self.camera = moss.Camera(
            self.shader, fov = 130, far = 10000
        )

        self.tpsCameraEnabled = False

        self.ground = moss.Model(
            self.shader, os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")
        )

        scale = 10000.0

        self.ground.transform.scale(glm.vec3(scale, 1.0, scale))

        falconModel = moss.loadOBJ(self.shader, "res/falcon.obj")
        privateJetModel = moss.loadOBJ(self.shader, "res/jet.obj")

        self.airplane = Falcon(self.shader, falconModel)
        self.airplane.engine.throttle = 1.0
        self.airplane.position = glm.vec3(0.0, 100.0, 0.0)
        self.airplane.velocity = glm.vec3(phi.metersPerSecond(500.0), 0.0, 0.0)

        for i in self.airplane.meshes:
            for j in self.airplane.meshes[i].submeshes:
                self.airplane.meshes[i].submeshes[j]["cullFace"] = False

        self.npcs = []
        self.npcCount = 0

        for i in range(self.npcCount):
            npc = Falcon(self.shader, falconModel)
            npc.position = glm.vec3(0.0, 50.0, random.randint(-300, 300))
            npc.velocity = glm.vec3(phi.metersPerSecond(500.0), 0.0, 0.0)
            self.npcs.append(npc)

        imgui.create_context()
        self.impl = GlfwRenderer(self.window.window)
        self.flightTime = 0.0

        self.move = lambda value, factor: glm.clamp(value - factor * self.window.deltaTime, -1.0, 1.0)
        self.center = lambda value, factor: glm.clamp(value - factor * self.window.deltaTime, 0.0, 1.0) if value >= 0 else glm.clamp(value + factor * self.window.deltaTime, -1.0, 0.0)
        self.factor = glm.vec3(3.0, 0.5, 1.0)
        self.aileron = 0.0
        self.rudder = 0.0
        self.elevator = 0.0
        self.trim = 0.0

        self.camera.position = glm.vec3(0.0)
        self.camera.rotation = glm.quat(1.0, 0.0, 0.0, 0.0)
        self.state = True

    def update(self, window):
        self.ground.materials[None].albedo = glm.vec3(1.0)
        self.camera.fov = glm.clamp(phi.kilometersPerHour(self.airplane.getSpeed()) / 10, 90, 110)

        if self.window.input.getKey(moss.KEY_A): self.aileron = self.move(self.aileron, self.factor.x)
        elif self.window.input.getKey(moss.KEY_D): self.aileron = self.move(self.aileron, -self.factor.x)
        else: self.aileron = self.center(self.aileron, self.factor.x)

        if self.window.input.getKey(moss.KEY_W): self.elevator = self.move(self.elevator, self.factor.z)
        elif self.window.input.getKey(moss.KEY_S): self.elevator = self.move(self.elevator, -self.factor.z)
        else: self.elevator = self.center(self.elevator, self.factor.z)

        if self.window.input.getKey(moss.KEY_Q): self.rudder = self.move(self.rudder, self.factor.x)
        elif self.window.input.getKey(moss.KEY_E): self.rudder = self.move(self.rudder, -self.factor.x)
        else: self.rudder = self.center(self.rudder, self.factor.z)

        if self.window.input.getKey(moss.KEY_C): self.tpsCamera.radius += 0.01
        if self.window.input.getKey(moss.KEY_V): self.tpsCamera.radius -= 0.01

        if self.window.input.getKey(moss.KEY_K): self.airplane.engine.throttle = glm.clamp(self.airplane.engine.throttle + 0.001, 0.0, 1.0)
        if self.window.input.getKey(moss.KEY_J): self.airplane.engine.throttle = glm.clamp(self.airplane.engine.throttle - 0.001, 0.0, 1.0)

        if self.window.input.getKey(moss.KEY_O):
            if self.state:
                self.tpsCameraEnabled = not self.tpsCameraEnabled
                self.state = False

        else:
            self.state = True

        self.flightTime += self.window.deltaTime
        self.airplane.control = glm.vec4(self.aileron, self.rudder, self.elevator, self.trim)
        self.airplane.update(self.window.deltaTime)

        for npc in self.npcs:
            npc.engine.throttle = self.airplane.engine.throttle
            ai.follow(npc, self.airplane.position)
            npc.update(self.window.deltaTime)

        if self.tpsCameraEnabled:
            self.tpsCamera.center = self.airplane.position
            self.tpsCamera.proccessInputs()

        else:
            self.camera.position = glm.mix(self.camera.position, self.airplane.position + self.airplane.up() * 4.5 + self.airplane.forward() * 13.0, self.window.deltaTime * 0.035 * self.airplane.getSpeed())
            self.camera.rotation = glm.mix(self.camera.rotation, self.airplane.orientation * glm.quat(glm.vec3(0.0, glm.radians(-90.0), 0.0)), self.window.deltaTime * 5.0)
            self.camera.view = glm.inverse(glm.translate(glm.mat4(1.0), self.camera.position) * glm.mat4(self.camera.rotation) * glm.scale(glm.mat4(1.0), glm.vec3(1.0)))

        self.airplane.transform.matrix = glm.translate(glm.mat4(1.0), self.airplane.position) * glm.mat4(self.airplane.orientation) \
            * glm.scale(glm.mat4(1.0), self.airplane.transform.scaleVector) * glm.rotate(glm.mat4(1.0), glm.radians(self.airplane.transform.rotation.y), glm.vec3(0.0, 1.0, 0.0))

        for npc in self.npcs:
            npc.transform.matrix = glm.translate(glm.mat4(1.0), npc.position) * glm.mat4(npc.orientation)

        self.window.clear()
        self.updateLights()

        for i in [self.shader, self.basicShader]:
            for camera in [self.tpsCamera] if self.tpsCameraEnabled else [self.camera]:
                camera.shader = i
                camera.updateMatrices()

        self.lights[0].transform.position = self.airplane.position + glm.vec3(0.0, 50.0, 0.0)
        self.lights[0].begin()

        for i in [self.airplane] + self.npcs:
            for j in i.meshes:
                i.meshes[j].shader = self.lights[0].depthShader

            i.render(useTexture = False)

            for j in i.meshes:
                i.meshes[j].shader = self.shader

        self.lights[0].end()
        self.lights[0].update(self.shader)

        for i in range(2):
            self.shader.use()
            self.shader.setUniform1i("enableShadows", i)
            self.shader.unuse()

            if i == 0:
                for i in [self.airplane] + self.npcs:
                    i.render()

            else:
                self.ground.render()

        self.impl.process_inputs()
        imgui.new_frame()

        imgui.set_next_window_position(10, 10)
        imgui.set_next_window_size(145, 170)
        imgui.set_next_window_bg_alpha(0.35)
        imgui.begin("Flight Simulator", None, imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)
        imgui.text(f"ALT:   {str(self.airplane.getAltitude())[:7]} m")
        imgui.text(f"SPD:   {str(phi.kilometersPerHour(self.airplane.getSpeed()))[:7]} km/h")
        imgui.text(f"IAS:   {str(phi.kilometersPerHour(self.airplane.getIAS()))[:7]} km/h")
        imgui.text(f"MCH:   {self.airplane.getMach()}")
        imgui.text(f"G:     {self.airplane.getG()}")
        imgui.text(f"AoA:   {self.airplane.getAoA()}")
        imgui.text(f"THR:   {self.airplane.engine.throttle * 100.0} %")
        imgui.text(f"Trim:  {self.trim}")
        imgui.text(f"FPS:   {self.window.framesPerSecond} - {int(1 / self.window.deltaTime)}")
        imgui.end()

        imgui.set_next_window_position(self.window.width - 140.0 - 10.0, self.window.height - 135.0 - 10.0)
        imgui.set_next_window_size(140, 135)
        imgui.set_next_window_bg_alpha(0.35)
        imgui.begin("Debug", None, imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)
        imgui.text(f"Time:       {self.flightTime}")
        imgui.text(f"Roll Rate:  {glm.degrees(self.airplane.angularVelocity).x}")
        imgui.text(f"Yaw Rate:   {glm.degrees(self.airplane.angularVelocity).y}")
        imgui.text(f"Pitch Rate: {glm.degrees(self.airplane.angularVelocity).z}")
        imgui.text(f"Roll:       {glm.degrees(self.airplane.getEulerAngles()).x}")
        imgui.text(f"Yaw:        {glm.degrees(self.airplane.getEulerAngles()).y}")
        imgui.text(f"Pitch:      {glm.degrees(self.airplane.getEulerAngles()).z}")
        imgui.end()

        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def exit(self, window):
        self.airplane.delete()

        for npc in self.npcs:
            npc.delete()

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