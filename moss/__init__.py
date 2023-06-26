__version__ = "0.0.3"
__author__ = "Yusuf Rençber"
__requirements__ = ["pyglm", "pyglet", "pysdl2", "pysdl2-dll", "glfw", "rsxpy", "rvr", "imgui", "stbi-py"]

import pyglet.gl as gl
import ctypes, glm, traceback

gl.glGetString.restype = ctypes.c_char_p

from moss.context import *
from moss.window import *
from moss.buffers import *
from moss.mesh import *
from moss.color import *
from moss.shader import *
from moss.input import *
from moss.camera import *
from moss.transform import *
from moss.mixer import *
from moss.loader import *
from moss.model import *
from moss.texture import *
from moss.collision import *
from moss.physics import *
from moss.material import *
from moss.logger import *
from moss.renderer import *

mkarr = lambda type, list: (type * len(list))(*list)
mkmat = lambda arr: glm.mat4(*[float(arr[i]) for i in range(16)])
valptr = lambda mat: moss.mkarr(ctypes.c_float, [glm.value_ptr(mat)[i] for i in range(16)])
readFile = lambda filePath: open(filePath, "r").read()

path = os.path.split(__file__)[0]

logger = Logger()
context = Context()

def event(func):
    context.events[func.__name__] = func

def run():
    try:
        context.run()

    except Exception as e:
        logger.log(FATAL_ERROR, f"engine crashed, traceback:\n{''.join(traceback.format_exc()[:-1])}")
        logger.save(os.path.join(os.path.split(__file__)[0], "crash_log.txt"))