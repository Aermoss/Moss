import moss, imgui, glm, os, rsxpy, ctypes, rvr, pickle, sys, shutil, glfw, sdl2dll, stbipy, random

import pyglet.gl as gl

script_template = """// Moss Editor

include "rsxio", "api/moss_api.rsxh" : *;

void setup() {
    int objectID = moss::getObjectID();
    std::rout("Hello from R# with ID: " + (string) objectID + std::endl());
}

void update() {

}"""

class Script:
    def __init__(self, editor, object, filePath, id):
        self.editor = editor
        self.object = object
        self.filePath = filePath
        self.id = id
        self.variables, self.functions = {}, {}

    def setup(self):
        try:
            context = rsxpy.core.Context(
                rsxpy.core.parser(
                    rsxpy.core.lexer(
                        moss.readFile(self.filePath), self.filePath
                    ), self.filePath
                ), self.filePath
            )
 
            context.api = {
                "id": self.id,
                "object": self.object,
                "objects": self.editor.objects,
                "models": self.editor.models,
                "context": moss.context,
                "window": self.editor.window,
                "camera": self.editor.camera
            }
            
            self.variables, self.functions = \
                rsxpy.tools.extract(
                    context = context,
                    include_folders = [
                        os.path.split(rsxpy.__file__)[0] + "/include",
                        os.path.split(__file__)[0] + "/"
                    ]
            )

            self.functions["setup"]()

        except SystemExit:
            return False

        return True

    def update(self):
        try:
            self.functions["update"]()

        except SystemExit:
            return False
        
        return True

class Popup:
    def __init__(self, editor):
        self.editor = editor
        self.requests = {}

    def requestVariable(self, request, variables = {"Name": ""}):
        self.requests[request] = {"visible": True, "variables": variables, "done": False}

    def getRequest(self, request):
        if request in self.requests:
            if not self.requests[request]["visible"]:
                temp = self.requests[request]
                del self.requests[request]

                if temp["done"]:
                    return temp["variables"]

        return None

    def update(self):
        for i in self.requests:
            if self.requests[i]["visible"]:
                self.requests[i]["visible"] = imgui.begin(i, True, imgui.WINDOW_NO_RESIZE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)[1]

                for j in self.requests[i]["variables"]:
                    _, self.requests[i]["variables"][j] = imgui.input_text(j, self.requests[i]["variables"][j], 512)

                if imgui.button("Done"):
                    self.requests[i]["visible"] = False
                    self.requests[i]["done"] = True

                imgui.end()

