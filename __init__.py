import os
import sys
import pkg_resources
import subprocess
from . import auto_load

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


required_packages = ['pyperclip', 'blenderproc', 'tqdm', 'pywin32']

for required_package in required_packages:
    try:
        pkg_resources.require(required_package)
    except pkg_resources.DistributionNotFound:
        subprocess.check_call([os.path.join(
            sys.prefix, 'bin', 'python.exe'), '-m', 'pip', 'install', required_package])


auto_load.init()


def register():
    auto_load.register()


def unregister():
    auto_load.unregister()


if __name__ == "__main__":
    register()
