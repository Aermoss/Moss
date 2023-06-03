import moss, glfw

class Context:
    def __init__(self):
        glfw.init()
        self.windows = {}
        self.events = {"noWindowsAvailable": self.delete}
        self.removeQueue = []
        self.currentWindow = None
        self.running = True

    def event(self, func):
        self.events[func.__name__] = func

    def genWindowId(self):
        windowId = 1
        while windowId in self.windows: windowId += 1
        return windowId

    def registerWindow(self, window):
        windowId = self.genWindowId()
        self.windows[windowId] = window
        return windowId

    def removeWindow(self, id):
        self.removeQueue.append(id)

    def checkRemoveQueue(self):
        for windowId in self.removeQueue:
            window = self.windows[windowId]

            if "exit" in self.events:
                self.events["exit"](window)

            glfw.destroy_window(window.window)
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
                self.events["noWindowsAvailable"]()

    def delete(self):
        self.running = False
        glfw.terminate()