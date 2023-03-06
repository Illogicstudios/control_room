import os
from functools import partial

import sys

from pymel.core import *
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from shiboken2 import wrapInstance

from utils import *

from Prefs import *

import maya.OpenMaya as OpenMaya

from PresetManager import *

from parts.CameraPart import *
from parts.FeatureOverridesPart import *
from parts.DepthOfFieldPart import *
from parts.MotionBlurPart import *
from parts.ImageSizePart import *
from parts.SamplingPart import *
from parts.AdaptiveSamplingPart import *
from parts.PresetsPart import *

# ######################################################################################################################

_FILE_NAME_PREFS = "control_room"


# ######################################################################################################################


class ControlRoom(QDialog):

    def __init__(self, prnt=wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(ControlRoom, self).__init__(prnt)

        # Common Preferences (common preferences on all tools)
        self.__common_prefs = Prefs()
        # Preferences for this tool
        self.__prefs = Prefs(_FILE_NAME_PREFS)

        asset_path = os.path.dirname(__file__) + "/assets"

        # Model attributes
        self.__parts = {
            "camera": CameraPart(self),
            "feature_overrides": FeatureOverridesPart(self),
            "dof": DepthOfFieldPart(self),
            "motion_blur": MotionBlurPart(self),
            "image_size": ImageSizePart(self),
            "sampling": SamplingPart(self),
            "adaptive_sampling": AdaptiveSamplingPart(self),
            "presets": PresetsPart(self, asset_path),
        }

        # UI attributes
        self.__ui_width = 550
        self.__ui_height = 900
        self.__ui_min_width = 550
        self.__ui_min_height = 900
        self.__ui_pos = QDesktopWidget().availableGeometry().center() - QPoint(self.__ui_width, self.__ui_height) / 2

        self.__retrieve_prefs()

        # name the window
        self.setWindowTitle("Control Room")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        if ControlRoom.test_arnold_renderer():
            # Create the layout, linking it to actions and refresh the display
            self.__create_ui()
            self.__refresh_ui()
            self.__add_callbacks()
        else:
            self.close()

    @staticmethod
    def test_arnold_renderer():
        arnold_renderer_loaded = objExists("defaultArnoldRenderOptions")
        if not arnold_renderer_loaded:
            msg = QMessageBox()
            msg.setWindowTitle("Error Control Room with Arnold Renderer")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Arnold Renderer not loaded")
            msg.setInformativeText('Control Room can\'t run without the Arnold Renderer loaded. You '
                                   'can load the Arnold Renderer by opening the Render Settings Window')
            msg.exec_()
        return arnold_renderer_loaded

    # Save preferences
    def __save_prefs(self):
        size = self.size()
        self.__prefs["window_size"] = {"width": size.width(), "height": size.height()}
        pos = self.pos()
        self.__prefs["window_pos"] = {"x": pos.x(), "y": pos.y()}

    # Retrieve preferences
    def __retrieve_prefs(self):
        if "window_size" in self.__prefs:
            size = self.__prefs["window_size"]
            self.__ui_width = size["width"]
            self.__ui_height = size["height"]
        if "window_pos" in self.__prefs:
            pos = self.__prefs["window_pos"]
            self.__ui_pos = QPoint(pos["x"], pos["y"])

    def showEvent(self, arg__1: QShowEvent) -> None:
        pass

    # Remove callbacks
    def hideEvent(self, arg__1: QCloseEvent) -> None:
        self.__remove_callbacks()
        self.__save_prefs()

    # Create the ui
    def __create_ui(self):
        # Reinit attributes of the UI
        self.setMinimumSize(self.__ui_min_width, self.__ui_min_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(self.__ui_pos)

        # Main Layout
        main_lyt = QVBoxLayout()
        main_lyt.setContentsMargins(3, 8, 3, 0)
        main_lyt.setSpacing(5)
        main_lyt.setAlignment(Qt.AlignTop)
        self.setLayout(main_lyt)

        for part in self.__parts.values():
            main_lyt.addLayout(part.create_ui())

    # Refresh the ui according to the model attribute
    def __refresh_ui(self):
        for part in self.__parts.values():
            part.refresh_ui()

    # Refresh the ui according to the model attribute
    def __add_callbacks(self):
        for part in self.__parts.values():
            part.add_callbacks()

    def __remove_callbacks(self):
        for part in self.__parts.values():
            part.remove_callbacks()

    def generate_preset(self, preset_name):
        preset_manager = PresetManager.get_instance()
        preset = Preset(name=preset_name, active=True)
        for part_name, part in self.__parts.items():
            part.add_to_preset(part_name, preset)
        preset_manager.add_preset(preset)
        preset_manager.save_presets()

    def apply_preset(self, preset):
        for part_name,part in self.__parts.items():
            part.apply(part_name, preset)
        for part in self.__parts.values():
            part.refresh_ui()

    def cam_changed(self, cam):
        self.__parts["dof"].cam_changed(cam)
        self.__parts["image_size"].cam_changed(cam)
