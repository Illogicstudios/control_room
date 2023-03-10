import sys
import importlib

if __name__ == '__main__':
    # TODO specify the right path
    install_dir = 'PATH/TO/control_room'
    if not sys.path.__contains__(install_dir):
        sys.path.append(install_dir)

    modules = [
        "ControlRoom",
        "Preset",
        "PresetManager",
        "FormSlider",
        "parts.CameraPart",
        "parts.FeatureOverridesPart",
        "parts.DepthOfFieldPart",
        "parts.MotionBlurPart",
        "parts.ImageSizePart",
        "parts.SamplingPart",
        "parts.AdaptiveSamplingPart",
        "parts.PresetsPart",
    ]

    from utils import *
    unload_packages(silent=True, packages=modules)

    for module in modules:
        importlib.import_module(module)

    from ControlRoom import *

    try:
        control_room.close()
    except:
        pass
    control_room = ControlRoom()
    control_room.show()
