from rsxpy.tools import *

import glfw, glm, rvr, moss

create_library("moss_api")

@create_function(IntType(), {})
def getObjectID(environ):
    return environ["context"].api["id"]

@create_function(IntType(), {"name": StringType()})
def getObjectIDByName(environ):
    for index, i in enumerate(environ["context"].api["objects"]):
        if i.name == environ["args"]["name"]:
            return index
        
    return -1

@create_function(IntType(), {})
def getWindowID(environ):
    return environ["context"].api["window"].id

@create_function(IntType(), {"id": IntType()})
def getWidth(environ):
    return glfw.get_window_size(environ["context"].api["window"].window)[0]

@create_function(IntType(), {"id": IntType()})
def getHeight(environ):
    return glfw.get_window_size(environ["context"].api["window"].window)[1]

@create_function(BoolType(), {"key": IntType()})
def getKey(environ):
    return bool(environ["context"].api["window"].input.getKey(environ["args"]["key"]))

@create_function(BoolType(), {"button": IntType()})
def getMouseButton(environ):
    return bool(environ["context"].api["window"].input.getMouseButton(environ["args"]["button"]))

@create_function(VoidType(), {"visible": BoolType()})
def setCursorVisible(environ):
    environ["context"].api["window"].input.setCursorVisible(environ["args"]["visible"])

@create_function(VoidType(), {"position": {"type": "ARRAY", "array_type": FloatType()}})
def setCursorPosition(environ):
    environ["context"].api["window"].input.setCursorPosition(environ["args"]["position"][0], environ["args"]["position"][1])

@create_function(FloatType(), {})
def getCursorPositionX(environ):
    return environ["context"].api["window"].input.getCursorPosition()[0]

@create_function(FloatType(), {})
def getCursorPositionY(environ):
    return environ["context"].api["window"].input.getCursorPosition()[1]

@create_function(VoidType(), {"id": IntType(), "value": {"type": "ARRAY", "array_type": FloatType()}})
def translate(environ):
    environ["context"].api["objects"][environ["args"]["id"]].transform.translate(
        glm.vec3(environ["args"]["value"][0], environ["args"]["value"][1], environ["args"]["value"][2]))

@create_function(VoidType(), {"id": IntType(), "value": {"type": "ARRAY", "array_type": FloatType()}})
def rotate(environ):
    environ["context"].api["objects"][environ["args"]["id"]].transform.rotate(
        glm.vec3(environ["args"]["value"][0], environ["args"]["value"][1], environ["args"]["value"][2]))

@create_function(VoidType(), {"id": IntType(), "value": {"type": "ARRAY", "array_type": FloatType()}})
def scale(environ):
    environ["context"].api["objects"][environ["args"]["id"]].transform.scale(
        glm.vec3(environ["args"]["value"][0], environ["args"]["value"][1], environ["args"]["value"][2]))
    
@create_function(VoidType(), {"id": IntType(), "position": {"type": "ARRAY", "array_type": FloatType()}})
def setPosition(environ):
    environ["context"].api["objects"][environ["args"]["id"]].transform.position = \
        glm.vec3(environ["args"]["position"][0], environ["args"]["position"][1], environ["args"]["position"][2])
    
@create_function(VoidType(), {"id": IntType(), "rotation": {"type": "ARRAY", "array_type": FloatType()}})
def setRotation(environ):
    environ["context"].api["objects"][environ["args"]["id"]].transform.rotation = \
        glm.vec3(environ["args"]["rotation"][0], environ["args"]["rotation"][1], environ["args"]["rotation"][2])

@create_function(VoidType(), {"id": IntType(), "scale": {"type": "ARRAY", "array_type": FloatType()}})
def setScale(environ):
    environ["context"].api["objects"][environ["args"]["id"]].transform.scaleVector = \
        glm.vec3(environ["args"]["scale"][0], environ["args"]["scale"][1], environ["args"]["scale"][2])

@create_function(FloatType(), {"id": IntType()})
def getPositionX(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.position.x

@create_function(FloatType(), {"id": IntType()})
def getPositionY(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.position.y

@create_function(FloatType(), {"id": IntType()})
def getPositionZ(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.position.z

@create_function(FloatType(), {"id": IntType()})
def getRotationX(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.rotation.x

@create_function(FloatType(), {"id": IntType()})
def getRotationY(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.rotation.y

@create_function(FloatType(), {"id": IntType()})
def getRotationZ(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.rotation.z

@create_function(FloatType(), {"id": IntType()})
def getScaleX(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.scaleVector.x

@create_function(FloatType(), {"id": IntType()})
def getScaleY(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.scaleVector.y

@create_function(FloatType(), {"id": IntType()})
def getScaleZ(environ):
    return environ["context"].api["objects"][environ["args"]["id"]].transform.scaleVector.z

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "albedoMap": StringType()})
def setMeshAlbedoMap(environ):
    try:
        mesh = environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]]
        mesh.parts[environ["args"]["material"]]["material"].albedoMap = moss.Texture(mesh.shader, environ["args"]["albedoMap"], 0)

    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "roughnessMap": StringType()})
def setMeshRoughnessMap(environ):
    try:
        mesh = environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]]
        mesh.parts[environ["args"]["material"]]["material"].roughnessMap = moss.Texture(mesh.shader, environ["args"]["roughnessMap"], 1)

    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "metallicMap": StringType()})
