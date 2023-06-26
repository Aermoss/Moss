import sys, os, math, imgui

from imgui.integrations.glfw import GlfwRenderer

import moss, glm, ctypes, glfw
import pyglet.gl as gl

sphereVAO = None
indexCount = None

def renderSphere():
    global sphereVAO, indexCount

    if sphereVAO == None:
        sphereVAO, sphereVBO = moss.VAO(), moss.VBO()
        positions, uv, normals, indices = [], [], [], []
        X_SEGMENTS, Y_SEGMENTS = 64, 64

        x = 0

        while x <= X_SEGMENTS:
            y = 0

            while y <= Y_SEGMENTS:
                xSegment = float(x) / float(X_SEGMENTS)
                ySegment = float(y) / float(Y_SEGMENTS)
                xPos = math.cos(xSegment * 2.0 * math.pi) * math.sin(ySegment * math.pi)
                yPos = math.cos(ySegment * math.pi)
                zPos = math.sin(xSegment * 2.0 * math.pi) * math.sin(ySegment * math.pi)
                positions.append(glm.vec3(xPos, yPos, zPos))
                uv.append(glm.vec2(xSegment, ySegment))
                normals.append(glm.vec3(xPos, yPos, zPos))
                y += 1

            x += 1

        oddRow = False
        
        for y in range(Y_SEGMENTS):
            if not oddRow:
                x = 0

                while x <= X_SEGMENTS:
                    indices.append(y * (X_SEGMENTS + 1) + x)
                    indices.append((y + 1) * (X_SEGMENTS + 1) + x)
                    x += 1

            else:
                x = X_SEGMENTS

                while x >= 0:
                    indices.append((y + 1) * (X_SEGMENTS + 1) + x)
                    indices.append(y * (X_SEGMENTS + 1) + x)
                    x -= 1

            oddRow = not oddRow

        indexCount = len(indices)

        data = []

        for i in indices:
            data.append(positions[i].x)
            data.append(positions[i].y)
            data.append(positions[i].z)

            if len(uv) > 0:
                data.append(uv[i].x)
                data.append(uv[i].y)

            if len(normals) > 0:
                data.append(normals[i].x)
                data.append(normals[i].y)
                data.append(normals[i].z)

        data = moss.mkarr(ctypes.c_float, data)

        sphereVAO.bind()
        sphereVBO.bind()
        sphereVBO.bufferData(ctypes.sizeof(data), data)
        sphereVAO.enableAttrib(0, 3, 8 * 4, 0 * 4)
        sphereVAO.enableAttrib(1, 2, 8 * 4, 3 * 4)
        sphereVAO.enableAttrib(2, 3, 8 * 4, 5 * 4)
        sphereVBO.unbind()
        sphereVAO.unbind()

    sphereVAO.bind()
    gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, indexCount)
    sphereVAO.unbind()

cubeVAO = None

