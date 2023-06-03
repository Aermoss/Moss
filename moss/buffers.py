import moss, ctypes
import pyglet.gl as gl

class VAO:
    def __init__(self):
        self.vao = ctypes.c_uint32()
        gl.glGenVertexArrays(1, ctypes.byref(self.vao))

    def enableAttrib(self, location, size, stride, pointer, type = gl.GL_FLOAT, normalized = gl.GL_FALSE):
        gl.glEnableVertexAttribArray(location)
        gl.glVertexAttribPointer(location, size, type, normalized, stride, ctypes.c_void_p(pointer))

    def bind(self):
        gl.glBindVertexArray(self.vao)

    def unbind(self):
        gl.glBindVertexArray(0)

    def delete(self):
        gl.glDeleteVertexArrays(1, ctypes.byref(self.vao))

class VBO:
    def __init__(self):
        self.vbo = ctypes.c_uint32()
        gl.glGenBuffers(1, ctypes.byref(self.vbo))

    def bufferData(self, size, data, target = gl.GL_STATIC_DRAW):
        gl.glBufferData(gl.GL_ARRAY_BUFFER, size, data, target)

    def bind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

    def unbind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def delete(self):
        gl.glDeleteBuffers(1, ctypes.byref(self.vbo))

class IBO:
    def __init__(self):
        self.ibo = ctypes.c_uint32()
        gl.glGenBuffers(1, ctypes.byref(self.ibo))

    def bufferData(self, size, data, target = gl.GL_STATIC_DRAW):
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, size, data, target)

    def bind(self):
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo)

    def unbind(self):
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

    def delete(self):
        gl.glDeleteBuffers(1, ctypes.byref(self.ibo))