def setMeshMetallicMap(environ):
    try:
        mesh = environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]]
        mesh.parts[environ["args"]["material"]]["material"].metallicMap = moss.Texture(mesh.shader, environ["args"]["metallicMap"], 2)

    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "normalMap": StringType()})
def setMeshNormalMap(environ):
    try:
        mesh = environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]]
        mesh.parts[environ["args"]["material"]]["material"].normalMap = moss.Texture(mesh.shader, environ["args"]["normalMap"], 3)

    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "specularMap": StringType()})
def setMeshSpecularMap(environ):
    try:
        mesh = environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]]
        mesh.parts[environ["args"]["material"]]["material"].specularMap = moss.Texture(mesh.shader, environ["args"]["specularMap"], 4)

    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "ambientMap": StringType()})
def setMeshAmbientMap(environ):
    try:
        mesh = environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]]
        mesh.parts[environ["args"]["material"]]["material"].ambientMap = moss.Texture(mesh.shader, environ["args"]["ambientMap"], 5)

    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "scale": IntType()})
def setMeshTextureScale(environ):
    try:
        environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]].parts[environ["args"]["material"]]["textureScale"] = environ["args"]["scale"]
    
    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "rotate": IntType()})
def setMeshRotateTexture(environ):
    try:
        environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]].parts[environ["args"]["material"]]["rotateTexture"] = environ["args"]["rotate"]

    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "cullFace": BoolType()})
def setMeshCullFace(environ):
    try:
        environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]].parts[environ["args"]["material"]]["cullFace"] = environ["args"]["cullFace"]

    except Exception as e:
        print(e)

@create_function(VoidType(), {"id": IntType(), "mesh": StringType(), "material": StringType(), "inverseNormal": BoolType()})
def setMeshInverseNormal(environ):
    try:
        environ["context"].api["objects"][environ["args"]["id"]].meshes[environ["args"]["mesh"]].parts[environ["args"]["material"]]["inverseNormal"] = environ["args"]["inverseNormal"]

    except Exception as e:
        print(e)

@create_function(BoolType(), {})
def isCameraVR(environ):
    return environ["context"].api["camera"].vr

@create_function(VoidType(), {"rotation": {"type": "ARRAY", "array_type": FloatType()}})
def setCameraRotation(environ):
    environ["context"].api["camera"].pitch = environ["args"]["rotation"][0]
    environ["context"].api["camera"].yaw = environ["args"]["rotation"][1]

@create_function(FloatType(), {})
def getCameraPitch(environ):
    return environ["context"].api["camera"].pitch

@create_function(FloatType(), {})
def getCameraYaw(environ):
    return environ["context"].api["camera"].yaw

@create_function(VoidType(), {"position": {"type": "ARRAY", "array_type": FloatType()}})
def setCameraPosition(environ):
    environ["context"].api["camera"].position = \
        glm.vec3(environ["args"]["position"][0], environ["args"]["position"][1], environ["args"]["position"][2])

@create_function(FloatType(), {})
def getCameraPositionX(environ):
    return environ["context"].api["camera"].position.x

@create_function(FloatType(), {})
def getCameraPositionY(environ):
    return environ["context"].api["camera"].position.y

@create_function(FloatType(), {})
def getCameraPositionZ(environ):
    return environ["context"].api["camera"].position.z

@create_function(FloatType(), {})
def getHmdDirectionX(environ):
    return rvr.RVRGetHmdDirection().x

@create_function(FloatType(), {})
def getHmdDirectionY(environ):
    return rvr.RVRGetHmdDirection().y

@create_function(FloatType(), {})
def getHmdDirectionZ(environ):
    return rvr.RVRGetHmdDirection().z

@create_function(FloatType(), {"controller": IntType()})
def getControllerJoystickPositionX(environ):
    try:
        return rvr.RVRGetControllerJoystickPosition(environ["args"]["controller"]).x
    
    except Exception as e:
        print(e)
        return 0.0

@create_function(FloatType(), {"controller": IntType()})
def getControllerJoystickPositionY(environ):
    try:
        return rvr.RVRGetControllerJoystickPosition(environ["args"]["controller"]).y
    
    except Exception as e:
        print(e)
        return 0.0

moss_api = pack_library()