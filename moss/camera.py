import moss, glm, math

class Camera:
    def __init__(self, shader, fov = 90, position = glm.vec3(0.0, 0.0, 1.0), front = glm.vec3(0.0, 0.0, -1.0), near = 0.01, far = 1000.0):
        self.window, self.shader = moss.context.getCurrentWindow(), shader
        self.fov, self.position = fov, position
        self.front, self.near, self.far = front, near, far
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw, self.pitch = 0.0, 0.0
        self.proj, self.view = None, None

    def createViewMatrix(self):
        self.front = glm.normalize(glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        ))

        self.view = glm.lookAt(self.position, self.position + self.front, self.up)

    def updateMatrices(self):
        if self.window.width == 0: return
        
        self.proj = glm.perspective(glm.radians(self.fov), self.window.width / self.window.height, self.near, self.far)
        self.shader.use()
        self.shader.setUniform3fv("cameraPosition", glm.value_ptr(self.position))
        self.shader.setUniformMatrix4fv("proj", glm.value_ptr(self.proj))
        self.shader.setUniformMatrix4fv("view", glm.value_ptr(self.view))
        self.shader.unuse()

class TPSCamera:
    def __init__(self, shader, fov = 90, sensitivity = 100.0, radius = 10.0, center = glm.vec3(0.0), near = 0.01, far = 1000.0):
        self.window, self.shader = moss.context.getCurrentWindow(), shader
        self.sensitivity, self.fov = sensitivity, fov
        self.radius, self.center = radius, center
        self.near, self.far = near, far
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw, self.pitch = 0.0, 0.0

    def proccessInputs(self):
        if self.window.width == 0: return

        self.window.input.setCursorVisible(False)
        x, y = self.window.input.getCursorPosition()

        x_offset = self.sensitivity * (x - int(self.window.width / 2)) / self.window.width
        y_offset = self.sensitivity * (y - int(self.window.height / 2)) / self.window.height

        self.yaw += x_offset
        self.pitch += y_offset

        if self.pitch >= 89.9:
            self.pitch = 89.9

        if self.pitch <= -89.9:
            self.pitch = -89.9

        self.window.input.setCursorPosition(self.window.width / 2, self.window.height / 2)

    def updateMatrices(self):
        if self.window.width == 0: return

        self.front = glm.normalize(glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        ))

        proj = glm.perspective(glm.radians(self.fov), self.window.width / self.window.height, self.near, self.far)
        offset = glm.normalize(self.front) * self.radius
        self.position = self.center + offset
        view = glm.lookAt(self.position, self.position - self.front, self.up)
        self.shader.use()
        self.shader.setUniform3fv("cameraPosition", glm.value_ptr(self.position))
        self.shader.setUniformMatrix4fv("proj", glm.value_ptr(proj))
        self.shader.setUniformMatrix4fv("view", glm.value_ptr(view))
        self.shader.unuse()

