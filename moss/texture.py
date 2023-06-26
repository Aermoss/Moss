import moss, ctypes, os

import stbipy as stb
import pyglet.gl as gl

class TextureManager:
    def __init__(self):
        self.textures = {}

    def register(self, path, texture):
        if path in self.textures:
            self.textures[path]["shared"] = True
            return self.textures[path]["texture"]
        
        self.textures[path] = {"texture": texture, "shared": False}

    def remove(self, path):
        if self.textures[path]["shared"]:
            return False
        
        del self.textures[path]
        return True

textureManager = TextureManager()

class Texture:
    def __init__(self, shader, filePath, slot, internalFormat = gl.GL_RGBA, format = None, wrap = gl.GL_REPEAT, mipmap = True,
                 pixelType = gl.GL_UNSIGNED_BYTE, minFilter = gl.GL_LINEAR_MIPMAP_LINEAR, magFilter = gl.GL_LINEAR):
        self.shader = shader
        self.filePath = filePath
        self.slot = slot
        self.internalFormat = internalFormat
        self.format = format
        self.pixelType = pixelType
        self.wrap = wrap
        self.mipmap = mipmap
        self.minFilter = minFilter
        self.magFilter = magFilter

        result = textureManager.register(self.filePath, self)

        if result is not None:
            self.tex = result.tex
            return

        self.width, self.height, self.channels = ctypes.c_int32(), ctypes.c_int32(), ctypes.c_int32()
        stb.stbi_set_flip_vertically_on_load(True)
        data = {gl.GL_UNSIGNED_BYTE: stb.stbi_load, gl.GL_FLOAT: stb.stbi_loadf}[self.pixelType] \
            (self.filePath.encode(), ctypes.byref(self.width), ctypes.byref(self.height), ctypes.byref(self.channels), 0)
        self.format = self.format if self.format is not None else \
            {1: gl.GL_RED, 2: gl.GL_RG, 3: gl.GL_RGB, 4: gl.GL_RGBA}[self.channels.value]
        self.tex = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.tex))
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, self.minFilter)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, self.magFilter)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, self.wrap)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, self.wrap)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, self.internalFormat, self.width, self.height, 0, self.format, self.pixelType, data)
        if self.mipmap: gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        stb.stbi_image_free(data)

        moss.logger.log(moss.INFO, f"loaded image file: \"{os.path.split(self.filePath)[1]}\", texture id: {self.tex.value}.")

    def texUnit(self, name):
        self.shader.setUniform1i(name, self.slot)

    def bind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex)

    def unbind(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def delete(self):
        if textureManager.remove(self.filePath):
            gl.glDeleteTextures(1, ctypes.byref(self.tex))
            moss.logger.log(moss.INFO, f"deleted texture: \"{os.path.split(self.filePath)[1]}\", texture id: {self.tex.value}.")