import moss, glfw

import pyglet.gl as gl

class Context:
    def __init__(self):
        glfw.init()
        moss.logger.log(moss.INFO, "context created successfully.")
        self.windows = {}
        self.events = {"noWindowsAvailable": self.delete}
        self.removeQueue = []
        self.currentWindow = None
        self.running = True
        self.vendorName = gl.glGetString(gl.GL_VENDOR).decode()
        self.rendererName = gl.glGetString(gl.GL_RENDERER).decode()
        self.glVersion = gl.glGetString(gl.GL_VERSION).decode()
        self.glslVersion = gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION).decode()
        self.glExtensions = gl.glGetString(gl.GL_EXTENSIONS).decode().split(" ")
        self.glExtensionCount = len(self.glExtensions)
        self.display = glfw.get_primary_monitor()
        videoMode = glfw.get_video_mode(self.display)
        self.displayWidth = videoMode.size.width
        self.displayHeight = videoMode.size.height
        self.displayRefreshRate = videoMode.refresh_rate
        moss.logger.log(moss.INFO,
            f"found display device:\n{' ' * 12}> size: {self.displayWidth} x {self.displayHeight}\n{' ' * 12}> refresh rate: {self.displayRefreshRate}"
        )
        moss.logger.log(moss.INFO,
            f"found renderer device:\n{' ' * 12}> vendor: {self.vendorName}\n{' ' * 12}> renderer: {self.rendererName}\n{' ' * 12}> version: {self.glVersion}\n{' ' * 12}> glsl: {self.glslVersion}"
        )
        moss.logger.log(moss.INFO, f"supported extension count: {self.glExtensionCount}")

    def event(self, func):
        self.events[func.__name__] = func

    def genWindowId(self):
        windowId = 1
        while windowId in self.windows: windowId += 1
        return windowId

    def registerWindow(self, window):
        windowId = self.genWindowId()
        self.windows[windowId] = window
        moss.logger.log(moss.INFO, f"a window named \"{self.windows[windowId].title}\" has been registered with id {windowId}.")
        return windowId

    def removeWindow(self, windowId):
        moss.logger.log(moss.INFO, f"window with id {windowId} named \"{self.windows[windowId].title}\" is queued to be closed.")
        self.removeQueue.append(windowId)

    def checkRemoveQueue(self):
        for windowId in self.removeQueue:
            window = self.windows[windowId]

            if "exit" in self.events:
                self.events["exit"](window)

            glfw.destroy_window(window.window)
            moss.logger.log(moss.INFO, f"window with id {windowId} named \"{self.windows[windowId].title}\" was successfully closed.")
            del self.windows[windowId]

        self.removeQueue.clear()

    def getCurrentWindow(self):
        return self.currentWindow

    def run(self):
        for windowId in self.windows:
            window = self.windows[windowId]
            self.currentWindow = window
            window.makeContextCurrent()
            window.setup()

            if "setup" in self.events:
                self.events["setup"](window)

        while self.running:
            glfw.poll_events()

            for windowId in self.windows:
                window = self.windows[windowId]
                self.currentWindow = window
                window.makeContextCurrent()
                window.update()

                if "update" in self.events:
                    self.events["update"](window)

                window.swapBuffers()

            self.checkRemoveQueue()
            
            if len(self.windows) == 0:
                moss.logger.log(moss.WARNING, f"no windows available!")
                self.events["noWindowsAvailable"]()

    def delete(self):
        self.running = False
        glfw.terminate()
        moss.logger.log(moss.INFO, f"context successfully terminated.")