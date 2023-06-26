import moss, glfw
import pyglet.gl as gl

class Window:
    def __init__(self, title, width, height, backgroundColor, vsync = False, samples = 1, fullscreen = False, doubleBuffer = False):
        if not moss.context.running: moss.context.__init__()
        self.title, self.width, self.height = title, width, height
        self.actualTitle = self.title
        self.backgroundColor = backgroundColor
        self.id = moss.context.registerWindow(self)
        if vsync: moss.logger.log(moss.INFO, f"target time per frame: {1.0 / moss.context.displayRefreshRate}")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.DOUBLEBUFFER, glfw.TRUE if doubleBuffer else glfw.FALSE)
        glfw.window_hint(glfw.SAMPLES, samples)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        self.window = glfw.create_window(self.width, self.height, self.title, moss.context.display if fullscreen else None, None)
        self.input = moss.Input(self.window)
        self.makeContextCurrent()
        gl.glEnable(gl.GL_DEPTH_TEST)
        if samples > 1: gl.glEnable(gl.GL_MULTISAMPLE)
        glfw.swap_interval(1 if vsync else 0)
        self.destroyed = False
        self.shaders = {}
        self.events = {}
        self.currentTime = glfw.get_time()
        self.startTime = self.currentTime
        self.lastTime = self.currentTime
        self.deltaTime = self.currentTime - self.lastTime
        self.lastResetTime = self.currentTime
        self.targetDelta = 0
        self.framesPerSecond = 0
        self.frames = 0

    def registerShader(self, shader):
        self.shaders[shader.program] = shader

    def removeShader(self, shader):
        del self.shaders[shader.program]

    def reloadShaders(self):
        startTime = glfw.get_time()

        for i in list(self.shaders.keys()):
            self.shaders[i].reload()

        moss.logger.log(moss.INFO, f"all shaders are reloaded in {glfw.get_time() - startTime}.")

    def event(self, func):
        self.events[func.__name__] = func

    def setup(self):
        if "setup" in self.events:
            self.events["setup"](self)

    def update(self):
        if self.actualTitle != self.title:
            self.actualTitle = self.title
            glfw.set_window_title(self.window, self.title)

        self.width, self.height = glfw.get_window_size(self.window)
        gl.glViewport(0, 0, self.width, self.height)

        self.currentTime = glfw.get_time()
        self.deltaTime = self.currentTime - self.lastTime
        self.lastTime = self.currentTime
        self.frames += 1

        if self.currentTime - self.lastResetTime >= 1:
            self.framesPerSecond = self.frames
            self.lastResetTime = self.currentTime
            self.frames = 0

        if glfw.window_should_close(self.window):
            self.delete()

        if not self.destroyed:
            if "update" in self.events:
                self.events["update"](self)

    def clear(self):
        gl.glClearColor(*self.backgroundColor.get())
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT | gl.GL_STENCIL_BUFFER_BIT)

    def makeContextCurrent(self):
        glfw.make_context_current(self.window)

    def swapBuffers(self):
        glfw.swap_buffers(self.window)

    def delete(self):
        if "exit" in self.events:
            self.events["exit"](self)

        self.destroyed = True
        moss.context.removeWindow(self.id)