def renderCube():
    global cubeVAO, cubeVBO
    
    if cubeVAO is None:
        vertices = moss.mkarr(ctypes.c_float, [
            -1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 0.0,
             1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 1.0,
             1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 0.0,       
             1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 1.0, 1.0,
            -1.0, -1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 0.0,
            -1.0,  1.0, -1.0,  0.0,  0.0, -1.0, 0.0, 1.0,
            -1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 0.0,
             1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 0.0,
             1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 1.0,
             1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 1.0, 1.0,
            -1.0,  1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 1.0,
            -1.0, -1.0,  1.0,  0.0,  0.0,  1.0, 0.0, 0.0,
            -1.0,  1.0,  1.0, -1.0,  0.0,  0.0, 1.0, 0.0,
            -1.0,  1.0, -1.0, -1.0,  0.0,  0.0, 1.0, 1.0,
            -1.0, -1.0, -1.0, -1.0,  0.0,  0.0, 0.0, 1.0,
            -1.0, -1.0, -1.0, -1.0,  0.0,  0.0, 0.0, 1.0,
            -1.0, -1.0,  1.0, -1.0,  0.0,  0.0, 0.0, 0.0,
            -1.0,  1.0,  1.0, -1.0,  0.0,  0.0, 1.0, 0.0,
             1.0,  1.0,  1.0,  1.0,  0.0,  0.0, 1.0, 0.0,
             1.0, -1.0, -1.0,  1.0,  0.0,  0.0, 0.0, 1.0,
             1.0,  1.0, -1.0,  1.0,  0.0,  0.0, 1.0, 1.0,
             1.0, -1.0, -1.0,  1.0,  0.0,  0.0, 0.0, 1.0,
             1.0,  1.0,  1.0,  1.0,  0.0,  0.0, 1.0, 0.0,
             1.0, -1.0,  1.0,  1.0,  0.0,  0.0, 0.0, 0.0,
            -1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 0.0, 1.0,
             1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 1.0, 1.0,
             1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 1.0, 0.0,
             1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 1.0, 0.0,
            -1.0, -1.0,  1.0,  0.0, -1.0,  0.0, 0.0, 0.0,
            -1.0, -1.0, -1.0,  0.0, -1.0,  0.0, 0.0, 1.0,
            -1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 0.0, 1.0,
             1.0,  1.0 , 1.0,  0.0,  1.0,  0.0, 1.0, 0.0,
             1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 1.0, 1.0,
             1.0,  1.0,  1.0,  0.0,  1.0,  0.0, 1.0, 0.0,
            -1.0,  1.0, -1.0,  0.0,  1.0,  0.0, 0.0, 1.0,
            -1.0,  1.0,  1.0,  0.0,  1.0,  0.0, 0.0, 0.0
        ])

        cubeVAO = moss.VAO()
        cubeVBO = moss.VBO()
        cubeVBO.bind()
        cubeVBO.bufferData(len(vertices) * 4, vertices)
        cubeVAO.bind()
        cubeVAO.enableAttrib(0, 3, 8 * 4, 0 * 4)
        cubeVAO.enableAttrib(1, 3, 8 * 4, 3 * 4)
        cubeVAO.enableAttrib(2, 2, 8 * 4, 6 * 4)
        cubeVBO.unbind()
        cubeVAO.unbind()

    cubeVAO.bind()
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
    cubeVAO.unbind()

quadVAO = None

def renderQuad():
    global quadVAO

    if quadVAO is None:
        vertices = moss.mkarr(ctypes.c_float, [
            -1.0,  1.0, 0.0, 0.0, 1.0,
            -1.0, -1.0, 0.0, 0.0, 0.0,
             1.0,  1.0, 0.0, 1.0, 1.0,
             1.0, -1.0, 0.0, 1.0, 0.0
        ])
        
        quadVAO = moss.VAO()
        quadVBO = moss.VBO()
        quadVAO.bind()
        quadVBO.bind()
        quadVBO.bufferData(len(vertices) * 4, vertices)
        quadVAO.enableAttrib(0, 3, 5 * 4, 0 * 4)
        quadVAO.enableAttrib(1, 2, 5 * 4, 3 * 4)
        quadVBO.unbind()
        quadVAO.unbind()

    quadVAO.bind()
    gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
    quadVAO.unbind()

class Light:
    def __init__(self, renderer, position, brightness, color, scale = glm.vec3(0.1), shader = None): 
        self.renderer = renderer
        self.shader = shader if shader is not None else self.renderer.basicShader
        self.position = position
        self.brightness = brightness
        self.color = color
        self.scale = scale

    def render(self):
        self.shader.use()
        self.shader.setUniform1i("useAlbedoMap", 0)
        self.shader.setUniform1i("isTransparent", 0)
        self.shader.setUniform3fv("albedoDefault", glm.value_ptr(self.color))
        model = glm.scale(glm.translate(glm.mat4(1.0), self.position), self.scale)
        self.shader.setUniformMatrix4fv("model", moss.valptr(model))
        self.shader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
        renderSphere()
        self.shader.unuse()

    def delete(self):
        ...

