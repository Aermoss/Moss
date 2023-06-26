import sys, os, math

sys.path.append("../../")

import moss, glm, time, ctypes

import pyglet.gl as gl

def setup(window):
    global renderer, camera, cube, ground

    renderer = moss.Renderer(window)
    camera = moss.FPSCamera(renderer.shader, position = glm.vec3(-5.0, 12.0, 5.0))

    renderer.lights = [
        moss.Light(renderer, glm.vec3(-1.5, 10.0, 1.5), 1.0, glm.vec3(1.0, 1.0, 1.0))
    ]

    ground = moss.Model(
        shader = renderer.shader,
        filePath = os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")
    )

    ground.transform.position = glm.vec3(0.0, 0.0, 0.0)
    ground.transform.scaleVector = glm.vec3(5, 5, 5)

    cube = moss.Model(
        shader = renderer.shader,
        filePath = os.path.join(os.path.split(moss.__file__)[0], "res/cube.obj")
    )

    cube.transform.position = glm.vec3(0.0, 8.0, 0.0)
    cube.transform.scaleVector = glm.vec3(1, 1, 1)

def update(window):
    window.clear()
    camera.proccessInputs()
    renderer.submit(cube)
    renderer.submit(ground)
    renderer.render(camera)

def exit(window):
    cube.delete()
    ground.delete()
    renderer.delete()

def main(argv):
    global window
    window = moss.Window("Shadow Test", 1200, 600, moss.Color(0, 0, 0), True)
    window.event(setup)
    window.event(update)
    window.event(exit)
    moss.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))