import moss, glfw
import pyglet.gl as gl

class Window:
    def __init__(self, title, width, height, backgroundColor, vsync, samples = 1):
        if not moss.context.running: moss.context.__init__()
        self.id = moss.context.registerWindow(self)
        self.title, self.width, self.height = title, width, height
        self.backgroundColor = backgroundColor
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.SAMPLES, samples)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        self.input = moss.Input(self.window)
        self.makeContextCurrent()
        gl.glEnable(gl.GL_DEPTH_TEST)
        if samples > 1: gl.glEnable(gl.GL_MULTISAMPLE)
        glfw.swap_interval(1 if vsync else 0)
        self.destroyed = False
        self.events = {}
        self.currentTime = glfw.get_time()
        self.lastTime = self.currentTime
        self.deltaTime = self.currentTime - self.lastTime
        self.lastResetTime = self.currentTime
        self.framesPerSecond = 0
        self.frames = 0

    def event(self, func):
        self.events[func.__name__] = func

    def setup(self):
        if "setup" in self.events:
            self.events["setup"](self)

    def update(self):
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