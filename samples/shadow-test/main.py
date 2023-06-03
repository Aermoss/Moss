import sys, os, math

sys.path.append("../../")

import moss, glm, time, ctypes

import pyglet.gl as gl

class Light(moss.Model):
    def __init__(self):
        self.depthShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.frag")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.geom"))
        )

        self.lightShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.frag"))
        )
    
        super().__init__(
            shader = self.lightShader,
            filePath = os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")
        )
    
        self.SHADOW_WIDTH, self.SHADOW_HEIGHT = 1024, 1024

        self.color = glm.vec3(1.0, 1.0, 1.0)
        self.brightness = 1.0

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
        far_plane = 100.0
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
        self.lightShader.setUniform4fv("color", glm.value_ptr(glm.vec4(1.0, 1.0, 1.0, 1.0)))
        self.lightShader.unuse()

    def end(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glViewport(0, 0, window.width, window.height)

    def update(self):
        shader.use()
        gl.glActiveTexture(gl.GL_TEXTURE0 + 6)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.depthCubemap)
        shader.setUniform1i("depthMap", 6)
        shader.unuse()

def setup(window):
    global shader, camera, model, light, light2, state

    shader = moss.Shader(
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
    )

    camera = moss.FPSCamera(shader, position = glm.vec3(-5.0, 12.0, 5.0))
    light = Light()

    light.transform.position = glm.vec3(-1.5, 10.0, 1.5)
    light.transform.scaleVector = glm.vec3(0.1, 0.1, 0.1)

    model = moss.Model(
        shader = shader,
        filePath = os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")
    )

    state = True

def update(window):
    global shader, lightShader, state

    if window.input.getKey(moss.glfw.KEY_R):
        if state:
            start = time.time()
            shader.delete()

            shader = moss.Shader(
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
            )
            
            model.shader = shader
            state = False
            print(f"shaders are reloaded in: {time.time() - start}")

    else:
        state = True

    light.begin()

    for mesh in model.meshes:
        model.meshes[mesh].shader = light.depthShader

    model.transform.position = glm.vec3(0.0, 0.0, 0.0)
    model.transform.scaleVector = glm.vec3(5, 5, 5)
    model.render()
    model.transform.position = glm.vec3(0.0, 8.0, 0.0)
    model.transform.scaleVector = glm.vec3(1, 1, 1)
    model.render()
    light.end()
    light.update()

    shader.use()
    shader.setUniform1i("enableShadows", 1)
    shader.setUniform1i("lightCount", 1)
    shader.setUniform3fv("lightPositions", glm.value_ptr(light.transform.position))
    shader.setUniform3fv("lightColors", glm.value_ptr(glm.vec3(1.0, 1.0, 1.0)))
    shader.setUniform1fv("lightBrightnesses", ctypes.c_float(1.0))
    shader.unuse()

    for mesh in model.meshes:
        model.meshes[mesh].shader = shader

    camera.proccessInputs()

    for i in [shader, light.lightShader]:
        camera.shader = i
        camera.updateMatrices()

    window.clear()
    model.transform.position = glm.vec3(0.0, 0.0, 0.0)
    model.transform.scaleVector = glm.vec3(5, 5, 5)
    model.render()
    model.transform.position = glm.vec3(0.0, 8.0, 0.0)
    model.transform.scaleVector = glm.vec3(1, 1, 1)
    model.render()
    light.render()

def exit(window):
    model.delete()
    shader.delete()

def main(argv):
    global window
    window = moss.Window("Shadow Test", 1200, 600, moss.Color(0, 0, 0), True)
    window.event(setup)
    window.event(update)
    window.event(exit)
    moss.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))