import os, sys, moss, glm, time, rvr, ctypes, math
import pyglet.gl as gl

window = moss.Window("VR Test", 1200, 600, moss.Color(0, 0, 0), False, 1)
mixer = moss.Mixer()

near, far = 0.1, 100.0

position = glm.vec3(0.0, 0.0, 0.0)

shader = moss.Shader(
    moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.vert")),
    moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/default.frag"))
)

lightShader = moss.Shader(
    moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.vert")),
    moss.readFile(os.path.join(os.path.split(moss.__file__)[0], "shaders/light.frag"))
)

light = moss.Model(
    shader = lightShader,
    filePath = os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")
)

light.transform.position = glm.vec3(5.0, 5.0, 5.0)
light.transform.scaleVector = glm.vec3(0.1, 0.1, 0.1)

model = moss.Model(
    shader = shader,
    filePath = os.path.join(os.path.split(moss.__file__)[0], "res/deagle.obj")
)

model.transform.scale(glm.vec3(0.3, 0.3, 0.3))
deagle_sound = mixer.load(os.path.join(os.path.split(moss.__file__)[0], "res/deagle.mp3"))

mesh = "Barrel_Lowpoly_Mesh"
model.meshes[mesh].transform = moss.Transform()
barrel_pos = glm.vec3(0.0, 0.0, 0.0)
gun_std_pos, gun_pos = glm.vec3(0.0, -0.1, 0.15), glm.vec3(0.0, 0.0, 0.0)
gun_std_rot, gun_rot = glm.vec3(-75.0, 180.0, -7.5), glm.vec3(0.0, 0.0, 0.0)
state = True

rvr.RVRInit()
rvr.RVRSetupStereoRenderTargets()
rvr.RVRInitControllers()
rvr.RVRInitEyes(near, far)

@window.event
def update(window):
    global barrel_pos, gun_pos, gun_rot, state, gun_std_pos, gun_std_rot, position

    rvr.RVRPollEvents()

    for i in [model, model.meshes[mesh]]:
        i.transform.pivotx = model.transform.position
        i.transform.pivoty = model.transform.position
        i.transform.pivotz = model.transform.position

    model.meshes[mesh].transform.position = model.transform.position + barrel_pos
    model.meshes[mesh].transform.rotation = model.transform.rotation
    model.meshes[mesh].transform.scaleVector = model.transform.scaleVector

    model.transform.matrix = moss.mkmat(rvr.RVRGetControllerPoseMatrixArray(rvr.RVRControllerRight))
    model.meshes[mesh].transform.matrix = model.transform.matrix

    barrel_pos = glm.lerp(barrel_pos, glm.vec3(0.0, 0.0, 0.0), 0.15)
    gun_pos = glm.lerp(gun_pos, glm.vec3(0.0, 0.0, 0.0), 0.1)
    gun_rot = glm.lerp(gun_rot, glm.vec3(0.0, 0.0, 0.0), 0.1)

    # model.transform.position = glm.vec3(*[rvr.RVRGetControllerPosition(rvr.RVRControllerRight).get()[i] for i in range(3)])
    # model.transform.rotate(glm.vec3(0.0, 0.1, 0.0))

    # speed = 0.1
    # d = glm.vec3(*[rvr.RVRGetHmdDirection().get()[i] for i in range(3)])
    # yaw = -math.atan2(d.x, d.z) - glm.radians(90)
    # front = glm.vec3(glm.cos(yaw), 0, glm.sin(yaw))
    # joystick = glm.vec2(*[rvr.RVRGetControllerJoystickPosition(rvr.RVRControllerRight).get()[i] for i in range(2)])

    # if joystick.y != 0.0:
    #     position += joystick.y * speed * front

    # if joystick.x != 0.0:
    #     position += joystick.x * speed * glm.normalize(glm.cross(front, glm.vec3(0.0, 1.0, 0.0)))

    for controller in [rvr.RVRControllerLeft, rvr.RVRControllerRight]:
        if rvr.RVRGetControllerTriggerClickState(controller):
            if controller == rvr.RVRControllerRight:
                if state:
                    state = False
                    mixer.play(deagle_sound)
                    rvr.RVRTriggerHapticVibration(controller, 0.1, 1.0, 3.0)
                    gun_rot = glm.vec3(45.0, 0.0, 0.0)
                    gun_pos = glm.vec3(0.0, 0.1, 0.0)
                    barrel_pos = glm.vec3(0.0, 0.0, -0.15)

        else:
            if controller == rvr.RVRControllerRight:
                state = True

    for eye in [rvr.RVREyeLeft, rvr.RVREyeRight]:
        rvr.RVRBeginRendering(eye)
        window.clear()

        mat = moss.mkmat(rvr.RVRGetHmdPoseMatrix().value)
        pos = glm.vec3(-position.x, -position.y, -position.z)
        mat = glm.translate(mat, pos)

        shader.use()
        shader.setUniform1i("enableShadows", 0)
        shader.setUniform1i("lightCount", 1)
        shader.setUniform3fv("lightPositions", glm.value_ptr(light.transform.position))
        shader.setUniform3fv("lightColors", glm.value_ptr(glm.vec3(1.0, 1.0, 1.0)))
        shader.setUniform1fv("lightBrightnesses", ctypes.c_float(1.0))
        shader.setUniform3fv("cameraPosition", glm.value_ptr(position + glm.vec3(*[rvr.RVRGetHmdPosition().get()[i] for i in range(3)])))
        shader.setUniformMatrix4fv("proj", rvr.RVRGetCurrentViewProjectionNoPoseMatrix(eye).value)
        shader.setUniformMatrix4fv("view", moss.valptr(mat))
        shader.unuse()

        lightShader.use()
        lightShader.setUniform4fv("color", glm.value_ptr(glm.vec4(1.0, 1.0, 1.0, 1.0)))
        lightShader.setUniform3fv("cameraPosition", glm.value_ptr(glm.vec3(0.0, 0.0, 0.0)))
        lightShader.setUniformMatrix4fv("proj", rvr.RVRGetCurrentViewProjectionNoPoseMatrix(eye).value)
        lightShader.setUniformMatrix4fv("view", moss.valptr(mat))
        lightShader.unuse()

        model.render()
        light.render()

        rvr.RVRSetControllerShowState(rvr.RVRControllerRight, False)
        rvr.RVRRenderControllers()
        rvr.RVREndRendering()

    rvr.RVRSubmitFramebufferDescriptorsToCompositor()
    rvr.RVRUpdateHMDPoseMatrix()

    model.transform.position = gun_std_pos + gun_pos
    model.transform.rotation = gun_std_rot + gun_rot

@window.event
def exit(window):
    model.delete()
    shader.delete()
    lightShader.delete()
    rvr.RVRShutdown()
    rvr.RVRDeleteFramebufferDescriptors()

moss.run()