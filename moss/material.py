import moss, glm

class Material:
    def __init__(self, shader, illumination = None, roughness = 1.0, metallic = 1.0, albedo = glm.vec3(1.0, 1.0, 1.0),
                 ambient = None, specular = None, emission = None, dissolve = None, roughnessMap = None, albedoMap = None,
                 specularMap = None, ambientMap = None, dissolveMap = None, normalMap = None, emissionMap = None, metallicMap = None):
        self.shader = shader
        self.illumination = illumination
        self.roughness = roughness
        self.metallic = metallic
        self.albedo = albedo
        self.ambient = ambient
        self.specular = specular
        self.emission = emission
        self.dissolve = dissolve
        self.roughnessMap = roughnessMap
        self.albedoMap = albedoMap
        self.specularMap = specularMap
        self.ambientMap = ambientMap
        self.dissolveMap = dissolveMap
        self.normalMap = normalMap
        self.emissionMap = emissionMap
        self.metallicMap = metallicMap
        self.update()

    def update(self):
        for index, i in enumerate(["albedoMap", "roughnessMap", "metallicMap", "normalMap", "specularMap", "ambientMap"]):
            if getattr(self, i) is not None and isinstance(getattr(self, i), str):
                setattr(self, i, moss.Texture(self.shader, getattr(self, i), index))

    def delete(self):
        for index, i in enumerate(["albedoMap", "roughnessMap", "metallicMap", "normalMap", "specularMap", "ambientMap"]):
            if getattr(self, i) is not None and not isinstance(getattr(self, i), str):
                getattr(self, i).delete()