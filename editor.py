import moss, imgui, glm, os, rsxpy, ctypes, time, rvr, pickle

from imgui.integrations.glfw import GlfwRenderer
import pyglet.gl as gl

script_template = """// Moss Editor

include "rsxio", "moss_api.rsxh" : *;

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
    
class Light:
    def __init__(self):
        self.depthShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.frag")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.geom"))
        )

        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.shadow_width, self.shadow_height = 8192, 8192
        self.depthMapFBO = ctypes.c_uint32()
        gl.glGenFramebuffers(1, ctypes.byref(self.depthMapFBO))
        self.depthCubemap = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.depthCubemap))
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.depthCubemap)

        for i in range(6):
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_DEPTH_COMPONENT, self.shadow_width, self.shadow_height, 0, gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, 0)

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
        shadowProj = glm.perspective(glm.radians(90.0), self.shadow_width / self.shadow_height, near_plane, far_plane)
        shadowTransforms = []
        shadowTransforms.append(shadowProj * glm.lookAt(self.position, self.position + glm.vec3(1.0, 0.0, 0.0), glm.vec3(0.0, -1.0, 0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.position, self.position + glm.vec3(-1.0, 0.0, 0.0), glm.vec3(0.0, -1.0, 0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.position, self.position + glm.vec3(0.0, 1.0, 0.0), glm.vec3(0.0, 0.0, 1.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.position, self.position + glm.vec3(0.0, -1.0, 0.0), glm.vec3(0.0, 0.0, -1.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.position, self.position + glm.vec3(0.0, 0.0, 1.0), glm.vec3(0.0, -1.0, 0.0)))
        shadowTransforms.append(shadowProj * glm.lookAt(self.position, self.position + glm.vec3(0.0, 0.0, -1.0), glm.vec3(0.0, -1.0, 0.0)))

        gl.glViewport(0, 0, self.shadow_width, self.shadow_height)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.depthMapFBO)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        self.depthShader.use()

        for i in range(6):
            self.depthShader.setUniformMatrix4fv(f"shadowMatrices[{i}]", glm.value_ptr(shadowTransforms[i]))

        self.depthShader.setUniform3fv("lightPosition", glm.value_ptr(self.position))

    def end(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glViewport(0, 0, window.width, window.height)

    def update(self, shader):
        shader.use()
        gl.glActiveTexture(gl.GL_TEXTURE0 + 6)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.depthCubemap)
        shader.setUniform1i("depthMap", 6)
        shader.unuse()

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
                self.requests[i]["visible"] = imgui.begin(i, True)[1]

                for j in self.requests[i]["variables"]:
                    _, self.requests[i]["variables"][j] = imgui.input_text(j, self.requests[i]["variables"][j], 512)

                if imgui.button("Done"):
                    self.requests[i]["visible"] = False
                    self.requests[i]["done"] = True

                imgui.end()

class Editor:
    def __init__(self):
        imgui.create_context()
        self.window = moss.context.getCurrentWindow()
        self.impl = GlfwRenderer(self.window.window)
        self.io = imgui.get_io()

        self.shader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
        )

        self.lightShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.frag"))
        )

        self.running = False
        self.should_start = False
        self.reloadState = True
        self.skyColor = glm.vec4(0.0, 0.0, 0.0, 1.0)
        self.popup = Popup(self)
        self.light = Light()
        self.editorCamera = moss.EditorCamera(self.shader)
        self.camera = moss.Camera(self.shader)
        self.camera.vr = False
        self.camera_model = moss.Model(self.shader, os.path.join(os.path.split(moss.__file__)[0], "res/camera.obj"))
        self.loadModel = lambda path: (moss.loadOBJ(path), path)
        self.lights, self.objects, self.scripts, self.models = [], [], {}, {
            "Cube": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")),
            "Plane": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/plane.obj")),
            "Sphere": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/sphere.obj")),
            "Monkey": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/monkey.obj")),
            "Teapot": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/teapot.obj"))
        }

    def start(self):
        self.running = True
        self.camera.position = self.camera_model.transform.position
        self.camera.pitch = self.camera_model.transform.rotation.z
        self.camera.yaw = -self.camera_model.transform.rotation.y

        if self.camera.vr:
            rvr.RVRInit()
            rvr.RVRSetupStereoRenderTargets()
            rvr.RVRInitControllers()
            rvr.RVRInitEyes(self.camera.near, self.camera.far)

        for i in self.objects:
            i.initialValues = {
                "position": glm.vec3(i.transform.position),
                "rotation": glm.vec3(i.transform.rotation),
                "scale": glm.vec3(i.transform.scaleVector),
                "color": glm.vec4(i.color),
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
            i.color = i.initialValues["color"]

        self.running = False

    def reloadShaders(self):
        start_time = time.time()
        self.lightShader.delete()
        self.shader.delete()

        self.shader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
        )

        self.lightShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.frag"))
        )

        self.camera_model.shader = self.shader
        
        for i in self.lights:
            i.shader = self.lightShader

        for i in self.objects:
            i.shader = self.shader

        self.reloadState = False
        print(f"shaders are reloaded in: {time.time() - start_time}")

    def newObject(self, name, modelName, script = None, color = None, position = None, rotation = None, scale = None):
        if color == None: color = glm.vec4(1.0, 1.0, 1.0, 1.0)
        if position == None: position = glm.vec3(0.0, 0.0, 0.0)
        if rotation == None: rotation = glm.vec3(0.0, 0.0, 0.0)
        if scale == None: scale = glm.vec3(1.0, 1.0, 1.0)

        model = moss.Model(self.shader,
            meshes = self.models[modelName][0][0],
            materials = self.models[modelName][0][1]
        )

        model.transform.position, model.transform.rotation, model.transform.scaleVector, model.color, model.model, model.name = \
            position, rotation, scale, color, modelName, name
        
        temp, equal = None, True
        
        for i in model.meshes:
            for j in model.meshes[i].parts:
                if temp == None:
                    temp = model.meshes[i].parts[j]["material"]["albedo"]

                if model.meshes[i].parts[j]["material"]["albedo"] != temp or \
                    "albedoMap" in model.meshes[i].parts[j]["material"]: equal = False

        if equal:
            for i in model.meshes:
                for j in model.meshes[i].parts:
                    model.meshes[i].parts[j]["material"]["albedo"] = model.color

        model.script = Script(self, model, script, len(self.objects)) if script != None else None
        model.initialValues = {}
        self.objects.append(model)

    def newPointLight(self, name, brightness = 1, color = None, position = None, rotation = None):
        if color == None: color = glm.vec4(1.0, 1.0, 1.0, 1.0)
        if position == None: position = glm.vec3(0.0, 0.0, 0.0)
        if rotation == None: rotation = glm.vec3(0.0, 0.0, 0.0)
        
        model = moss.Model(self.lightShader,
            meshes = self.models["Sphere"][0][0],
            materials = self.models["Sphere"][0][1]
        )

        model.transform.position, model.transform.rotation, model.color, model.name, model.brightness = \
            position, rotation, color, name, brightness
        
        model.transform.scaleVector = glm.vec3(0.1, 0.1, 0.1)
        self.lights.append(model)

    def save(self, filePath):
        data = {"lights": {}, "models": {}, "objects": {}}

        data["sky"] = {
            "color": [glm.value_ptr(self.skyColor)[i] for i in range(4)]
        }

        data["camera"] = {
            "position": [glm.value_ptr(self.camera_model.transform.position)[i] for i in range(3)],
            "rotation": [glm.value_ptr(self.camera_model.transform.rotation)[i] for i in range(3)],
            "vr": self.camera.vr
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
                "color": [glm.value_ptr(i.color)[j] for j in range(4)],
                "script": i.script.filePath if i.script != None else None,
                "model": i.model
            }

        for i in self.lights:
            data["lights"][i.name] = {
                "position": [glm.value_ptr(i.transform.position)[j] for j in range(3)],
                "rotation": [glm.value_ptr(i.transform.rotation)[j] for j in range(3)],
                "color": [glm.value_ptr(i.color)[j] for j in range(4)],
                "brightness": i.brightness
            }

        with open(filePath, "wb") as file:
            file.write(pickle.dumps(data))

    def reset(self):
        self.running = False
        self.should_start = False
        self.reloadState = True
        self.skyColor = glm.vec4(0.0, 0.0, 0.0, 1.0)
        self.camera.vr = False
        self.camera_model.transform.position = glm.vec3(0.0, 0.0, 0.0)
        self.camera_model.transform.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.editorCamera.position = glm.vec3(0.0, 0.0, 1.0)
        self.editorCamera.pitch = 0.0
        self.editorCamera.yaw = 0.0

        self.lights, self.objects, self.scripts, self.models = [], [], {}, {
            "Cube": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")),
            "Plane": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/plane.obj")),
            "Sphere": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/sphere.obj")),
            "Monkey": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/monkey.obj")),
            "Teapot": self.loadModel(os.path.join(os.path.split(moss.__file__)[0], "res/teapot.obj"))
        }

    def load(self, filePath):
        self.reset()

        with open(filePath, "rb") as file:
            data = pickle.loads(file.read())

        if "sky" in data:
            self.skyColor = glm.vec4(*(data["sky"]["color"]))

        if "camera" in data:
            self.camera.vr = data["camera"]["vr"]
            self.camera_model.transform.position = glm.vec3(*(data["camera"]["position"]))
            self.camera_model.transform.rotation = glm.vec3(*(data["camera"]["rotation"]))

        if "editorCamera" in data:
            self.editorCamera.position = glm.vec3(*(data["editorCamera"]["position"]))
            self.editorCamera.pitch = data["editorCamera"]["pitch"]
            self.editorCamera.yaw = data["editorCamera"]["yaw"]

        for i in data["models"]:
            if i in self.models: continue
            self.models[i] = (moss.loadOBJ(data["models"][i]), data["models"][i])

        for i in data["objects"]:
            self.newObject(
                i, data["objects"][i]["model"],
                data["objects"][i]["script"],
                glm.vec4(*(data["objects"][i]["color"])),
                glm.vec3(*(data["objects"][i]["position"])),
                glm.vec3(*(data["objects"][i]["rotation"])),
                glm.vec3(*(data["objects"][i]["scale"]))
            )

        for i in data["lights"]:
            self.newPointLight(
                i, data["lights"][i]["brightness"],
                glm.vec4(*(data["lights"][i]["color"])),
                glm.vec3(*(data["lights"][i]["position"])),
                glm.vec3(*(data["lights"][i]["rotation"]))
            )

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

        request = self.popup.getRequest("Open")
        if request != None:
            self.load(request["File Path"])

        request = self.popup.getRequest("Model Loader")
        if request != None:
            self.models[request["Name"]] = (moss.loadOBJ(request["File Path"]), request["File Path"])

        request = self.popup.getRequest("Add Script")
        if request != None:
            if not os.path.exists(request["File Path"]):
                with open(request["File Path"], "w") as file:
                    file.write(script_template)

            for index, i in enumerate(self.objects):
                if i.name == request["Target Object"]:
                    i.script = Script(self, i, request["File Path"], index)

    def updateLights(self):
        lightPositions = []
        lightColors = []
        lightBrightnesses = []

        for i in self.lights:
            lightPositions += [i.transform.position.x, i.transform.position.y, i.transform.position.z]
            lightColors += [i.color.x, i.color.y, i.color.z]
            lightBrightnesses += [i.brightness]

            if not self.running:
                self.lightShader.use()
                self.lightShader.setUniform4fv("color", glm.value_ptr(i.color))
                self.lightShader.unuse()

        self.shader.use()
        self.shader.setUniform1i("enableShadows", 1)
        self.shader.setUniform1i("lightCount", len(self.lights))

        if len(self.lights) != 0:
            self.shader.setUniform3fv("lightPositions", (ctypes.c_float * len(lightPositions))(*lightPositions), len(self.lights))
            self.shader.setUniform3fv("lightColors", (ctypes.c_float * len(lightColors))(*lightColors), len(self.lights))
            self.shader.setUniform1fv("lightBrightnesses", (ctypes.c_float * len(lightBrightnesses))(*lightBrightnesses), len(self.lights))

        self.shader.unuse()

    def render(self, eye):
        if self.running:
            if self.camera.vr:
                rvr.RVRBeginRendering(eye)

            for i in [self.shader, self.lightShader]:
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

            for i in [self.shader, self.lightShader]:
                self.editorCamera.shader = i
                self.editorCamera.updateMatrices()

        self.window.clear()

        for i in self.objects:
            i.render()
        
        if not self.running:
            self.camera_model.transform.pivotx = self.camera_model.transform.position
            self.camera_model.transform.pivoty = self.camera_model.transform.position
            self.camera_model.transform.pivotz = self.camera_model.transform.position
            self.camera_model.render()

            for i in self.lights:
                i.transform.pivotx = i.transform.position
                i.transform.pivoty = i.transform.position
                i.transform.pivotz = i.transform.position
                i.render()

        else:
            if self.camera.vr:
                rvr.RVRRenderControllers()
                rvr.RVREndRendering()

    def update(self):
        if self.should_start:
            self.should_start = False
            self.start()

        if self.camera.vr and self.running:
            rvr.RVRPollEvents()

        if self.window.input.getKey(moss.KEY_R):
            if self.reloadState:
                self.reloadShaders()

        else:
            self.reloadState = True

        for i in self.objects:
            if self.running and i.script != None:
                if not i.script.update():
                    self.stop()

        for i in self.objects:
            i.transform.pivotx = i.transform.position
            i.transform.pivoty = i.transform.position
            i.transform.pivotz = i.transform.position

        self.updateLights()

        if len(self.lights) != 0:
            # if self.light.position != self.lights[0].transform.position:

            self.light.position.x, self.light.position.y, self.light.position.z = \
                self.lights[0].transform.position.x, self.lights[0].transform.position.y, self.lights[0].transform.position.z
            
            self.light.begin()

            for i in self.objects:
                for mesh in i.meshes:
                    i.meshes[mesh].shader = self.light.depthShader

                i.render(useTexture = False)

                for mesh in i.meshes:
                    i.meshes[mesh].shader = self.shader

            self.light.end()

        for eye in [rvr.RVREyeLeft]:
            self.render(eye)

        if self.running:
            if self.camera.vr:
                rvr.RVRSubmitFramebufferDescriptorsToCompositor()
                rvr.RVRUpdateHMDPoseMatrix()
                self.window.clear()

            if window.input.getKey(moss.KEY_ESCAPE):
                self.stop()

            return
        
        if window.input.getKey(moss.KEY_C) and window.input.getKey(moss.KEY_LEFT_ALT):
            self.camera_model.transform.position = glm.vec3(self.editorCamera.position)
            self.camera_model.transform.rotation.z = self.editorCamera.pitch
            self.camera_model.transform.rotation.y = -self.editorCamera.yaw
        
        self.impl.process_inputs()
        imgui.new_frame()

        self.popup.update()
        self.handleRequests()

        imgui.show_demo_window(True)
        imgui.begin("Scene", None, imgui.WINDOW_MENU_BAR)

        if imgui.begin_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("Exit", None)[0]:
                    window.destroy()

                if imgui.menu_item("Save", None)[0]:
                    self.popup.requestVariable("Save", variables = {"File Path": "project.moss"})

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
                    self.popup.requestVariable("New Point Light", variables = {"Name": f"New Point Light {len(self.lights)}"})

                imgui.end_menu()

            if imgui.begin_menu("Load"):
                if imgui.menu_item("Model", None)[0]:
                    self.popup.requestVariable("Model Loader", variables = {"Name": "New Model", "File Path": "model.obj"})

                imgui.end_menu(),
            
            if imgui.begin_menu("Game"):
                if imgui.menu_item("Run", None)[0]:
                    self.should_start = True

                imgui.end_menu()

            imgui.end_menu_bar()

        self.window.backgroundColor.r, self.window.backgroundColor.g, self.window.backgroundColor.b, self.window.backgroundColor.a = \
            self.skyColor.x * 255, self.skyColor.y * 255, self.skyColor.z * 255, self.skyColor.w * 255

        if imgui.tree_node("Sky"):
            self.skyColor.x, self.skyColor.y, self.skyColor.z, self.skyColor.w = \
                imgui.color_edit4("Color", self.skyColor.x, self.skyColor.y, self.skyColor.z, self.skyColor.w)[1]
            
            imgui.tree_pop()

        if imgui.tree_node("Camera"):
            self.camera.vr = imgui.checkbox("VR", self.camera.vr)[1]

            self.camera_model.transform.position.x, self.camera_model.transform.position.y, self.camera_model.transform.position.z = \
                imgui.drag_float3("Position", self.camera_model.transform.position.x, self.camera_model.transform.position.y, self.camera_model.transform.position.z, 0.1)[1]
                
            if not self.camera.vr:
                self.camera_model.transform.rotation.z, self.camera_model.transform.rotation.y = \
                    imgui.drag_float2("Rotation", self.camera_model.transform.rotation.z, self.camera_model.transform.rotation.y, 1)[1]
                
            else:
                self.camera_model.transform.rotation = glm.vec3(0.0, 0.0, 0.0)
            
            imgui.tree_pop()

        queue = []

        for index, i in enumerate(self.lights):
            if imgui.tree_node(i.name):
                i.transform.position.x, i.transform.position.y, i.transform.position.z = \
                    imgui.drag_float3("Position", i.transform.position.x, i.transform.position.y, i.transform.position.z, 0.1)[1]
                
                i.brightness = imgui.drag_float("Brightness", i.brightness, 0.1, 0.0, 1000000.0)[1]

                i.color.x, i.color.y, i.color.z, i.color.w = \
                    imgui.color_edit4("Color", i.color.x, i.color.y, i.color.z, i.color.w)[1]

                if imgui.button("Delete"):
                    queue.append(index)
                
                imgui.tree_pop()

        for index, i in enumerate(queue):
            self.lights[i - index].delete()
            self.lights.pop(i - index)

        queue = []

        for index, i in enumerate(self.objects):
            if imgui.tree_node(i.name):
                i.transform.position.x, i.transform.position.y, i.transform.position.z = \
                    imgui.drag_float3("Position", i.transform.position.x, i.transform.position.y, i.transform.position.z, 0.1)[1]
                
                i.transform.rotation.x, i.transform.rotation.y, i.transform.rotation.z = \
                    imgui.drag_float3("Rotation", i.transform.rotation.x, i.transform.rotation.y, i.transform.rotation.z, 1.0)[1]
                
                i.transform.scaleVector.x, i.transform.scaleVector.y, i.transform.scaleVector.z = \
                    imgui.drag_float3("Scale", i.transform.scaleVector.x, i.transform.scaleVector.y, i.transform.scaleVector.z, 0.1)[1]
                
                i.color.x, i.color.y, i.color.z, i.color.w = \
                    imgui.color_edit4("Color", i.color.x, i.color.y, i.color.z, i.color.w)[1]
                
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
                    queue.append(index)
                
                imgui.tree_pop()

        for index, i in enumerate(queue):
            self.objects[i - index].delete()
            self.objects.pop(i - index)

        imgui.end()
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def delete(self):
        for i in self.objects:
            i.delete()

        self.camera_model.delete()
        self.shader.delete()
        self.lightShader.delete()
        self.impl.shutdown()

def setup(window):
    global editor
    editor = Editor()

def update(window):
    editor.update()

def exit(window):
    editor.delete()

def main():
    global window
    window = moss.Window("Moss Editor", 1600, 900, moss.Color(0, 0, 0), False, 1)
    window.event(setup)
    window.event(update)
    window.event(exit)
    moss.run()

if __name__ == "__main__":
    main()