from abc import *

import maya.OpenMaya as OpenMaya

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from utils import *


class ControlRoomPart(ABC):
    def __init__(self, control_room, name):
        self._control_room = control_room
        self._name = name

    def create_ui(self):
        lyt = QVBoxLayout()
        lyt.setSpacing(2)
        lyt.setAlignment(Qt.AlignTop)

        title_label = QLabel(self._name)
        title_label.setContentsMargins(5,5,5,5)
        title_label.setStyleSheet("background-color:#5D5D5D;font-weight:bold")
        lyt.addWidget(title_label,0, Qt.AlignTop)

        lyt.addLayout(self.populate())
        return lyt


    @abstractmethod
    def populate(self):
        pass

    @abstractmethod
    def refresh_ui(self):
        pass

    @abstractmethod
    def add_callbacks(self):
        pass

    @abstractmethod
    def remove_callbacks(self):
        pass

    @abstractmethod
    def add_to_preset(self, part_name, preset):
        pass

    @abstractmethod
    def apply(self, part_name, preset):
        pass

    def get_name(self):
        return self._name
