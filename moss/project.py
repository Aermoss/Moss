import moss, pickle, glm, sys, os, ctypes

from moss.editor import Script

class Project:
    def __init__(self, filePath):
        self.data = pickle.loads(open(filePath, "rb").read())
        self.window = moss.Window("Moss Window", 1200, 600, moss.Color(*self.data["sky"]["color"]), False, 1)
        self.window.event(self.setup)
        self.window.event(self.update)
        self.window.event(self.exit)

    def setup(self, window):
        self.renderer = moss.Renderer(
            window = self.window,
            hdrTexturePath = None if "currentHDRIndex" not in self.data["sky"] else (None if self.data["sky"]["currentHDRIndex"] == 0 else \
                os.path.join(os.path.split(moss.__file__)[0], "res/hdr_textures", os.listdir(os.path.join(os.path.split(moss.__file__)[0], "res/hdr_textures"))[self.data["sky"]["currentHDRIndex"] - 1]))
        )

        self.camera = moss.Camera(self.renderer.shader)
        self.camera.fov = self.data["camera"]["fov"]
        self.camera.vr = self.data["camera"]["vr"]
        self.camera.position = glm.vec3(*[self.data["camera"]["position"]])
        self.camera.pitch = self.data["camera"]["rotation"][2]
        self.camera.yaw = -self.data["camera"]["rotation"][1]

        self.models = {}
        self.loadModel = lambda filePath: (moss.loadOBJ(self.renderer.shader, filePath), filePath)

        for i in self.data["models"]:
            self.models[i] = self.loadModel(self.data["models"][i])

        self.objects = []

        for i in self.data["objects"]:
            model = moss.Model(self.renderer.shader,
                meshes = self.models[self.data["objects"][i]["model"]][0][0],
                materials = self.models[self.data["objects"][i]["model"]][0][1]
            )

            position = glm.vec3(*self.data["objects"][i]["position"])
            rotation = glm.vec3(*self.data["objects"][i]["rotation"])
            scale = glm.vec3(*self.data["objects"][i]["scale"])

            model.transform.position, model.transform.rotation, model.transform.scaleVector, model.model, model.name = \
                position, rotation, scale, self.data["objects"][i]["model"], i
            
            model.script = Script(self, object, self.data["objects"][i]["script"], len(self.objects)) if self.data["objects"][i]["script"] != None else None
            model.initialValues = {}
            self.objects.append(model)

            if model.script != None:
                if not model.script.setup():
                    sys.exit(-1)

        for i in self.data["lights"]:
            self.renderer.lights.append(
                moss.Light(
                    renderer = self.renderer,
                    position = glm.vec3(*(self.data["lights"][i]["position"])),
                    brightness = self.data["lights"][i]["brightness"],
                    color = glm.vec4(*(self.data["lights"][i]["color"]))
                )
            )

    def update(self, window):
        window.clear()
        self.camera.createViewMatrix()

        for i in self.objects:
            i.transform.pivotx = i.transform.position
            i.transform.pivoty = i.transform.position
            i.transform.pivotz = i.transform.position

            if i.script != None:
                if not i.script.update():
                    sys.exit(-1)

            self.renderer.submit(i)

        self.renderer.render(self.camera)

    def exit(self, window):
        for i in self.objects:
            i.delete()

        for i in self.models:
            for j in self.models[i][0][1]:
                self.models[i][0][1][j].delete()

        self.renderer.shader.delete()

def main(file = None):
    if len(sys.argv) >= 2 and file is None:
        file = sys.argv[1]

    if file is None:
        raise FileNotFoundError("project file not found.")

    project = Project(file)
    moss.run()
    return 0