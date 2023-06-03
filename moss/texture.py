import moss, ctypes

import PIL.Image
import pyglet.gl as gl

class Texture:
    def __init__(self, shader, filePath, slot):
        self.shader = shader
        self.slot = slot
        image = PIL.Image.open(filePath).convert("RGBA").transpose(PIL.Image.FLIP_TOP_BOTTOM)
        self.tex = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.tex))
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, image.size[0], image.size[1], 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image.tobytes())
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def texUnit(self, name):
        self.shader.setUniform1i(name, self.slot)

    def bind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex)

    def unbind(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def delete(self):
        gl.glDeleteTextures(1, ctypes.byref(self.tex))

class TextureArray:
    def __init__(self, shader, filePaths, slot, length, width, height):
        self.shader = shader
        self.slot = slot
        self.tex = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.tex))
        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.tex)
        gl.glTexImage3D(gl.GL_TEXTURE_2D_ARRAY, 1, gl.GL_RGBA, width, height, length, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
        gl.glTexParameteri(gl.GL_TEXTURE_2D_ARRAY, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D_ARRAY, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D_ARRAY, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D_ARRAY, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

        for index, i in enumerate(filePaths):
            if i == None: continue
            print(i, index)
            image = PIL.Image.open(i).convert("RGBA").transpose(PIL.Image.FLIP_TOP_BOTTOM)
            gl.glTexSubImage3D(gl.GL_TEXTURE_2D_ARRAY, 0, 0, 0, index, 4096, 4096, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image.tobytes())

        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, 0)

    def bind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.slot)
        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.tex)

    def unbind(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, 0)

    def delete(self):
        gl.glDeleteTextures(1, ctypes.byref(self.tex))