class FPSCamera:
    def __init__(self, shader, fov = 90, normalSpeed = 0.1, sprintSpeed = 0.2, sensitivity = 100.0,
                 position = glm.vec3(0.0, 0.0, 1.0), front = glm.vec3(0.0, 0.0, -1.0), near = 0.01, far = 1000.0):
        self.window, self.shader = moss.context.getCurrentWindow(), shader
        self.fov, self.position, self.speed = fov, position, 0.0
        self.normalSpeed, self.sprintSpeed = normalSpeed, sprintSpeed
        self.sensitivity, self.front = sensitivity, front
        self.near, self.far = near, far
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw, self.pitch = 0.0, 0.0

    def proccessInputs(self):
        if self.window.width == 0: return

        if self.window.input.getKey(moss.KEY_LEFT_CONTROL):
            self.speed = self.sprintSpeed

        else:
            self.speed = self.normalSpeed

        if self.window.input.getKey(moss.KEY_W):
            self.position += self.speed * glm.vec3(glm.cos(glm.radians(self.yaw)), 0, glm.sin(glm.radians(self.yaw))) * self.window.deltaTime * 10

        if self.window.input.getKey(moss.KEY_S):
            self.position += self.speed * -glm.vec3(glm.cos(glm.radians(self.yaw)), 0, glm.sin(glm.radians(self.yaw))) * self.window.deltaTime * 10

        if self.window.input.getKey(moss.KEY_A):
            self.position += self.speed * -glm.normalize(glm.cross(self.front, self.up)) * self.window.deltaTime * 10

        if self.window.input.getKey(moss.KEY_D):
            self.position += self.speed * glm.normalize(glm.cross(self.front, self.up)) * self.window.deltaTime * 10

        if self.window.input.getKey(moss.KEY_SPACE):
            self.position += self.speed * self.up * self.window.deltaTime * 10

        if self.window.input.getKey(moss.KEY_LEFT_SHIFT):
            self.position += self.speed * -self.up * self.window.deltaTime * 10

        self.window.input.setCursorVisible(False)
        x, y = self.window.input.getCursorPosition()

        x_offset = self.sensitivity * (x - int(self.window.width / 2)) / self.window.width
        y_offset = self.sensitivity * (y - int(self.window.height / 2)) / self.window.height

        self.yaw += x_offset
        self.pitch -= y_offset

        if self.pitch >= 89.9:
            self.pitch = 89.9

        if self.pitch <= -89.9:
            self.pitch = -89.9

        self.window.input.setCursorPosition(self.window.width / 2, self.window.height / 2)

    def updateMatrices(self):
        if self.window.width == 0: return

        self.front = glm.normalize(glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        ))

        proj = glm.perspective(glm.radians(self.fov), self.window.width / self.window.height, self.near, self.far)
        view = glm.lookAt(self.position, self.position + self.front, self.up)
        self.shader.use()
        self.shader.setUniform3fv("cameraPosition", glm.value_ptr(self.position))
        self.shader.setUniformMatrix4fv("proj", glm.value_ptr(proj))
        self.shader.setUniformMatrix4fv("view", glm.value_ptr(view))
        self.shader.unuse()

class FreeCamera:
    def __init__(self, shader, fov = 90, normalSpeed = 0.1, sprintSpeed = 0.2, sensitivity = 100.0,
                 position = glm.vec3(0.0, 0.0, 1.0), front = glm.vec3(0.0, 0.0, -1.0), near = 0.01, far = 1000.0):
        self.window, self.shader = moss.context.getCurrentWindow(), shader
        self.fov, self.position, self.speed = fov, position, 0.0
        self.normalSpeed, self.sprintSpeed = normalSpeed, sprintSpeed
        self.sensitivity, self.front = sensitivity, front
        self.near, self.far = near, far
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw, self.pitch = 0.0, 0.0

    def proccessInputs(self):
        if self.window.width == 0: return

        if self.window.input.getKey(moss.KEY_LEFT_CONTROL):
            self.speed = self.sprintSpeed

        else:
            self.speed = self.normalSpeed

        if self.window.input.getKey(moss.KEY_W):
            self.position += self.speed * self.front

        if self.window.input.getKey(moss.KEY_S):
            self.position += self.speed * -self.front

        if self.window.input.getKey(moss.KEY_A):
            self.position += self.speed * -glm.normalize(glm.cross(self.front, self.up))

        if self.window.input.getKey(moss.KEY_D):
            self.position += self.speed * glm.normalize(glm.cross(self.front, self.up))

        if self.window.input.getKey(moss.KEY_SPACE):
            self.position += self.speed * self.up

        if self.window.input.getKey(moss.KEY_LEFT_SHIFT):
            self.position += self.speed * -self.up

        self.window.input.setCursorVisible(False)
        x, y = self.window.input.getCursorPosition()

        x_offset = self.sensitivity * (x - int(self.window.width / 2)) / self.window.width
        y_offset = self.sensitivity * (y - int(self.window.height / 2)) / self.window.height

        self.yaw += x_offset
        self.pitch -= y_offset

        if self.pitch >= 89.9:
            self.pitch = 89.9

        if self.pitch <= -89.9:
            self.pitch = -89.9

        self.window.input.setCursorPosition(self.window.width / 2, self.window.height / 2)

    def updateMatrices(self):
        if self.window.width == 0: return

        self.front = glm.normalize(glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        ))

        proj = glm.perspective(glm.radians(self.fov), self.window.width / self.window.height, self.near, self.far)
        view = glm.lookAt(self.position, self.position + self.front, self.up)
        self.shader.use()
        self.shader.setUniform3fv("cameraPosition", glm.value_ptr(self.position))
        self.shader.setUniformMatrix4fv("proj", glm.value_ptr(proj))
        self.shader.setUniformMatrix4fv("view", glm.value_ptr(view))
        self.shader.unuse()

