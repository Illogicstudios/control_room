import enum
import maya.OpenMaya as OpenMaya

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from utils import *

class FormSliderType(Enum):
    IntSlider = 0
    FloatSlider = 1


class FormSlider:
    def __init__(self, type, name, field_name, key_preset, min, max, mmax = None):
        self.__type = type
        self.__name = name
        self.__field_name = field_name
        self.__key_preset = key_preset
        self.__min = min
        self.__max = max
        self.__mmax = mmax if mmax is not None else max
        self.__mult = 1000 if self.__type == FormSliderType.FloatSlider else 1
        self.__ui_value_line_edit = None
        self.__ui_slider = None
        self.__callback = None

    def __on_slider_value_changed(self, value):
        if self.__type is FormSliderType.IntSlider:
            value = int(value)
        else:
            value = value / self.__mult
        self.__ui_value_line_edit.setText(str(value))
        setAttr(self.__field_name, value)

    def __on_edit_value_changed(self):
        str_value = self.__ui_value_line_edit.text()
        value = float(str_value)
        self.__ui_slider.setValue(value)
        setAttr(self.__field_name, value)

    def generate_ui(self):
        lbl = QLabel(self.__name)
        lyt = QHBoxLayout()
        self.__ui_value_line_edit = QLineEdit()

        if self.__type is FormSliderType.IntSlider:
            validator = QIntValidator(bottom=self.__min,top=self.__mmax)
        else:
            validator = QDoubleValidator(bottom=self.__min,top=self.__mmax, decimals=3)
            locale = QLocale(QLocale.English, QLocale.UnitedStates)
            validator.setLocale(locale)
            validator.setNotation(QDoubleValidator.StandardNotation)
        self.__ui_value_line_edit.setValidator(validator)
        self.__ui_value_line_edit.editingFinished.connect(self.__on_edit_value_changed)
        self.__ui_slider = QSlider(Qt.Horizontal)
        self.__ui_slider.setMaximum(self.__max * self.__mult)
        self.__ui_slider.setMinimum(self.__min * self.__mult)
        self.__ui_slider.valueChanged.connect(self.__on_slider_value_changed)
        lyt.addWidget(self.__ui_value_line_edit, 1)
        lyt.addWidget(self.__ui_slider, 3)
        return lbl, lyt

    def refresh_ui(self):
        val = getAttr(self.__field_name)
        if getAttr(self.__field_name) >= self.__max:
            self.__ui_slider.setMaximum(val* self.__mult)
        self.__ui_slider.setValue(val * self.__mult)
        self.__ui_value_line_edit.setText(str(round(getAttr(self.__field_name), 3)))

    def __callback_action(self):
        self.refresh_ui()

    def add_callback(self):
        self.__callback = scriptJob(attributeChange=[self.__field_name, self.__callback_action])

    def remove_callback(self):
        scriptJob(kill=self.__callback)

    def get_key_preset_and_field(self):
        return self.__key_preset, self.__field_name
