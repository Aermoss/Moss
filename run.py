import moss, pickle, glm, sys, rsxpy, os, ctypes

import pyglet.gl as gl

class Script:
    def __init__(self, objects, models, window, camera, object, filePath, id):
        self.objects = objects
        self.models = models
        self.window = window
        self.camera = camera
        self.objects = objects
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
                "objects": self.objects,
                "models": self.models,
                "context": moss.context,
                "window": self.window,
                "camera": self.camera
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
    
class Light(moss.Model):
    def __init__(self, shader):
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

        self.color = glm.vec3(1.0)
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
        self.lightShader.setUniform4fv("color", glm.value_ptr(glm.vec4(self.color.x, self.color.y, self.color.z, 1.0)))
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

data = pickle.loads(open("test.moss", "rb").read())

def setup(window):
    global shader, lightShader, camera, objects, lights, models, light

    shader = moss.Shader(
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
    )

    lightShader = moss.Shader(
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.vert")),
        moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.frag"))
    )

    camera = moss.Camera(shader)
    camera.vr = data["camera"]["vr"]
    camera.position = glm.vec3(*[data["camera"]["position"]])
    camera.pitch = data["camera"]["rotation"][2]
    camera.yaw = -data["camera"]["rotation"][1]

    light = Light(lightShader)

    models = {}

    for i in data["models"]:
        models[i] = (moss.loadOBJ(data["models"][i]), data["models"][i])

    objects = []

    for i in data["objects"]:
        model = moss.Model(shader,
            meshes = models[data["objects"][i]["model"]][0][0],
            materials = models[data["objects"][i]["model"]][0][1]
        )

        position = glm.vec3(*data["objects"][i]["position"])
        rotation = glm.vec3(*data["objects"][i]["rotation"])
        scale = glm.vec3(*data["objects"][i]["scale"])
        color = glm.vec4(*data["objects"][i]["color"])

        model.transform.position, model.transform.rotation, model.transform.scaleVector, model.color, model.model, model.name = \
            position, rotation, scale, color, data["objects"][i]["model"], i
        
        temp, equal = None, True
        
        for j in model.meshes:
            for k in model.meshes[j].parts:
                if temp == None:
                    temp = model.meshes[j].parts[k]["material"]["albedo"]

                if model.meshes[j].parts[k]["material"]["albedo"] != temp or \
                    "albedoMap" in model.meshes[j].parts[k]["material"]: equal = False

        if equal:
            for j in model.meshes:
                for k in model.meshes[j].parts:
                    model.meshes[j].parts[k]["material"]["albedo"] = model.color

        model.script = Script(objects, models, window, camera, object, data["objects"][i]["script"], len(objects)) if data["objects"][i]["script"] != None else None
        model.initialValues = {}
        objects.append(model)

        if model.script != None:
            if not model.script.setup():
                sys.exit(-1)

    lights = []

    for i in data["lights"]:
        lights.append({
            "name": i,
            "brightness": data["lights"][i]["brightness"],
            "color": glm.vec4(*(data["lights"][i]["color"])),
            "position": glm.vec3(*(data["lights"][i]["position"])),
            "rotation": glm.vec3(*(data["lights"][i]["rotation"]))
        })

def update(window):
    window.clear()
    camera.createViewMatrix()
    camera.updateMatrices()

    lightPositions = []
    lightColors = []
    lightBrightnesses = []

    for i in lights:
        lightPositions += [i["position"].x, i["position"].y, i["position"].z]
        lightColors += [i["color"].x, i["color"].y, i["color"].z]
        lightBrightnesses += [i["brightness"]]

    shader.use()
    shader.setUniform1i("enableShadows", 1)
    shader.setUniform1i("lightCount", len(lights))

    if len(lights) != 0:
        shader.setUniform3fv("lightPositions", (ctypes.c_float * len(lightPositions))(*lightPositions), len(lights))
        shader.setUniform3fv("lightColors", (ctypes.c_float * len(lightColors))(*lightColors), len(lights))
        shader.setUniform1fv("lightBrightnesses", (ctypes.c_float * len(lightBrightnesses))(*lightBrightnesses), len(lights))

    shader.unuse()

    light.transform.position = lights[0]["position"]
    light.color = lights[0]["color"]
    light.brightness = lights[0]["brightness"]
    light.begin()

    for i in objects:
        if i.script != None:
            if not i.script.update():
                sys.exit(-1)

        i.transform.pivotx = i.transform.position
        i.transform.pivoty = i.transform.position
        i.transform.pivotz = i.transform.position

        for j in i.meshes:
            i.meshes[j].shader = light.depthShader

        i.render()

        for j in i.meshes:
            i.meshes[j].shader = shader

    light.end()
    light.update(shader)

    for i in objects:
        i.render()

def exit(window):
    for i in objects:
        i.delete()

    shader.delete()

def main(argv):
    global window
    window = moss.Window("Moss Window", 1200, 600, moss.Color(*data["sky"]["color"]), False, 1)
    window.event(setup)
    window.event(update)
    window.event(exit)
    moss.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))