class Editor:
    def __init__(self, filePath = None):
        self.filePath = filePath
        self.window = moss.Window("Moss Editor", 1600, 900, moss.Color(0, 0, 0), False, 1)
        self.window.event(self.setup)
        self.window.event(self.update)
        self.window.event(self.exit)

    def setup(self, window):
        self.renderer = moss.Renderer(self.window)
        self.hdrTextures = ["none"] + os.listdir(os.path.join(os.path.split(moss.__file__)[0], "res/hdr_textures"))
        self.currentHDRIndex = 0
        self.actualHDRIndex = self.currentHDRIndex
        self.currentFile = None
        self.running = False
        self.shouldStart = False
        self.reloadState = True
        self.demoWindow = True
        self.skyColor = glm.vec4(0.0, 0.0, 0.0, 1.0)
        self.popup = Popup(self)
        self.editorCamera = moss.EditorCamera(self.renderer.shader)
        self.camera = moss.Camera(self.renderer.shader, fov = 90)
        self.camera.vr = False
        self.cameraModel = moss.Model(self.renderer.shader, os.path.join(os.path.split(moss.__file__)[0], "res/camera.obj"))
        self.loadModel = lambda path: (moss.loadOBJ(self.renderer.shader, path), path)
        self.renderer.lights, self.objects, self.scripts, self.models = [], [], {}, {
            "Cube": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")),
            "Plane": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/plane.obj")),
            "Sphere": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/sphere.obj")),
            "Monkey": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/monkey.obj")),
            "Teapot": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/teapot.obj"))
        }

        if len(sys.argv) >= 2 and self.filePath is None:
            self.filePath = sys.argv[1]

        if self.filePath is not None:
            self.load(self.filePath)

    def start(self):
        self.running = True
        self.camera.position = self.cameraModel.transform.position
        self.camera.pitch = self.cameraModel.transform.rotation.z
        self.camera.yaw = -self.cameraModel.transform.rotation.y

        if self.camera.vr:
            rvr.RVRInit()
            rvr.RVRSetupStereoRenderTargets()
            rvr.RVRInitControllers()
            rvr.RVRInitEyes(self.camera.near, self.camera.far)

        for i in self.objects:
            i.initialValues = {
                "position": glm.vec3(i.transform.position),
                "rotation": glm.vec3(i.transform.rotation),
                "scale": glm.vec3(i.transform.scaleVector)
            }

        for i in self.objects:
            if i.script != None:
                if not i.script.setup():
                    self.stop()

    def stop(self):
        if self.camera.vr:
            rvr.RVRShutdown()
            rvr.RVRDeleteFramebufferDescriptors()

        for i in self.objects:
            i.transform.position = i.initialValues["position"]
            i.transform.rotation = i.initialValues["rotation"]
            i.transform.scaleVector = i.initialValues["scale"]

        self.running = False

    def newObject(self, name, modelName, script = None, position = None, rotation = None, scale = None):
        if position == None: position = glm.vec3(0.0, 0.0, 0.0)
        if rotation == None: rotation = glm.vec3(0.0, 0.0, 0.0)
        if scale == None: scale = glm.vec3(1.0, 1.0, 1.0)

        model = moss.Model(self.renderer.shader,
            meshes = self.models[modelName][0][0],
            materials = self.models[modelName][0][1]
        )

        model.transform.position, model.transform.rotation, model.transform.scaleVector, model.model, model.name = \
            position, rotation, scale, modelName, name
        
        model.script = Script(self, model, script, len(self.objects)) if script != None else None
        model.initialValues = {}
        self.objects.append(model)

    def newPointLight(self, name, brightness = 1, color = None, position = None):
        if color == None: color = glm.vec4(1.0, 1.0, 1.0, 1.0)
        if position == None: position = glm.vec3(0.0, 0.0, 0.0)
        
        light = moss.Light(self.renderer, position, brightness, color)
        light.name = name
        self.renderer.lights.append(light)

    def save(self, filePath):
        self.currentFile = filePath
        data = {"lights": {}, "models": {}, "objects": {}}

        data["sky"] = {
            "color": [glm.value_ptr(self.skyColor)[i] for i in range(4)],
            "currentHDRIndex": self.currentHDRIndex
        }

        data["camera"] = {
            "position": [glm.value_ptr(self.cameraModel.transform.position)[i] for i in range(3)],
            "rotation": [glm.value_ptr(self.cameraModel.transform.rotation)[i] for i in range(3)],
            "vr": self.camera.vr, "fov": self.camera.fov
        }

        data["editorCamera"] = {
            "position": [glm.value_ptr(self.editorCamera.position)[i] for i in range(3)],
            "pitch": self.editorCamera.pitch,
            "yaw": self.editorCamera.yaw
        }

        for i in self.models:
            data["models"][i] = self.models[i][1]

        for i in self.objects:
            data["objects"][i.name] = {
                "position": [glm.value_ptr(i.transform.position)[j] for j in range(3)],
                "rotation": [glm.value_ptr(i.transform.rotation)[j] for j in range(3)],
                "scale": [glm.value_ptr(i.transform.scaleVector)[j] for j in range(3)],
                "script": i.script.filePath if i.script != None else None,
                "model": i.model
            }

        for i in self.renderer.lights:
            data["lights"][i.name] = {
                "position": [glm.value_ptr(i.position)[j] for j in range(3)],
                "color": [glm.value_ptr(i.color)[j] for j in range(4)],
                "brightness": i.brightness
            }

        with open(filePath, "wb") as file:
            file.write(pickle.dumps(data))

    def reset(self):
        self.currentHDRIndex = 0
        self.currentFile = None
        self.running = False
        self.shouldStart = False
        self.reloadState = True
        self.skyColor = glm.vec4(0.0, 0.0, 0.0, 1.0)
        self.camera.vr = False
        self.camera.fov = 90
        self.cameraModel.transform.position = glm.vec3(0.0, 0.0, 0.0)
        self.cameraModel.transform.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.editorCamera.position = glm.vec3(0.0, 0.0, 1.0)
        self.editorCamera.pitch = 0.0
        self.editorCamera.yaw = 0.0

        self.renderer.lights, self.objects, self.scripts = [], [], {}

        for i in list(self.models.keys()):
            if i not in ["Cube", "Plane", "Sphere", "Monkey", "Teapot"]:
                del self.models[i]

    def load(self, filePath):
        self.reset()
        self.currentFile = filePath

        with open(filePath, "rb") as file:
            data = pickle.loads(file.read())

        if "sky" in data:
            self.skyColor = glm.vec4(*(data["sky"]["color"]))

            if "currentHDRIndex" in data["sky"]:
                self.currentHDRIndex = data["sky"]["currentHDRIndex"]

        if "camera" in data:
            if "fov" in data["camera"]: self.camera.fov = data["camera"]["fov"]
            self.camera.vr = data["camera"]["vr"]
            self.cameraModel.transform.position = glm.vec3(*(data["camera"]["position"]))
            self.cameraModel.transform.rotation = glm.vec3(*(data["camera"]["rotation"]))

        if "editorCamera" in data:
            self.editorCamera.position = glm.vec3(*(data["editorCamera"]["position"]))
            self.editorCamera.pitch = data["editorCamera"]["pitch"]
            self.editorCamera.yaw = data["editorCamera"]["yaw"]

        for i in data["models"]:
            if i in self.models: continue
            self.models[i] = (moss.loadOBJ(self.renderer.shader, data["models"][i]), data["models"][i])

        for i in data["objects"]:
            self.newObject(
                i, data["objects"][i]["model"],
                data["objects"][i]["script"],
                glm.vec3(*(data["objects"][i]["position"])),
                glm.vec3(*(data["objects"][i]["rotation"])),
                glm.vec3(*(data["objects"][i]["scale"]))
            )

        for i in data["lights"]:
            self.newPointLight(
                i, data["lights"][i]["brightness"],
                glm.vec4(*(data["lights"][i]["color"])),
                glm.vec3(*(data["lights"][i]["position"]))
            )

    def build(self):
        projectName = "project"

        if self.currentFile is not None:
            projectName = os.path.split(os.path.splitext(self.currentFile)[0])[1]

        script = f"import sys, os\n\nos.environ[\"PYSDL2_DLL_PATH\"] = os.getcwd()\nsys.path.append(os.getcwd())\n\nfrom moss.project import *\n\nimport sys\n\nif __name__ == \"__main__\":\n    sys.exit(main(\"{projectName}.moss\"))"

        if "build" in os.listdir("."):
            shutil.rmtree("build", ignore_errors = True)

        os.mkdir("build")

        with open(f"build/{projectName}.py", "w") as file:
            file.write(script)

        self.save(f"build/{projectName}.moss")
        cwd = os.getcwd()
        os.chdir("build")
        hiddenImports = ""

        for i in ["moss", "pyglet", "rsxpy", "stbipy", "rvr", "glfw", "glm", "sdl2", "sdl2.ext", "sdl2.sdlmixer", "sdl2dll", "imgui", "imgui.integrations", "imgui.integrations.glfw"]:
            hiddenImports += "--hidden-import=" + i + " "

        os.system(f"pyinstaller {projectName}.py {hiddenImports}")

        with open(os.path.join(os.path.split(glfw.__file__)[0], "glfw3.dll"), "rb") as file:
            data = file.read()

        with open("glfw3.dll", "wb") as file:
            file.write(data)

        with open(os.path.join(os.path.split(glfw.__file__)[0], "msvcr110.dll"), "rb") as file:
            data = file.read()

        with open("msvcr110.dll", "wb") as file:
            file.write(data)

        os.mkdir("stbipy")
        os.mkdir("stbipy/bin")
        shutil.copytree(os.path.join(os.path.split(stbipy.__file__)[0], "bin"), "./stbipy/bin", dirs_exist_ok = True)
        shutil.copytree(os.path.split(rvr.__file__)[0], "./rvr", dirs_exist_ok = True)
        shutil.copytree(os.path.split(moss.__file__)[0], "./moss", dirs_exist_ok = True)
        shutil.copytree(os.path.join(os.path.split(sdl2dll.__file__)[0], "dll"), "./", dirs_exist_ok = True)
        shutil.copytree(f"dist/{projectName}/", "./", dirs_exist_ok = True)
        shutil.rmtree("dist", ignore_errors = True)
        shutil.rmtree("build", ignore_errors = True)
        os.remove(f"{projectName}.spec")
        os.remove(f"{projectName}.py")
        os.chdir(cwd)
        moss.logger.log(moss.INFO, "build successfully finished.")

    def handleRequests(self):
        request = self.popup.getRequest("New Object")
        if request != None:
            self.newObject(request["Name"], request["Model"])

        request = self.popup.getRequest("New Point Light")
        if request != None:
            self.newPointLight(request["Name"])

        request = self.popup.getRequest("Save")
        if request != None:
            self.save(request["File Path"])

        request = self.popup.getRequest("Save As")
        if request != None:
            self.save(request["File Path"])

        request = self.popup.getRequest("Open")
        if request != None:
            self.load(request["File Path"])

        request = self.popup.getRequest("Model Loader")
        if request != None:
            self.models[request["Name"]] = self.loadModel(request["File Path"])

        request = self.popup.getRequest("Add Script")
        if request != None:
            if not os.path.exists(request["File Path"]):
                with open(request["File Path"], "w") as file:
                    file.write(script_template)

            for index, i in enumerate(self.objects):
                if i.name == request["Target Object"]:
                    i.script = Script(self, i, request["File Path"], index)

    def render(self, eye):
        if self.running:
            if self.camera.vr:
                rvr.RVRBeginRendering(eye)

            for i in [self.renderer.shader, self.renderer.basicShader] + ([self.renderer.backgroundShader] if self.renderer.hdrTexturePath is not None else []):
                if self.camera.vr:
                    mat = moss.mkmat(rvr.RVRGetHmdPoseMatrix().value)
                    pos = glm.vec3(-self.camera.position.x, -self.camera.position.y, -self.camera.position.z)
                    mat = glm.translate(mat, pos)

                    i.use()
                    i.setUniform3fv("cameraPosition", glm.value_ptr(self.camera.position + glm.vec3(*[rvr.RVRGetHmdPosition().get()[i] for i in range(3)])))
                    i.setUniformMatrix4fv("proj", rvr.RVRGetCurrentViewProjectionNoPoseMatrix(eye).value)
                    i.setUniformMatrix4fv("view", moss.valptr(mat))
                    i.unuse()

                else:
                    self.camera.shader = i
                    self.camera.createViewMatrix()
                    self.camera.updateMatrices()

        else:
            self.editorCamera.proccessInputs()

            for i in [self.renderer.shader, self.renderer.basicShader] + ([self.renderer.backgroundShader] if self.renderer.hdrTexturePath is not None else []):
                self.editorCamera.shader = i
                self.editorCamera.updateMatrices()

        self.window.clear()

        if not self.running:
            self.renderGui()

        for i in self.objects:
            self.renderer.submit(i)
        
        if not self.running:
            self.renderer.showLights = True
            self.cameraModel.transform.pivotx = self.cameraModel.transform.position
            self.cameraModel.transform.pivoty = self.cameraModel.transform.position
            self.cameraModel.transform.pivotz = self.cameraModel.transform.position
            self.renderer.submit(self.cameraModel)
            self.renderer.render(self.editorCamera)

        else:
            self.renderer.showLights = False
            self.renderer.render(self.camera)

            if self.camera.vr:
                rvr.RVRRenderControllers()
                rvr.RVREndRendering()

    def update(self, window):
        if self.actualHDRIndex != self.currentHDRIndex:
            self.actualHDRIndex = self.currentHDRIndex
            
            if self.currentHDRIndex == 0:
                self.renderer.removeHDRTexture()

            else:
                self.renderer.loadHDRTexture(os.path.join(os.path.split(moss.__file__)[0], f"res/hdr_textures/{self.hdrTextures[self.currentHDRIndex]}"))

        if self.shouldStart or self.window.input.getKey(moss.KEY_F5):
            self.shouldStart = False
            self.start()

        if self.camera.vr and self.running:
            rvr.RVRPollEvents()

        for i in self.objects:
            if self.running and i.script != None:
                if not i.script.update():
                    self.stop()

        for i in self.objects:
            i.transform.pivotx = i.transform.position
            i.transform.pivoty = i.transform.position
            i.transform.pivotz = i.transform.position

        for eye in [rvr.RVREyeLeft, rvr.RVREyeRight] if self.camera.vr else [rvr.RVREyeLeft]:
            self.render(eye)

        if self.running:
            if self.camera.vr:
                rvr.RVRSubmitFramebufferDescriptorsToCompositor()
                rvr.RVRUpdateHMDPoseMatrix()
                self.window.clear()

            if self.window.input.getKey(moss.KEY_ESCAPE):
                self.stop()
        
    def renderGui(self):
        if self.currentFile is not None:
            self.window.title = "Moss Editor - " + self.currentFile

        else:
            self.window.title = "Moss Editor"

        if self.window.input.getKey(moss.KEY_S) and self.window.input.getKey(moss.KEY_LEFT_ALT):
            if self.reloadState:
                self.reloadState = False
                self.window.reloadShaders()

        else:
            self.reloadState = True

        if self.window.input.getKey(moss.KEY_C) and self.window.input.getKey(moss.KEY_LEFT_ALT):
            self.cameraModel.transform.position = glm.vec3(self.editorCamera.position)
            self.cameraModel.transform.rotation.z = self.editorCamera.pitch
            self.cameraModel.transform.rotation.y = -self.editorCamera.yaw

        if self.window.input.getKey(moss.KEY_N) and self.window.input.getKey(moss.KEY_LEFT_CONTROL):
            self.reset()

        if self.window.input.getKey(moss.KEY_O) and self.window.input.getKey(moss.KEY_LEFT_CONTROL):
            self.popup.requestVariable("Open", variables = {"File Path": "project.moss"})

        if self.window.input.getKey(moss.KEY_S) and self.window.input.getKey(moss.KEY_LEFT_CONTROL) and self.window.input.getKey(moss.KEY_LEFT_SHIFT):
            self.popup.requestVariable("Save As", variables = {"File Path": "project.moss"})

        elif self.window.input.getKey(moss.KEY_S) and self.window.input.getKey(moss.KEY_LEFT_CONTROL):
            if self.currentFile is None:
                self.popup.requestVariable("Save", variables = {"File Path": "project.moss"})

            else:
                self.save(self.currentFile)
        
        self.popup.update()
        self.handleRequests()

        # imgui.begin("Inspector", None, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_TITLE_BAR)
        # imgui.set_window_size(self.window.width / 6, self.window.height)
        # imgui.set_window_position(self.window.width - self.window.width / 6, 0.0)
        # imgui.text(self.lastChanged)
        # imgui.end()

        imgui.begin("Scene", None, imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        # imgui.set_window_size(self.window.width / 6, self.window.height)
        imgui.set_window_position(0, 19)

        if self.demoWindow:
            self.demoWindow = imgui.show_demo_window(True)

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("Exit", None)[0]:
                    self.window.destroy()

                if imgui.menu_item("Save", None)[0]:
                    if self.currentFile is None:
                        self.popup.requestVariable("Save", variables = {"File Path": "project.moss"})

                    else:
                        self.save(self.currentFile)

                if self.currentFile is not None:
                    if imgui.menu_item("Save As", None)[0]:
                        self.popup.requestVariable("Save As", variables = {"File Path": self.currentFile})

                if imgui.menu_item("Open", None)[0]:
                    self.popup.requestVariable("Open", variables = {"File Path": "project.moss"})

                if imgui.menu_item("New", None)[0]:
                    self.reset()

                imgui.end_menu()

            if imgui.begin_menu("Object"):
                for i in self.models:
                    if imgui.menu_item(i, None)[0]:
                        self.popup.requestVariable("New Object", variables = {"Name": f"New Object {len(self.objects)}", "Model": i})

                imgui.end_menu()

            if imgui.begin_menu("Light"):
                if imgui.menu_item("Point Light", None)[0]:
                    self.popup.requestVariable("New Point Light", variables = {"Name": f"New Point Light {len(self.renderer.lights)}"})

                imgui.end_menu()

            if imgui.begin_menu("Load"):
                if imgui.menu_item("Model", None)[0]:
                    self.popup.requestVariable("Model Loader", variables = {"Name": "New Model", "File Path": "model.obj"})

                imgui.end_menu(),
            
            if imgui.begin_menu("Game"):
                if imgui.menu_item("Run", None)[0]:
                    self.shouldStart = True

                if imgui.menu_item("Build", None)[0]:
                    self.build()

                imgui.end_menu()

            imgui.end_main_menu_bar()
        
        self.window.backgroundColor.r, self.window.backgroundColor.g, self.window.backgroundColor.b, self.window.backgroundColor.a = \
            self.skyColor.x * 255, self.skyColor.y * 255, self.skyColor.z * 255, self.skyColor.w * 255

        if imgui.tree_node("Sky"):
            self.skyColor.x, self.skyColor.y, self.skyColor.z, self.skyColor.w = \
                imgui.color_edit4("Color", self.skyColor.x, self.skyColor.y, self.skyColor.z, self.skyColor.w)[1]
            
            self.currentHDRIndex = imgui.combo("HDR Texture", self.currentHDRIndex, self.hdrTextures)[1]
            imgui.tree_pop()

        if imgui.tree_node("Camera"):
            self.camera.vr = imgui.checkbox("VR", self.camera.vr)[1]
            self.camera.fov = imgui.drag_float("Field of View", self.camera.fov, 0.1, 0.0, 360.0)[1]

            self.cameraModel.transform.position.x, self.cameraModel.transform.position.y, self.cameraModel.transform.position.z = \
                imgui.drag_float3("Position", self.cameraModel.transform.position.x, self.cameraModel.transform.position.y, self.cameraModel.transform.position.z, 0.1)[1]
                
            if not self.camera.vr:
                self.cameraModel.transform.rotation.z, self.cameraModel.transform.rotation.y = \
                    imgui.drag_float2("Rotation", self.cameraModel.transform.rotation.z, self.cameraModel.transform.rotation.y, 1)[1]
                
            else:
                self.cameraModel.transform.rotation = glm.vec3(0.0, 0.0, 0.0)
            
            imgui.tree_pop()

        for index, i in enumerate(list(self.renderer.lights)):
            if imgui.tree_node(i.name):
                i.position.x, i.position.y, i.position.z = \
                    imgui.drag_float3("Position", i.position.x, i.position.y, i.position.z, 0.1)[1]
                
                i.brightness = imgui.drag_float("Brightness", i.brightness, 0.1, 0.0, 1000000.0)[1]

                i.color.x, i.color.y, i.color.z, i.color.w = \
                    imgui.color_edit4("Color", i.color.x, i.color.y, i.color.z, i.color.w)[1]

                if imgui.button("Delete"):
                    imgui.tree_pop()
                    self.renderer.lights.pop(index)
                    i.delete()
                    continue
                
                imgui.tree_pop()

        for index, i in enumerate(list(self.objects)):
            if imgui.tree_node(i.name):
                i.transform.position.x, i.transform.position.y, i.transform.position.z = \
                    imgui.drag_float3("Position", i.transform.position.x, i.transform.position.y, i.transform.position.z, 0.1)[1]
                
                i.transform.rotation.x, i.transform.rotation.y, i.transform.rotation.z = \
                    imgui.drag_float3("Rotation", i.transform.rotation.x, i.transform.rotation.y, i.transform.rotation.z, 1.0)[1]
                
                i.transform.scaleVector.x, i.transform.scaleVector.y, i.transform.scaleVector.z = \
                    imgui.drag_float3("Scale", i.transform.scaleVector.x, i.transform.scaleVector.y, i.transform.scaleVector.z, 0.1)[1]
                
                if i.script == None:
                    if imgui.button("Add Script"):
                        self.popup.requestVariable("Add Script", variables = {"File Path": "script.rsx", "Target Object": i.name})

                else:
                    imgui.text(f"Script: {i.script.filePath}")

                    if imgui.button("Edit Script"):
                        os.system(f"code {i.script.filePath}")

                    imgui.same_line()

                    if imgui.button("Remove Script"):
                        i.script = None

                imgui.same_line()

                if imgui.button("Delete"):
                    imgui.tree_pop()
                    self.objects.pop(index)
                    i.delete()
                    continue

                if imgui.tree_node("Meshes"):
                    for j in list(i.meshes.keys()):
                        if imgui.tree_node(j):
                            for k in i.meshes[j].submeshes:
                                imgui.text("Material: " + str(k))

                            if imgui.button("Delete"):
                                imgui.tree_pop()
                                del i.meshes[j]
                                continue

                            imgui.tree_pop()

                    imgui.tree_pop()

                if imgui.tree_node("Materials"):
                    for j in i.materials:
                        if imgui.tree_node(str(j)):
                            i.materials[j].albedo.x, i.materials[j].albedo.y, i.materials[j].albedo.z = \
                                imgui.color_edit3("Rotation", i.materials[j].albedo.x, i.materials[j].albedo.y, i.materials[j].albedo.z)[1]
                            
                            i.materials[j].roughness = imgui.drag_float("Roughness", i.materials[j].roughness, 0.01, 0.0, 1.0)[1]
                            i.materials[j].metallic = imgui.drag_float("Metallic", i.materials[j].metallic, 0.01, 0.0, 1.0)[1]

                            if i.materials[j].albedoMap != None or i.materials[j].normalMap != None or i.materials[j].roughnessMap != None or i.materials[j].metallicMap != None:
                                if imgui.tree_node("Textures"):
                                    if i.materials[j].albedoMap != None:
                                        if imgui.tree_node("Albedo Map"):
                                            imgui.text("Path: " + i.materials[j].albedoMap.filePath)
                                            if imgui.button("Delete"): i.materials[j].albedoMap = None
                                            imgui.tree_pop()

                                    if i.materials[j].normalMap != None:
                                        if imgui.tree_node("Normal Map"):
                                            imgui.text("Path: " + i.materials[j].normalMap.filePath)
                                            if imgui.button("Delete"): i.materials[j].normalMap = None
                                            imgui.tree_pop()

                                    if i.materials[j].roughnessMap != None:
                                        if imgui.tree_node("Roughness Map"):
                                            imgui.text("Path: " + i.materials[j].roughnessMap.filePath)
                                            if imgui.button("Delete"): i.materials[j].roughnessMap = None
                                            imgui.tree_pop()

                                    if i.materials[j].metallicMap != None:
                                        if imgui.tree_node("Metallic Map"):
                                            imgui.text("Path: " + i.materials[j].metallicMap.filePath)
                                            if imgui.button("Delete"): i.materials[j].metallicMap = None
                                            imgui.tree_pop()

                                    imgui.tree_pop()

                            imgui.tree_pop()

                    imgui.tree_pop()
                
                imgui.tree_pop()

        imgui.end()

    def exit(self, window):
        for i in self.objects:
            i.delete()

        for i in self.models:
            for j in self.models[i][0][1]:
                self.models[i][0][1][j].delete()

        self.cameraModel.delete()
        self.renderer.delete()

def main(filePath = None):
    editor = Editor(filePath = filePath)
    moss.run()
    return 0

if __name__ == "__main__":
    sys.exit(main())