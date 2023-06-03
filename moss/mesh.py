import moss, glm, ctypes
import pyglet.gl as gl

class Mesh:
    def __init__(self, shader, parts, materials, transform = None):
        self.shader = shader
        self.parts = {}
        self.transform = transform

        if self.transform == None:
            self.transform = moss.Transform()

        for i in parts:
            self.shader.use()
            vao, vbo = moss.VAO(), moss.VBO()
            vao.bind()
            vbo.bind()
            vbo.bufferData(ctypes.sizeof(parts[i]), parts[i])
            vao.enableAttrib(0, 3, 8 * ctypes.sizeof(ctypes.c_float), 0 * ctypes.sizeof(ctypes.c_float))
            vao.enableAttrib(1, 2, 8 * ctypes.sizeof(ctypes.c_float), 3 * ctypes.sizeof(ctypes.c_float))
            vao.enableAttrib(2, 3, 8 * ctypes.sizeof(ctypes.c_float), 5 * ctypes.sizeof(ctypes.c_float))
            vao.unbind()
            vbo.unbind()
            self.shader.unuse()
            self.parts[i] = {
                "count": int(len(parts[i]) / 8),
                "material": materials[i],
                "vao": vao, "vbo": vbo,
                "textures": {}, "textureScale": 1,
                "rotateTexture": 0, "cullFace": True,
                "inverseNormal": 0
            }

            if "albedoMap" in materials[i]:
                self.parts[i]["textures"]["albedoMap"] = moss.Texture(self.shader, materials[i]["albedoMap"], 0)

            if "roughnessMap" in materials[i]:
                self.parts[i]["textures"]["roughnessMap"] = moss.Texture(self.shader, materials[i]["roughnessMap"], 1)

            if "metallicMap" in materials[i]:
                self.parts[i]["textures"]["metallicMap"] = moss.Texture(self.shader, materials[i]["metallicMap"], 2)

            if "normalMap" in materials[i]:
                self.parts[i]["textures"]["normalMap"] = moss.Texture(self.shader, materials[i]["normalMap"], 3)

            if "specularMap" in materials[i]:
                self.parts[i]["textures"]["specularMap"] = moss.Texture(self.shader, materials[i]["specularMap"], 4)

            if "ambientMap" in materials[i]:
                self.parts[i]["textures"]["ambientMap"] = moss.Texture(self.shader, materials[i]["ambientMap"], 5)

    def render(self, useTexture = True):
        gl.glEnable(gl.GL_DEPTH_TEST)

        for i in self.parts:
            if self.parts[i]["cullFace"]:
                gl.glEnable(gl.GL_CULL_FACE)

            self.shader.use()

            self.shader.setUniform1i("textureScale", self.parts[i]["textureScale"])
            self.shader.setUniform1i("rotateTexture", self.parts[i]["rotateTexture"])
            self.shader.setUniform1i("inverseNormal", self.parts[i]["inverseNormal"])
            self.shader.setUniform1i("useAlbedoMap", 1 if "albedoMap" in self.parts[i]["textures"] and useTexture else 0)
            self.shader.setUniform1i("useRoughnessMap", 1 if "roughnessMap" in self.parts[i]["textures"] and useTexture else 0)
            self.shader.setUniform1i("useMetallicMap", 1 if "metallicMap" in self.parts[i]["textures"] and useTexture else 0)
            self.shader.setUniform1i("useNormalMap", 1 if "normalMap" in self.parts[i]["textures"] and useTexture else 0)
            self.shader.setUniform1i("useSpecularMap", 1 if "specularMap" in self.parts[i]["textures"] and useTexture else 0)
            self.shader.setUniform1i("useAmbientMap", 1 if "ambientMap" in self.parts[i]["textures"] and useTexture else 0)

            if useTexture:
                for j in self.parts[i]["textures"]:
                    self.parts[i]["textures"][j].bind()
                    self.parts[i]["textures"][j].texUnit(j)

            self.shader.setUniform3fv("albedoDefault", glm.value_ptr(self.parts[i]["material"]["albedo"]))
            self.shader.setUniform1f("roughnessDefault", self.parts[i]["material"]["roughness"])
            self.shader.setUniform1f("metallicDefault", 0.5)
            self.shader.setUniform1f("ambientDefault", 1.0)
            model = self.transform.get()
            self.shader.setUniformMatrix4fv("model", moss.valptr(model))
            self.shader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
            self.parts[i]["vao"].bind()
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.parts[i]["count"])
            self.parts[i]["vao"].unbind()

            if useTexture:
                for j in self.parts[i]["textures"]:
                    self.parts[i]["textures"][j].unbind()

            self.shader.unuse()

        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_DEPTH_TEST)

    def delete(self):
        for i in self.parts:
            self.parts[i]["vao"].delete()
            self.parts[i]["vbo"].delete()