class EditorCamera:
    def __init__(self, shader, fov = 90, normalSpeed = 0.1, sprintSpeed = 0.2, sensitivity = 100.0,
                 position = glm.vec3(0.0, 0.0, 1.0), front = glm.vec3(0.0, 0.0, -1.0), near = 0.01, far = 1000.0):
        self.window, self.shader = moss.context.getCurrentWindow(), shader
        self.fov, self.position, self.speed = fov, position, 0.0
        self.normalSpeed, self.sprintSpeed = normalSpeed, sprintSpeed
        self.enabled, self.lastScroll = False, 0
        self.sensitivity, self.front = sensitivity, front
        self.near, self.far = near, far
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw, self.pitch = 0.0, 0.0

    def proccessInputs(self):
        if self.window.width == 0: return
        
        if not self.window.input.getMouseButton(moss.MOUSE_BUTTON_RIGHT):
            self.window.input.setCursorVisible(True)
            self.enabled = False
            return
        
        if not self.enabled:
            self.window.input.setCursorPosition(self.window.width / 2, self.window.height / 2)
            self.lastScroll = self.window.input.scrollY
            self.enabled = True

        self.window.input.setCursorVisible(False)
        x, y = self.window.input.getCursorPosition()
        
        if self.window.input.getKey(moss.KEY_LEFT_CONTROL):
            self.speed = self.sprintSpeed

        else:
            self.speed = self.normalSpeed

        if self.window.input.scrollY != self.lastScroll:
            self.position += (self.window.input.scrollY - self.lastScroll) * self.speed * 10 * self.front
            self.lastScroll = self.window.input.scrollY

        if self.window.input.getKey(moss.KEY_W):
            self.position += self.speed * self.front

        if self.window.input.getKey(moss.KEY_S):
            self.position += self.speed * -self.front

        if self.window.input.getKey(moss.KEY_A):
            self.position += self.speed * -glm.normalize(glm.cross(self.front, self.up))

        if self.window.input.getKey(moss.KEY_D):
            self.position += self.speed * glm.normalize(glm.cross(self.front, self.up))

        if self.window.input.getKey(moss.KEY_SPACE):
            self.position += self.speed * self.up

        if self.window.input.getKey(moss.KEY_LEFT_SHIFT):
            self.position += self.speed * -self.up

        x_offset = self.sensitivity * (x - int(self.window.width / 2)) / self.window.width
        y_offset = self.sensitivity * (y - int(self.window.height / 2)) / self.window.height

        self.yaw += x_offset
        self.pitch -= y_offset

        if self.pitch >= 89.9:
            self.pitch = 89.9

        if self.pitch <= -89.9:
            self.pitch = -89.9

        self.window.input.setCursorPosition(self.window.width / 2, self.window.height / 2)

    def updateMatrices(self):
        if self.window.width == 0: return

        self.front = glm.normalize(glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        ))

        proj = glm.perspective(glm.radians(self.fov), self.window.width / self.window.height, self.near, self.far)
        view = glm.lookAt(self.position, self.position + self.front, glm.vec3(0.0, self.up.y * math.cos(45.0), 0.0))
        self.shader.use()
        self.shader.setUniform3fv("cameraPosition", glm.value_ptr(self.position))
        self.shader.setUniformMatrix4fv("proj", glm.value_ptr(proj))
        self.shader.setUniformMatrix4fv("view", glm.value_ptr(view))
        self.shader.unuse()