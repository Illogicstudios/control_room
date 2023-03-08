import enum
import os.path
import re
from functools import partial

import maya.OpenMaya as OpenMaya
from pymel.core import *

from ControlRoomPart import *
from FormSlider import *
from PresetManager import *

_PresetBaseName = "Preset"


class PresetsPart(ControlRoomPart):

    @staticmethod
    def get_new_preset_name():
        base_name = _PresetBaseName
        num = 1
        name = base_name + str(num)
        preset_manager = PresetManager.get_instance()
        while preset_manager.has_preset_with_name(name):
            num += 1
            name = base_name + str(num)
        return name

    def __init__(self, control_room, asset_path):
        super(PresetsPart, self).__init__(control_room, "Presets")
        self.__ui_presets_lyt = None
        self.__asset_path = asset_path
        self.__spacer = None
        self.__maya_callback = None

    def populate(self):
        self.__ui_presets_lyt = QHBoxLayout()
        self.__ui_presets_lyt.setContentsMargins(2, 4, 2, 4)
        self.__ui_presets_lyt.setSpacing(4)
        return self.__ui_presets_lyt

    def refresh_ui(self):
        if self.__spacer is not None:
            self.__ui_presets_lyt.removeItem(self.__spacer)
        clear_layout(self.__ui_presets_lyt)
        preset_manager = PresetManager.get_instance()
        presets = preset_manager.get_presets()

        index = 0

        icon_size = QtCore.QSize(16, 16)
        icon_container_size = QtCore.QSize(24, 24)

        for preset in presets:
            widget_preset = QWidget()
            widget_preset.setStyleSheet(".QWidget{background:#383838; border-radius:4px}")
            lyt_preset = QVBoxLayout(widget_preset)
            lyt_preset.setSpacing(10)
            lbl_name_preset = QLabel(preset.get_name())
            lbl_name_preset.setStyleSheet("font-weight:bold")
            lyt_preset.addWidget(lbl_name_preset, alignment=Qt.AlignCenter)
            lyt_actions = QHBoxLayout()
            lyt_actions.setSpacing(5)
            lyt_actions.setAlignment(Qt.AlignCenter)
            lyt_preset.addLayout(lyt_actions)

            apply_btn = QPushButton()
            apply_btn.setIconSize(QtCore.QSize(18, 18))
            apply_btn.setFixedSize(icon_container_size)
            apply_btn.setIcon(QIcon(QPixmap(os.path.join(self.__asset_path, "apply.png"))))
            apply_btn.clicked.connect(partial(self.__apply_preset, preset))
            lyt_actions.addWidget(apply_btn)

            rename_btn = QPushButton()
            rename_btn.setIconSize(icon_size)
            rename_btn.setFixedSize(icon_container_size)
            rename_btn.setIcon(QIcon(QPixmap(os.path.join(self.__asset_path, "rename.png"))))
            rename_btn.clicked.connect(partial(self.__rename_preset, preset))
            lyt_actions.addWidget(rename_btn)

            save_btn = QPushButton()
            save_btn.setIconSize(icon_size)
            save_btn.setFixedSize(icon_container_size)
            save_btn.setIcon(QIcon(QPixmap(os.path.join(self.__asset_path, "save.png"))))
            save_btn.clicked.connect(partial(self.__save_to_preset, preset))
            lyt_actions.addWidget(save_btn)

            delete_btn = QPushButton()
            delete_btn.setIconSize(icon_size)
            delete_btn.setFixedSize(icon_container_size)
            delete_btn.setIcon(QIcon(QPixmap(os.path.join(self.__asset_path, "delete.png"))))
            delete_btn.clicked.connect(partial(self.__delete_preset, preset))
            lyt_actions.addWidget(delete_btn)
            self.__ui_presets_lyt.insertWidget(index, widget_preset, 1)
            index += 1

        if index < 4:
            add_preset_btn = QPushButton("New Preset")
            if index == 0:
                add_preset_btn.setStyleSheet("padding: 3px;margin-top:18px")
            add_preset_btn.setIconSize(QtCore.QSize(18, 18))
            add_preset_btn.setIcon(QIcon(QPixmap(os.path.join(self.__asset_path, "add.png"))))
            add_preset_btn.clicked.connect(partial(self.__generate_new_preset))
            self.__ui_presets_lyt.insertWidget(index, add_preset_btn, 1, Qt.AlignCenter)
            index += 1

        if index < 4:
            self.__spacer = QSpacerItem(0, 0)
            self.__ui_presets_lyt.insertItem(index, self.__spacer)
            self.__ui_presets_lyt.setStretch(index, 4 - index)
        else:
            self.__spacer = None

    def __generate_new_preset(self):
        self._control_room.generate_preset(PresetsPart.get_new_preset_name())
        self.refresh_ui()

    def __delete_preset(self, preset):
        answer_delete = confirmDialog(
            title='Confirm',
            message="Are you sure to delete the preset " + preset.get_name() + " ?",
            button=['Yes', 'No'],
            defaultButton='Yes',
            dismissString='No')
        if answer_delete == "Yes":
            preset_manager = PresetManager.get_instance()
            preset_manager.remove_preset(preset)
            preset_manager.save_presets()
            self.refresh_ui()

    def __rename_preset(self, preset):
        result = promptDialog(
            title='Rename Preset',
            message='Enter new name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')
        if result == 'OK':
            new_name = promptDialog(query=True, text=True)
            if re.match(r"^\w+$", new_name):
                preset_manager = PresetManager.get_instance()
                preset.set_name(promptDialog(query=True, text=True))
                preset_manager.save_presets()
                self.refresh_ui()

    def __save_to_preset(self, preset):
        self._control_room.generate_preset(preset.get_name())
        self.refresh_ui()

    def __apply_preset(self, preset):
        self._control_room.apply_preset(preset)
        self.refresh_ui()

    def __callback(self, *args, **kwargs):
        PresetManager.get_instance().retrieve_presets()
        self.refresh_ui()

    def add_callbacks(self):
        self.__maya_callback = scriptJob(event=["SceneOpened", self.__callback])

    def remove_callbacks(self):
        scriptJob(kill=self.__maya_callback)

    def add_to_preset(self, part_name, preset):
        # Nothing
        pass

    def apply(self, part_name, preset):
        # Nothing
        pass