class Renderer:
    def __init__(self, window, hdrTexturePath = None, showLights = False, depthMapSize = glm.ivec2(8192, 8192), intro = True):
        self.window = window
        self.camera = None
        self.showLights = showLights
        self.queue = []
        self.lights = []
        self.console = False
        self.consoleKeyState = True
        self.imgui = False
        self.intro = intro

        imgui.create_context()
        self.impl = GlfwRenderer(self.window.window)
        self.impl.io.ini_file_name = None

        style = imgui.get_style()
        style.colors[imgui.COLOR_TEXT] = imgui.Vec4(1.00, 1.00, 1.00, 1.00)
        style.colors[imgui.COLOR_TEXT_DISABLED] = imgui.Vec4(0.50, 0.50, 0.50, 1.00)
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.39)
        style.colors[imgui.COLOR_CHILD_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.00)
        style.colors[imgui.COLOR_POPUP_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.63)
        style.colors[imgui.COLOR_BORDER] = imgui.Vec4(1.00, 1.00, 1.00, 0.31)
        style.colors[imgui.COLOR_BORDER_SHADOW] = imgui.Vec4(0.00, 0.00, 0.00, 0.00)
        style.colors[imgui.COLOR_FRAME_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.63)
        style.colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = imgui.Vec4(0.23, 0.23, 0.23, 0.63)
        style.colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = imgui.Vec4(0.19, 0.19, 0.19, 0.39)
        style.colors[imgui.COLOR_TITLE_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.63)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = imgui.Vec4(0.00, 0.00, 0.00, 1.00)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_COLLAPSED] = imgui.Vec4(0.00, 0.00, 0.00, 0.35)
        style.colors[imgui.COLOR_MENUBAR_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.78)
        style.colors[imgui.COLOR_SCROLLBAR_BACKGROUND] = imgui.Vec4(0.05, 0.05, 0.05, 0.54)
        style.colors[imgui.COLOR_SCROLLBAR_GRAB] = imgui.Vec4(0.34, 0.34, 0.34, 0.63)
        style.colors[imgui.COLOR_SCROLLBAR_GRAB_HOVERED] = imgui.Vec4(0.50, 0.50, 0.50, 0.63)
        style.colors[imgui.COLOR_SCROLLBAR_GRAB_ACTIVE] = imgui.Vec4(0.38, 0.38, 0.38, 0.63)
        style.colors[imgui.COLOR_CHECK_MARK] = imgui.Vec4(0.22, 0.55, 0.74, 1.00)
        style.colors[imgui.COLOR_SLIDER_GRAB] = imgui.Vec4(0.34, 0.34, 0.34, 0.54)
        style.colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = imgui.Vec4(0.56, 0.56, 0.56, 0.54)
        style.colors[imgui.COLOR_BUTTON] = imgui.Vec4(0.00, 0.00, 0.00, 0.63)
        style.colors[imgui.COLOR_BUTTON_HOVERED] = imgui.Vec4(0.20, 0.22, 0.23, 0.63)
        style.colors[imgui.COLOR_BUTTON_ACTIVE] = imgui.Vec4(0.19, 0.19, 0.19, 0.39)
        style.colors[imgui.COLOR_HEADER] = imgui.Vec4(0.20, 0.20, 0.20, 0.78)
        style.colors[imgui.COLOR_HEADER_HOVERED] = imgui.Vec4(0.29, 0.29, 0.29, 0.78)
        style.colors[imgui.COLOR_HEADER_ACTIVE] = imgui.Vec4(0.19, 0.19, 0.19, 0.15)
        style.colors[imgui.COLOR_SEPARATOR] = imgui.Vec4(0.28, 0.28, 0.28, 0.29)
        style.colors[imgui.COLOR_SEPARATOR_HOVERED] = imgui.Vec4(0.44, 0.44, 0.44, 0.29)
        style.colors[imgui.COLOR_SEPARATOR_ACTIVE] = imgui.Vec4(0.40, 0.44, 0.47, 1.00)
        style.colors[imgui.COLOR_RESIZE_GRIP] = imgui.Vec4(0.28, 0.28, 0.28, 0.29)
        style.colors[imgui.COLOR_RESIZE_GRIP_HOVERED] = imgui.Vec4(0.44, 0.44, 0.44, 0.29)
        style.colors[imgui.COLOR_RESIZE_GRIP_ACTIVE] = imgui.Vec4(0.40, 0.44, 0.47, 1.00)
        style.colors[imgui.COLOR_TAB] = imgui.Vec4(0.00, 0.00, 0.00, 0.52)
        style.colors[imgui.COLOR_TAB_HOVERED] = imgui.Vec4(0.20, 0.20, 0.20, 0.36)
        style.colors[imgui.COLOR_TAB_ACTIVE] = imgui.Vec4(0.14, 0.14, 0.14, 1.00)
        style.colors[imgui.COLOR_TAB_UNFOCUSED] = imgui.Vec4(0.00, 0.00, 0.00, 0.52)
        style.colors[imgui.COLOR_TAB_UNFOCUSED_ACTIVE] = imgui.Vec4(0.14, 0.14, 0.14, 1.00)
        style.colors[imgui.COLOR_PLOT_LINES] = imgui.Vec4(1.00, 0.00, 0.00, 1.00)
        style.colors[imgui.COLOR_PLOT_LINES_HOVERED] = imgui.Vec4(1.00, 0.00, 0.00, 1.00)
        style.colors[imgui.COLOR_PLOT_HISTOGRAM] = imgui.Vec4(1.00, 0.00, 0.00, 1.00)
        style.colors[imgui.COLOR_PLOT_HISTOGRAM_HOVERED] = imgui.Vec4(1.00, 0.00, 0.00, 1.00)
        style.colors[imgui.COLOR_TABLE_HEADER_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.52)
        style.colors[imgui.COLOR_TABLE_BORDER_STRONG] = imgui.Vec4(0.00, 0.00, 0.00, 0.52)
        style.colors[imgui.COLOR_TABLE_BORDER_LIGHT] = imgui.Vec4(0.28, 0.28, 0.28, 0.29)
        style.colors[imgui.COLOR_TABLE_ROW_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.00)
        style.colors[imgui.COLOR_TABLE_ROW_BACKGROUND_ALT] = imgui.Vec4(1.00, 1.00, 1.00, 0.06)
        style.colors[imgui.COLOR_TEXT_SELECTED_BACKGROUND] = imgui.Vec4(0.20, 0.22, 0.23, 1.00)
        style.colors[imgui.COLOR_DRAG_DROP_TARGET] = imgui.Vec4(0.33, 0.67, 0.86, 1.00)
        style.colors[imgui.COLOR_NAV_HIGHLIGHT] = imgui.Vec4(1.00, 0.00, 0.00, 1.00)
        style.colors[imgui.COLOR_NAV_WINDOWING_HIGHLIGHT] = imgui.Vec4(1.00, 0.00, 0.00, 0.70)
        style.colors[imgui.COLOR_NAV_WINDOWING_DIM_BACKGROUND] = imgui.Vec4(1.00, 0.00, 0.00, 0.20)
        style.colors[imgui.COLOR_MODAL_WINDOW_DIM_BACKGROUND] = imgui.Vec4(1.00, 0.00, 0.00, 0.35)

        style.window_padding = imgui.Vec2(6.0, 6.0)
        style.frame_padding = imgui.Vec2(5.0, 2.0)
        style.cell_padding = imgui.Vec2(6.0, 6.0)
        style.item_spacing = imgui.Vec2(6.0, 6.0)
        style.item_inner_spacing = imgui.Vec2(6.0, 6.0)
        style.touch_extra_padding = imgui.Vec2(0.0, 0.0)
        style.window_title_align = imgui.Vec2(0.5, 0.5)
        style.indent_spacing = 25.0
        style.scrollbar_size = 10.0
        style.grab_min_size = 10.0
        style.window_border_size = 1.0
        style.child_border_size = 1.0
        style.popup_border_size = 1.0
        style.frame_border_size = 1.0
        style.tab_border_size = 1.0
        style.window_rounding = 5.0
        style.child_rounding = 4.0
        style.frame_rounding = 2.0
        style.popup_rounding = 4.0
        style.scrollbar_rounding = 9.0
        style.grab_rounding = 2.0
        style.log_slider_deadzone = 4.0
        style.tab_rounding = 4.0

        def scroll_callback(window, x, y):
            self.window.input.scrollX += x
            self.window.input.scrollY += y
            self.impl.io.mouse_wheel_horizontal = x
            self.impl.io.mouse_wheel = y

        glfw.set_scroll_callback(self.window.window, scroll_callback)

        _begin = imgui.begin

        def __begin(*args, **kwargs):
            if not self.imgui:
                self.impl.process_inputs()
                imgui.new_frame()
                
            self.imgui = True
            return _begin(*args, **kwargs)

        imgui.begin = __begin

        self.basicShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/basic.frag")),
            vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert"),
            fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/basic.frag")
        )

        self.window.clear()
        self.basicShader.use()
        self.basicShader.setUniform1i("textureScale", 1)
        self.basicShader.setUniform1i("useAlbedoMap", 1)
        self.basicShader.setUniform3fv("albedoDefault", glm.value_ptr(glm.vec3(0.0, 0.5, 0.5)))
        model = glm.scale(glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)), glm.vec3(0.3 / 3 * 2, 0.12 / 3 * 2, 0.0))
        self.basicShader.setUniformMatrix4fv("model", moss.valptr(model))
        self.basicShader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
        self.basicShader.setUniformMatrix4fv("proj", moss.valptr(glm.mat4(1.0)))
        self.basicShader.setUniformMatrix4fv("view", moss.valptr(glm.mat4(1.0)))
        self.logoTexture = moss.Texture(self.basicShader, os.path.join(os.path.split(moss.__file__)[0], f"res/logo.png"), 0)
        self.logoTexture.bind()
        self.logoTexture.texUnit("albedoMap")
        self.backgroundTransparency = 1.0
        self.logoTransparency = 1.0
        moss.renderQuad()
        self.basicShader.unuse()
        self.window.swapBuffers()

        self.shader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag")),
            vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert"),
            fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag")
        )  

        self.depthShader = moss.Shader(
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.vert")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.frag")),
            moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.geom")),
            vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.vert"),
            fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.frag"),
            geometryFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/depth.geom")
        )

        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glEnable(gl.GL_TEXTURE_CUBE_MAP_SEAMLESS)

        self.depthMapSize = depthMapSize
        self.depthMapFBO = ctypes.c_uint32()
        gl.glGenFramebuffers(1, ctypes.byref(self.depthMapFBO))
        self.depthCubemap = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.depthCubemap))
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.depthCubemap)

        for i in range(6):
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_DEPTH_COMPONENT, self.depthMapSize.x, self.depthMapSize.y, 0, gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, 0)

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

        self.shader.use()
        self.shader.setUniform1i("depthMap", 6)
        self.shader.unuse()

        self.hdrUsed = False
        self.loadHDRTexture(hdrTexturePath)

    def removeHDRTexture(self):
        if self.hdrTexturePath is not None:
            self.shader.use()
            self.shader.setUniform1i("enableIBL", 0)
            self.shader.unuse()
            self.hdrTexturePath = None

    def loadHDRTexture(self, filePath):
        self.hdrTexturePath = filePath

        if self.hdrTexturePath is None:
            return
        
        if self.hdrUsed:
            self.hdrTexture.delete()
            gl.glDeleteTextures(1, ctypes.byref(self.envCubemap))
            gl.glDeleteTextures(1, ctypes.byref(self.brdfLUTTexture))
            gl.glDeleteTextures(1, ctypes.byref(self.prefilterMap))
            gl.glDeleteFramebuffers(1, ctypes.byref(self.captureFBO))
            gl.glDeleteRenderbuffers(1, ctypes.byref(self.captureRBO))

        else:
            self.hdrUsed = True

            self.equirectangularToCubemapShader = moss.Shader(
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/cubemap.vert")),
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/equirectangularToCubemap.frag")),
                vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/cubemap.vert"),
                fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/equirectangularToCubemap.frag")
            )

            self.irradianceShader = moss.Shader(
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/cubemap.vert")),
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/irradianceConvolution.frag")),
                vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/cubemap.vert"),
                fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/irradianceConvolution.frag")
            )

            self.prefilterShader = moss.Shader(
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/cubemap.vert")),
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/prefilter.frag")),
                vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/cubemap.vert"),
                fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/prefilter.frag")
            )

            self.brdfShader = moss.Shader(
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/brdf.vert")),
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/brdf.frag")),
                vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/brdf.vert"),
                fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/brdf.frag")
            )

            self.backgroundShader = moss.Shader(
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/background.vert")),
                moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/background.frag")),
                vertexFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/background.vert"),
                fragmentFilePath = os.path.join(os.path.split(moss.__file__)[0], "shaders/background.frag")
            )

        self.shader.use()
        self.shader.setUniform1i("enableIBL", 1)
        self.shader.setUniform1i("irradianceMap", 7)
        self.shader.setUniform1i("prefilterMap", 8)
        self.shader.setUniform1i("brdfLUT", 9)
        self.shader.unuse()

        self.backgroundShader.use()
        self.backgroundShader.setUniform1i("environmentMap", 10)
        self.backgroundShader.unuse()

        self.captureFBO = ctypes.c_uint32()
        self.captureRBO = ctypes.c_uint32()
        gl.glGenFramebuffers(1, ctypes.byref(self.captureFBO))
        gl.glGenRenderbuffers(1, ctypes.byref(self.captureRBO))
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.captureFBO)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.captureRBO)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT24, 512, 512)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_RENDERBUFFER, self.captureRBO)

        self.hdrTexture = moss.Texture(self.shader, filePath, 0, gl.GL_RGB16F, gl.GL_RGB, gl.GL_CLAMP_TO_EDGE, False, gl.GL_FLOAT, gl.GL_LINEAR, gl.GL_LINEAR)

        self.envCubemap = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.envCubemap))
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.envCubemap)

        for i in range(6):
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB16F, 512, 512, 0, gl.GL_RGB, gl.GL_FLOAT, 0)

        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        captureProjection = glm.perspective(glm.radians(90.0), 1.0, 0.1, 10.0)
        captureViews = [
            glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3( 1.0,  0.0,  0.0), glm.vec3(0.0, -1.0,  0.0)),
            glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3(-1.0,  0.0,  0.0), glm.vec3(0.0, -1.0,  0.0)),
            glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3( 0.0,  1.0,  0.0), glm.vec3(0.0,  0.0,  1.0)),
            glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3( 0.0, -1.0,  0.0), glm.vec3(0.0,  0.0, -1.0)),
            glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3( 0.0,  0.0,  1.0), glm.vec3(0.0, -1.0,  0.0)),
            glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3( 0.0,  0.0, -1.0), glm.vec3(0.0, -1.0,  0.0))
        ]

        self.equirectangularToCubemapShader.use()
        self.equirectangularToCubemapShader.setUniform1i("equirectangularMap", 0)
        self.equirectangularToCubemapShader.setUniformMatrix4fv("proj", glm.value_ptr(captureProjection))

        self.hdrTexture.bind()

        gl.glViewport(0, 0, 512, 512)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.captureFBO)

        for i in range(6):
            self.equirectangularToCubemapShader.setUniformMatrix4fv("view", glm.value_ptr(captureViews[i]))
            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, self.envCubemap, 0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            renderCube()
        
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        self.irradianceMap = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.irradianceMap))
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.irradianceMap)

        for i in range(6):
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB16F, 32, 32, 0, gl.GL_RGB, gl.GL_FLOAT, 0)

        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.captureFBO)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.captureRBO)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT24, 32, 32)

        self.irradianceShader.use()
        self.irradianceShader.setUniform1i("environmentMap", 0)
        self.irradianceShader.setUniformMatrix4fv("proj", glm.value_ptr(captureProjection))
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.envCubemap)

        gl.glViewport(0, 0, 32, 32)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.captureFBO)

        for i in range(6):
            self.irradianceShader.setUniformMatrix4fv("view", glm.value_ptr(captureViews[i]))
            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, self.irradianceMap, 0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            renderCube()

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        self.prefilterMap = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.prefilterMap))
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.prefilterMap)

        for i in range(6):
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB16F, 128, 128, 0, gl.GL_RGB, gl.GL_FLOAT, 0)

        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glGenerateMipmap(gl.GL_TEXTURE_CUBE_MAP)

        self.prefilterShader.use()
        self.prefilterShader.setUniform1i("environmentMap", 0)
        self.prefilterShader.setUniformMatrix4fv("proj", glm.value_ptr(captureProjection))
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.envCubemap)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.captureFBO)
        maxMipLevels = 5

        for mip in range(maxMipLevels):
            mipWidth = int(128 * pow(0.5, mip))
            mipHeight = int(128 * pow(0.5, mip))
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.captureRBO)
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT24, mipWidth, mipHeight)
            gl.glViewport(0, 0, mipWidth, mipHeight)

            roughness = float(mip) / float(maxMipLevels - 1)
            self.prefilterShader.setUniform1f("roughness", roughness)

            for i in range(6):
                self.prefilterShader.setUniformMatrix4fv("view", glm.value_ptr(captureViews[i]))
                gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, self.prefilterMap, mip)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
                renderCube()

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        self.brdfLUTTexture = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.brdfLUTTexture))

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.brdfLUTTexture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RG16F, 512, 512, 0, gl.GL_RG, gl.GL_FLOAT, 0)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.captureFBO)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.captureRBO)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT24, 512, 512)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.brdfLUTTexture, 0)

        gl.glViewport(0, 0, 512, 512)
        self.brdfShader.use()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        renderQuad()

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glViewport(0, 0, self.window.width, self.window.height)

    def bindTextures(self):
        gl.glActiveTexture(gl.GL_TEXTURE6)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.depthCubemap)

        if self.hdrTexturePath is not None:
            gl.glActiveTexture(gl.GL_TEXTURE7)
            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.irradianceMap)
            gl.glActiveTexture(gl.GL_TEXTURE8)
            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.prefilterMap)
            gl.glActiveTexture(gl.GL_TEXTURE9)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.brdfLUTTexture)

    def renderBackground(self):
        self.bindTextures()
        self.shader.use()
        
        if self.hdrTexturePath is not None:
            gl.glDisable(gl.GL_DEPTH_TEST)
            self.backgroundShader.use()
            gl.glActiveTexture(gl.GL_TEXTURE10)
            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.envCubemap)
            # gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.irradianceMap)
            renderCube()
            self.backgroundShader.unuse()
            gl.glEnable(gl.GL_DEPTH_TEST)

        self.shader.unuse()

    def updateLights(self):
        self.shader.use()
        self.shader.setUniform1i("enableShadows", 1)
        self.shader.setUniform1i("lightCount", len(self.lights))

        for index, i in enumerate(self.lights):
            self.shader.setUniform3fv(f"lightPositions[{index}]", glm.value_ptr(i.position))
            self.shader.setUniform3fv(f"lightColors[{index}]", glm.value_ptr(i.color))
            self.shader.setUniform1fv(f"lightBrightnesses[{index}]", ctypes.c_float(i.brightness))

        self.shader.unuse()

    def submit(self, object):
        self.queue.append(object)

    def render(self, camera, updateCamera = True, renderBackground = True):
        self.bindTextures()
        self.updateLights()
        self.camera = camera
        
        if updateCamera:
            for i in [self.shader, self.basicShader] + ([self.backgroundShader] if self.hdrTexturePath is not None else []):
                self.camera.shader = i
                self.camera.updateMatrices()

        if self.hdrTexturePath is not None and renderBackground:
            self.renderBackground()

        gl.glEnable(gl.GL_DEPTH_TEST)

        if self.showLights:
            for i in self.lights:
                i.render()

        if len(self.lights) != 0:
            position = self.lights[0].position
            shadowProj = glm.perspective(glm.radians(90.0), self.depthMapSize.x / self.depthMapSize.y, 0.1, 1000.0)
            shadowTransforms = []
            shadowTransforms.append(shadowProj * glm.lookAt(position, position + glm.vec3(1.0, 0.0, 0.0), glm.vec3(0.0, -1.0, 0.0)))
            shadowTransforms.append(shadowProj * glm.lookAt(position, position + glm.vec3(-1.0, 0.0, 0.0), glm.vec3(0.0, -1.0, 0.0)))
            shadowTransforms.append(shadowProj * glm.lookAt(position, position + glm.vec3(0.0, 1.0, 0.0), glm.vec3(0.0, 0.0, 1.0)))
            shadowTransforms.append(shadowProj * glm.lookAt(position, position + glm.vec3(0.0, -1.0, 0.0), glm.vec3(0.0, 0.0, -1.0)))
            shadowTransforms.append(shadowProj * glm.lookAt(position, position + glm.vec3(0.0, 0.0, 1.0), glm.vec3(0.0, -1.0, 0.0)))
            shadowTransforms.append(shadowProj * glm.lookAt(position, position + glm.vec3(0.0, 0.0, -1.0), glm.vec3(0.0, -1.0, 0.0)))

            gl.glViewport(0, 0, self.depthMapSize.x, self.depthMapSize.y)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.depthMapFBO)
            gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
            self.depthShader.use()

            for i in range(6):
                self.depthShader.setUniformMatrix4fv(f"shadowMatrices[{i}]", glm.value_ptr(shadowTransforms[i]))

            self.depthShader.setUniform3fv("lightPosition", glm.value_ptr(position))

            for i in self.queue:
                for mesh in i.meshes:
                    i.meshes[mesh].shader = self.depthShader

                i.render(useTexture = False)

                for mesh in i.meshes:
                    i.meshes[mesh].shader = self.shader

            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            gl.glViewport(0, 0, self.window.width, self.window.height)
        
        for i in self.queue:
            i.render()

        self.queue = []

        if self.window.input.getKey(moss.KEY_GRAVE_ACCENT):
            if self.consoleKeyState:
                self.consoleKeyState = False
                self.console = not self.console

        else:
            self.consoleKeyState = True

        if self.imgui or self.console:
            if self.console:
                imgui.begin("Console")
                imgui.set_window_size(self.window.width / 2, self.window.height / 2)

                for i in moss.logger.text.split("\n"):
                    imgui.text(i)

                imgui.end()

            imgui.end_frame()
            imgui.render()
            self.impl.render(imgui.get_draw_data())
            self.imgui = False

        if self.intro:
            gl.glEnable(gl.GL_BLEND)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            if self.backgroundTransparency != 0.0:
                self.basicShader.use()
                self.basicShader.setUniform1i("useAlbedoMap", 0)
                self.basicShader.setUniform1i("isTransparent", 1)
                self.basicShader.setUniform1f("transparency", self.backgroundTransparency)
                self.basicShader.setUniform3fv("albedoDefault", glm.value_ptr(glm.vec3(0.0, 0.0, 0.0)))
                model = glm.scale(glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)), glm.vec3(1.0, 1.0, 0.0))
                self.basicShader.setUniformMatrix4fv("model", moss.valptr(model))
                self.basicShader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
                self.basicShader.setUniformMatrix4fv("proj", moss.valptr(glm.mat4(1.0)))
                self.basicShader.setUniformMatrix4fv("view", moss.valptr(glm.mat4(1.0)))
                moss.renderQuad()
                self.basicShader.unuse()

                if self.backgroundTransparency > 0.0:
                    self.backgroundTransparency -= 0.003
                
                if self.backgroundTransparency < 0.0:
                    self.backgroundTransparency = 0.0

            if self.logoTransparency != 0.0:
                self.basicShader.use()
                self.basicShader.setUniform1i("textureScale", 1)
                self.basicShader.setUniform1i("useAlbedoMap", 1)
                self.basicShader.setUniform1i("isTransparent", 1)
                self.basicShader.setUniform1f("transparency", self.logoTransparency)
                model = glm.scale(glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)), glm.vec3(0.3 / 3 * 2, 0.12 / 3 * 2, 0.0))
                self.basicShader.setUniformMatrix4fv("model", moss.valptr(model))
                self.basicShader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
                self.basicShader.setUniformMatrix4fv("proj", moss.valptr(glm.mat4(1.0)))
                self.basicShader.setUniformMatrix4fv("view", moss.valptr(glm.mat4(1.0)))
                self.logoTexture.bind()
                self.logoTexture.texUnit("albedoMap")
                moss.renderQuad()
                self.basicShader.unuse()

                if self.logoTransparency > 0.0:
                    self.logoTransparency -= 0.002
                
                if self.logoTransparency < 0.0:
                    self.logoTransparency = 0.0

            else:
                self.intro = False

            gl.glDisable(gl.GL_BLEND)
            gl.glEnable(gl.GL_DEPTH_TEST)

    def delete(self):
        self.impl.shutdown()
        gl.glDeleteFramebuffers(1, ctypes.byref(self.depthMapFBO))
        gl.glDeleteTextures(1, ctypes.byref(self.depthCubemap))

        for i in self.lights:
            i.delete()

        self.shader.delete()
        self.basicShader.delete()
        self.depthShader.delete()
        
        if self.hdrTexturePath is not None:
            gl.glDeleteTextures(1, ctypes.byref(self.envCubemap))
            gl.glDeleteTextures(1, ctypes.byref(self.brdfLUTTexture))
            gl.glDeleteTextures(1, ctypes.byref(self.prefilterMap))
            gl.glDeleteFramebuffers(1, ctypes.byref(self.captureFBO))
            gl.glDeleteRenderbuffers(1, ctypes.byref(self.captureRBO))

            self.hdrTexture.delete()
            self.equirectangularToCubemapShader.delete()
            self.irradianceShader.delete()
            self.prefilterShader.delete()
            self.brdfShader.delete()
            self.backgroundShader.delete()