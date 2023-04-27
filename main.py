import importlib
from common import utils

utils.unload_packages(silent=True, package="control_room")
importlib.import_module("control_room")
from control_room.ControlRoom import ControlRoom
try:
    control_room.close()
except:
    pass
control_room = ControlRoom()
control_room.show()
