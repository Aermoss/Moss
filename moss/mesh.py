import moss, glm, ctypes
import pyglet.gl as gl

class Mesh:
    def __init__(self, shader, submeshes, materials, transform = None):
        self.shader = shader
        self.submeshes = {}
        self.transform = transform

        if self.transform == None:
            self.transform = moss.Transform()

        for i in submeshes:
            self.shader.use()
            vao, vbo = moss.VAO(), moss.VBO()
            vao.bind()
            vbo.bind()
            vbo.bufferData(ctypes.sizeof(submeshes[i]), submeshes[i])
            vao.enableAttrib(0, 3, 8 * ctypes.sizeof(ctypes.c_float), 0 * ctypes.sizeof(ctypes.c_float))
            vao.enableAttrib(1, 2, 8 * ctypes.sizeof(ctypes.c_float), 3 * ctypes.sizeof(ctypes.c_float))
            vao.enableAttrib(2, 3, 8 * ctypes.sizeof(ctypes.c_float), 5 * ctypes.sizeof(ctypes.c_float))
            vao.unbind()
            vbo.unbind()
            self.shader.unuse()
            self.submeshes[i] = {
                "count": int(len(submeshes[i]) / 8),
                "material": materials[i],
                "vao": vao, "vbo": vbo,
                "textureScale": 1, "rotateTexture": 0,
                "cullFace": True, "inverseNormal": 0
            }

    def render(self, useTexture = True):
        gl.glEnable(gl.GL_DEPTH_TEST)

        for i in self.submeshes:
            if self.submeshes[i]["cullFace"]:
                gl.glEnable(gl.GL_CULL_FACE)

            self.shader.use()
            self.shader.setUniform1i("textureScale", self.submeshes[i]["textureScale"])
            self.shader.setUniform1i("rotateTexture", self.submeshes[i]["rotateTexture"])
            self.shader.setUniform1i("inverseNormal", self.submeshes[i]["inverseNormal"])

            for j in ["albedoMap", "roughnessMap", "metallicMap", "normalMap", "specularMap", "ambientMap"]:
                self.shader.setUniform1i("use" + j[0].capitalize() + j[1:], 1 if getattr(self.submeshes[i]["material"], j) is not None and useTexture else 0)
                
                if getattr(self.submeshes[i]["material"], j) is not None and useTexture:
                    getattr(self.submeshes[i]["material"], j).texUnit(j)
                    getattr(self.submeshes[i]["material"], j).bind()

            self.shader.setUniform3fv("albedoDefault", glm.value_ptr(self.submeshes[i]["material"].albedo))
            self.shader.setUniform1f("roughnessDefault", self.submeshes[i]["material"].roughness)
            self.shader.setUniform1f("metallicDefault", self.submeshes[i]["material"].metallic)
            self.shader.setUniform1f("ambientDefault", 1.0)
            model = self.transform.get()
            self.shader.setUniformMatrix4fv("model", moss.valptr(model))
            self.shader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
            self.submeshes[i]["vao"].bind()
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.submeshes[i]["count"])
            self.submeshes[i]["vao"].unbind()

            for j in ["albedoMap", "roughnessMap", "metallicMap", "normalMap", "specularMap", "ambientMap"]:
                if getattr(self.submeshes[i]["material"], j) is not None and useTexture:
                    getattr(self.submeshes[i]["material"], j).unbind()

            self.shader.unuse()

        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_DEPTH_TEST)

    def delete(self):
        for i in self.submeshes:
            self.submeshes[i]["vao"].delete()
            self.submeshes[i]["vbo"].delete()