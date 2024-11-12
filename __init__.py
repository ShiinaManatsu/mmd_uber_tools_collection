from . import auto_load
from . import install_blender_python_module

bl_info = {
    "name": "MMD Uber Tools Collection",
    "author": "ShiinaManatsu",
    "description": "MMD pipline tools collection",
    "blender": (3, 3, 0),
    "version": (0, 0, 3),
    "location": "",
    "warning": "",
    "category": "Generic"
}

install_blender_python_module.installModule("pyperclip")

auto_load.init()


def register():
    auto_load.register()


def unregister():
    auto_load.unregister()


if __name__ == "__main__":
    register()
