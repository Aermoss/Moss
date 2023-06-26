import moss, ctypes, os
import pyglet.gl as gl

class Shader:
    def __init__(self, vertexSource = None, fragmentSource = None, geometrySource = None,
                 vertexFilePath = None, fragmentFilePath = None, geometryFilePath = None):
        self.vertexSource = vertexSource
        self.fragmentSource = fragmentSource
        self.geometrySource = geometrySource
        self.vertexFilePath = vertexFilePath
        self.fragmentFilePath = fragmentFilePath
        self.geometryFilePath = geometryFilePath

        if self.vertexSource == None and self.vertexFilePath != None:
            self.vertexSource = moss.readFile(self.vertexFilePath)

        if self.fragmentSource == None and self.fragmentFilePath != None:
            self.fragmentSource = moss.readFile(self.fragmentFilePath)

        if self.geometrySource == None and self.geometryFilePath != None:
            self.geometrySource = moss.readFile(self.geometryFilePath)

        self.program = gl.glCreateProgram()
        shaders = [
            self.compileShader(gl.GL_VERTEX_SHADER, self.vertexSource),
            self.compileShader(gl.GL_FRAGMENT_SHADER, self.fragmentSource)
        ] + ([self.compileShader(gl.GL_GEOMETRY_SHADER, self.geometrySource)] if self.geometrySource != None else [])
        
        for i in shaders:
            if i != 0: gl.glAttachShader(self.program, i)

        gl.glLinkProgram(self.program)

        for i in shaders:
            if i != 0: gl.glDetachShader(self.program, i)

        for i in shaders:
            if i != 0: gl.glDeleteShader(i)

        status = ctypes.c_int32()
        gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS, status)

        if status.value != gl.GL_TRUE:
            length = ctypes.c_int32()
            gl.glGetProgramiv(self.program, gl.GL_INFO_LOG_LENGTH, ctypes.byref(length))
            buffer = ctypes.create_string_buffer(length.value)
            gl.glGetProgramInfoLog(self.program, length, None, buffer)
            moss.logger.log(moss.ERROR, "program linking error:\n" + buffer.value.decode()[:-1].replace("ERROR:", "opengl: error:"))
            return

        moss.context.getCurrentWindow().registerShader(self)
        moss.logger.log(moss.INFO, f"shader program linked successfully, id: {self.program}.")

    def getAttribLocation(self, name):
        return gl.glGetAttribLocation(self.program, name.encode())

    def getUniformLocation(self, name):
        return gl.glGetUniformLocation(self.program, name.encode())
    
    def setUniform1i(self, name, x):
        gl.glUniform1i(self.getUniformLocation(name), x)

    def setUniform1iv(self, name, value, count = 1):
        gl.glUniform1iv(self.getUniformLocation(name), count, value)

    def setUniform2i(self, name, x, y):
        gl.glUniform2i(self.getUniformLocation(name), x, y)

    def setUniform2iv(self, name, value, count = 1):
        gl.glUniform2iv(self.getUniformLocation(name), count, value)

    def setUniform3i(self, name, x, y, z):
        gl.glUniform3i(self.getUniformLocation(name), x, y, z)

    def setUniform3iv(self, name, value, count = 1):
        gl.glUniform3iv(self.getUniformLocation(name), count, value)

    def setUniform4i(self, name, x, y, z, w):
        gl.glUniform4i(self.getUniformLocation(name), x, y, z, w)

    def setUniform4iv(self, name, value, count = 1):
        gl.glUniform4iv(self.getUniformLocation(name), count, value)
    
    def setUniform1f(self, name, x):
        gl.glUniform1f(self.getUniformLocation(name), x)

    def setUniform1fv(self, name, value, count = 1):
        gl.glUniform1fv(self.getUniformLocation(name), count, value)

    def setUniform2f(self, name, x, y):
        gl.glUniform2f(self.getUniformLocation(name), x, y)

    def setUniform2fv(self, name, value, count = 1):
        gl.glUniform2fv(self.getUniformLocation(name), count, value)

    def setUniform3f(self, name, x, y, z):
        gl.glUniform3f(self.getUniformLocation(name), x, y, z)

    def setUniform3fv(self, name, value, count = 1):
        gl.glUniform3fv(self.getUniformLocation(name), count, value)

    def setUniform4f(self, name, x, y, z, w):
        gl.glUniform4f(self.getUniformLocation(name), x, y, z, w)

    def setUniform4fv(self, name, value, count = 1):
        gl.glUniform4fv(self.getUniformLocation(name), count, value)

    def setUniformMatrix2fv(self, name, value, count = 1):
        gl.glUniformMatrix2fv(self.getUniformLocation(name), count, gl.GL_FALSE, value)

    def setUniformMatrix3fv(self, name, value, count = 1):
        gl.glUniformMatrix3fv(self.getUniformLocation(name), count, gl.GL_FALSE, value)

    def setUniformMatrix4fv(self, name, value, count = 1):
        gl.glUniformMatrix4fv(self.getUniformLocation(name), count, gl.GL_FALSE, value)

    def use(self):
        gl.glUseProgram(self.program)

    def unuse(self):
        gl.glUseProgram(0)

    def delete(self):
        moss.logger.log(moss.INFO, f"shader program deleted successfully, id: {self.program}.")
        moss.context.getCurrentWindow().removeShader(self)
        gl.glDeleteProgram(self.program)

    def reload(self):
        if self.vertexFilePath != None:
            self.vertexSource = moss.readFile(self.vertexFilePath)

        if self.fragmentFilePath != None:
            self.fragmentSource = moss.readFile(self.fragmentFilePath)

        if self.geometryFilePath != None:
            self.geometrySource = moss.readFile(self.geometryFilePath)

        self.delete()
        self.__init__(self.vertexSource, self.fragmentSource, self.geometrySource)
        
    def compileShader(self, type, shaderSourceStr):
        shaderSourceBuffer = ctypes.create_string_buffer(shaderSourceStr.encode())
        shaderSource = ctypes.cast(ctypes.pointer(ctypes.pointer(shaderSourceBuffer)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
        shader = gl.glCreateShader(type)
        gl.glShaderSource(shader, 1, shaderSource, None)
        gl.glCompileShader(shader)

        status = ctypes.c_int32()
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ctypes.byref(status))

        type = {35633: "vertex", 36313: "geometry", 35632: "fragment"}[type]
        filePath = os.path.split(self.vertexFilePath)[1] if type == "vertex" and self.vertexFilePath != None else \
                  (os.path.split(self.fragmentFilePath)[1] if type == "fragment" and self.fragmentFilePath != None else \
                  (os.path.split(self.geometryFilePath)[1] if type == "geometry" and self.geometryFilePath != None else None))

        if status.value != gl.GL_TRUE:
            length = ctypes.c_int32()
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ctypes.byref(length))
            buffer = ctypes.create_string_buffer(length.value)
            gl.glGetShaderInfoLog(shader, length, None, buffer)
            moss.logger.log(moss.ERROR, f"failed to compile {type} shader" + (": \"" + filePath + "\"" if filePath != None else "") + ":\n" \
                                                                        + buffer.value.decode()[:-2].replace("ERROR:", "opengl: error:"))
            return 0
        
        moss.logger.log(moss.INFO, f"{type} shader" + (": \"" + filePath + "\" " if filePath != None else " ") + f"compiled successfully, id: {shader}.")
        return shader