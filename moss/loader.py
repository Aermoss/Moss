import moss, glm, os, ctypes

def loadMTL(shader, filePath):
    materials, current = {}, ""
    names = {
        "illumination": (["illum"], int),
        "roughness": (["Pr", "Ns"], float),
        "metallic": (["Pm"], float),
        "albedo": (["Kd"], glm.vec3),
        "ambient": (["Ka"], glm.vec3),
        "specular": (["Ks"], glm.vec3),
        "emission": (["Ke"], glm.vec3),
        "dissolve": (["d"], float),
        "roughnessMap": (["map_Pr", "map_Ns"], str),
        "albedoMap": (["map_Kd"], str),
        "specularMap": (["map_Ks"], str),
        "ambientMap": (["map_Ka"], str),
        "dissolveMap": (["map_d"], str),
        "normalMap": (["map_Bump", "map_bump", "bump"], str),
        "emissionMap": (["map_Ke"], str),
        "metallicMap": (["map_refl", "refl", "map_Pm"], str)
    }

    attributes = {}

    for i in names:
        for j in names[i][0]:
            attributes[j] = (i, names[i][1])

    for line in moss.readFile(filePath).split("\n"):
        values = line.split(" ")

        if values[0] == "newmtl":
            current = values[1]
            materials[current] = moss.Material(shader)

        elif values[0] in attributes:
            if attributes[values[0]][1] == str:
                setattr(materials[current], attributes[values[0]][0], os.path.join(os.path.split(filePath)[0], " ".join(values[1:])))

            if attributes[values[0]][1] == float:
                setattr(materials[current], attributes[values[0]][0], float(values[1]) / 1000 if attributes[values[0]][0] == "roughness" else float(values[1]))

            if attributes[values[0]][1] == glm.vec3:
                setattr(materials[current], attributes[values[0]][0], glm.vec3(*[float(i) for i in values[1:]]))

    for i in materials:
        materials[i].update()

    moss.logger.log(moss.INFO, f"loaded MTL file: \"{os.path.split(filePath)[1]}\".")
    return materials

def loadOBJ(shader, filePath):
    materials, meshes, data = {}, {}, {"v": [], "vt": [], "vn": []}
    current_mesh, current_material = None, None

    for line in moss.readFile(filePath).split("\n"):
        values = line.split(" ")

        if values[0] in list(data.keys()):
            data[values[0]].append([float(i) for i in values[1:] if i != ""])

        elif values[0] == "f":
            if current_mesh == None:
                meshes[None] = {}

            if current_material == None and current_material not in materials:
                materials[current_material] = moss.Material(shader)

            if current_material not in meshes[current_mesh]:
                meshes[current_mesh][current_material] = []

            # for i in values[1:]:
            #     if i == "": continue
            #     indices = i.split("/")
            #     
            #     meshes[current_mesh][current_material] += data["v"][int(indices[0]) - 1] \
            #         + (data["vt"][int(indices[1]) - 1][:2] if indices[1] != "" else [0.0, 0.0]) \
            #             + (data["vn"][int(indices[2]) - 1] if indices[2] != "" else [0.0, 0.0, 0.0]) if len(indices) == 3 else []

            i = 2

            while i < len(values[1:]):
                for j in [0, i - 1, i]:
                    if values[1:][j] == "": continue
                    indices = values[1:][j].split("/")

                    meshes[current_mesh][current_material] += data["v"][int(indices[0]) - 1] \
                        + (data["vt"][int(indices[1]) - 1][:2] if indices[1] != "" else [0.0, 0.0]) \
                            + (data["vn"][int(indices[2]) - 1] if indices[2] != "" else [0.0, 0.0, 0.0]) if len(indices) == 3 else []

                i += 1

        elif values[0] == "mtllib":
            materials = loadMTL(shader, os.path.join(os.path.split(filePath)[0], " ".join(values[1:])))

        elif values[0] == "usemtl":
            if current_mesh == "":
                current_mesh = "main"
                meshes[current_mesh] = {}

            current_material = " ".join(values[1:])
            meshes[current_mesh][current_material] = []

        elif values[0] == "o":
            current_material = None
            current_mesh = " ".join(values[1:])
            meshes[current_mesh] = {}

    for mesh in meshes:
        for material in meshes[mesh]:
            meshes[mesh][material] = moss.mkarr(ctypes.c_float, meshes[mesh][material])
    
    moss.logger.log(moss.INFO, f"loaded OBJ file: \"{os.path.split(filePath)[1]}\".")
    return meshes, materials