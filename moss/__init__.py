__version__ = "0.0.2"
__author__ = "Yusuf Rençber"
__requirements__ = ["pyglm", "pyglet", "pysdl2", "pysdl2-dll", "pillow", "glfw", "rsxpy", "rvr", "imgui"]

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

mkarr = lambda type, list: (type * len(list))(*list)
mkmat = lambda arr: glm.mat4(*[float(arr[i]) for i in range(16)])
valptr = lambda mat: moss.mkarr(ctypes.c_float, [glm.value_ptr(mat)[i] for i in range(16)])
readFile = lambda filePath: open(filePath, "r").read()

path = os.path.split(__file__)[0]

context = Context()

def event(func):
    context.events[func.__name__] = func

def run():
    context.run()