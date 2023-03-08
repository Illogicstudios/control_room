import enum
from ControlRoomPart import *
from FormSlider import *
from pymel.core import *
from functools import partial

_AspectRatios = {
    "1:1": {"ratio": 1.0, "HD": 1920, "SD": 720},
    "16:9": {"ratio": 1.77777777778, "HD": 1920, "SD": 1280},
    "9:16": {"ratio": 0.5625, "HD": 1080, "SD": 720},
    "4:5": {"ratio": 0.8, "HD": 1536, "SD": 720},
    "Scope": {"ratio": 2.38694638695, "HD": 2048, "SD": 1024},
}


class ImageSizePart(ControlRoomPart):
    def __init__(self, control_room):
        super(ImageSizePart, self).__init__(control_room, "Image Size")
        self.__cam = None
        self.__width_callback = None
        self.__height_callback = None
        self.__aspect_ratio_callback = None
        self.__overscan_callback = None
        self.__ratio_selected = None
        self.__is_gate_opaque = False
        self.__is_gate_enabled = False

        self.__ui_width_edit = None
        self.__ui_height_edit = None
        self.__ui_ratio_btns = {}
        self.__ui_sd_format_btn = None
        self.__ui_hd_format_btn = None
        self.__ui_overscan_line_edit = None
        self.__ui_overscan_slider = None
        self.__ui_opaque_gate_cb = None
        self.__ui_enable_gate_cb = None

        self.__retrieve_aspect_ratio()

    def populate(self):
        content = QVBoxLayout()
        content.setContentsMargins(4, 4, 2, 0)

        size_lyt = QHBoxLayout()
        lbl_width = QLabel("Width")
        size_lyt.addWidget(lbl_width)
        self.__ui_width_edit = QLineEdit()
        self.__ui_width_edit.editingFinished.connect(self.__on_width_changed)
        self.__ui_width_edit.setContentsMargins(0, 0, 10, 0)
        size_lyt.addWidget(self.__ui_width_edit)
        lbl_height = QLabel("Height")
        size_lyt.addWidget(lbl_height)
        self.__ui_height_edit = QLineEdit()
        self.__ui_height_edit.editingFinished.connect(self.__on_height_changed)
        size_lyt.addWidget(self.__ui_height_edit)

        ratios_lyt = QHBoxLayout()
        ratios_lyt.setContentsMargins(0, 4, 0, 0)
        for name in _AspectRatios.keys():
            self.__ui_ratio_btns[name] = QPushButton(name)
            self.__ui_ratio_btns[name].clicked.connect(partial(self.__on_click_ratio_btn, name))
            ratios_lyt.addWidget(self.__ui_ratio_btns[name])

        format_lyt = QHBoxLayout()
        format_lyt.setContentsMargins(0, 4, 0, 0)
        self.__ui_sd_format_btn = QPushButton("SD")
        self.__ui_sd_format_btn.clicked.connect(partial(self.__on_click_format_btn, "SD"))
        self.__ui_hd_format_btn = QPushButton("HD")
        self.__ui_hd_format_btn.clicked.connect(partial(self.__on_click_format_btn, "HD"))
        format_lyt.addWidget(self.__ui_sd_format_btn)
        format_lyt.addWidget(self.__ui_hd_format_btn)

        form_lyt = QFormLayout()
        lbl = QLabel("Overscan")
        lyt = QHBoxLayout()
        self.__ui_overscan_line_edit = QLineEdit()
        min = 0
        max = 10
        validator = QDoubleValidator(bottom=min, top=max, decimals=3)
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        validator.setLocale(locale)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.__ui_overscan_line_edit.setValidator(validator)
        self.__ui_overscan_line_edit.editingFinished.connect(self.__on_overscan_changed)
        self.__ui_overscan_slider = QSlider(Qt.Horizontal)
        self.__ui_overscan_slider.setMaximum(max * 1000)
        self.__ui_overscan_slider.setMinimum(min * 1000)
        self.__ui_overscan_slider.valueChanged.connect(self.__on_slider_overscan_changed)
        lyt.addWidget(self.__ui_overscan_line_edit, 1)
        lyt.addWidget(self.__ui_overscan_slider, 3)
        form_lyt.addRow(lbl, lyt)

        camera_gate_lyt = QHBoxLayout()
        self.__ui_enable_gate_cb = QCheckBox("Enable Gate")
        self.__ui_enable_gate_cb.stateChanged.connect(self.__on_gate_enable_changed)
        self.__ui_opaque_gate_cb = QCheckBox("Opaque Gate")
        self.__ui_opaque_gate_cb.stateChanged.connect(self.__on_gate_opacity_changed)
        camera_gate_lyt.addWidget(self.__ui_enable_gate_cb, 1)
        camera_gate_lyt.addWidget(self.__ui_opaque_gate_cb, 1)

        content.addLayout(size_lyt)
        content.addLayout(ratios_lyt)
        content.addLayout(format_lyt)
        content.addLayout(form_lyt)
        content.addLayout(camera_gate_lyt)
        return content

    def __on_overscan_changed(self):
        if self.__cam is not None:
            self.__cam.overscan.set(float(self.__ui_overscan_line_edit.text()))

    def __on_slider_overscan_changed(self, value):
        if self.__cam is not None:
            value = value / 1000
            if value > 0:
                self.__ui_overscan_line_edit.setText(str(value))
                self.__cam.overscan.set(value)

    def __on_click_ratio_btn(self, ratio):
        if self.__ratio_selected == ratio:
            self.__ratio_selected = None
        else:
            self.__ratio_selected = ratio
            setAttr("defaultResolution.deviceAspectRatio", _AspectRatios[self.__ratio_selected]["ratio"])
            self.__set_height()
            self.__retrieve_aspect_ratio()
        self.refresh_ui()

    def __on_click_format_btn(self, format):
        width = _AspectRatios[self.__ratio_selected][format]
        setAttr("defaultResolution.width", width)
        self.__set_height()
        self.__retrieve_aspect_ratio()
        self.refresh_ui()

    def __set_height(self):
        if self.__ratio_selected is not None:
            setAttr("defaultResolution.height",
                    getAttr("defaultResolution.width") / _AspectRatios[self.__ratio_selected]["ratio"])

    def __set_width(self):
        if self.__ratio_selected is not None:
            setAttr("defaultResolution.width",
                    getAttr("defaultResolution.height") * _AspectRatios[self.__ratio_selected]["ratio"])

    def __retrieve_aspect_ratio(self):
        self.__ratio_selected = None
        aspect_ratio = getAttr("defaultResolution.deviceAspectRatio")
        for name, aspect_ratio_datas in _AspectRatios.items():
            if abs(aspect_ratio - aspect_ratio_datas["ratio"]) < 0.001:
                self.__ratio_selected = name
                break

    def set_gate_attr(self):
        if self.__cam is not None:
            self.__cam.displayGateMaskOpacity.set(1.0 if self.__is_gate_opaque else 0.7)
            self.__cam.displayGateMaskColor.set((0, 0, 0) if self.__is_gate_opaque else (0.5, 0.5, 0.5))
            self.__cam.displayResolution.set(self.__is_gate_enabled)

    def set_gate_enable(self):
        if self.__cam is not None:
            self.__cam.displayResolution.set(self.__is_gate_enabled)

    def refresh_ui(self):
        width_retrieved = getAttr("defaultResolution.width")
        self.__ui_width_edit.setText(str(width_retrieved))
        self.__ui_height_edit.setText(str(getAttr("defaultResolution.height")))
        stylesheet_selected = "background-color:#2C2C2C"

        for name, btn in self.__ui_ratio_btns.items():
            is_ratio_selected = name == self.__ratio_selected
            btn.setStyleSheet(stylesheet_selected if is_ratio_selected else "")

        is_ratio_found = self.__ratio_selected is not None
        self.__ui_sd_format_btn.setEnabled(is_ratio_found)
        self.__ui_hd_format_btn.setEnabled(is_ratio_found)
        sd_selected = is_ratio_found and width_retrieved == _AspectRatios[self.__ratio_selected]["SD"]
        hd_selected = is_ratio_found and width_retrieved == _AspectRatios[self.__ratio_selected]["HD"]
        self.__ui_sd_format_btn.setStyleSheet(stylesheet_selected if sd_selected else "")
        self.__ui_hd_format_btn.setStyleSheet(stylesheet_selected if hd_selected else "")
        if self.__cam is not None:
            overscan = self.__cam.overscan.get()
            self.__ui_overscan_slider.setValue(overscan * 1000)
            self.__ui_overscan_line_edit.setText(str(overscan))
        self.__ui_enable_gate_cb.setChecked(self.__is_gate_enabled)
        self.__ui_opaque_gate_cb.setChecked(self.__is_gate_opaque)

    def __on_gate_opacity_changed(self, state):
        self.__is_gate_opaque = state == 2
        self.set_gate_attr()

    def __on_gate_enable_changed(self, state):
        self.__is_gate_enabled = state == 2
        self.set_gate_enable()

    def __on_width_changed(self):
        setAttr("defaultResolution.width", int(self.__ui_width_edit.text()))
        self.__set_height()

    def __on_height_changed(self):
        setAttr("defaultResolution.height", int(self.__ui_height_edit.text()))
        self.__set_width()

    def __callback(self):
        self.__retrieve_aspect_ratio()
        self.refresh_ui()

    def add_callbacks(self):
        self.__width_callback = scriptJob(attributeChange=["defaultResolution.width", self.__callback])
        self.__height_callback = scriptJob(attributeChange=["defaultResolution.height", self.__callback])
        self.__aspect_ratio_callback = scriptJob(
            attributeChange=["defaultResolution.deviceAspectRatio", self.__callback])

    def add_dynamic_callbacks(self):
        if self.__cam is not None:
            self.__overscan_callback = scriptJob(
                attributeChange=[self.__cam + '.overscan', self.refresh_ui])

    def remove_callbacks(self):
        scriptJob(kill=self.__width_callback)
        scriptJob(kill=self.__height_callback)
        scriptJob(kill=self.__aspect_ratio_callback)
        self.remove_dynamic_callbacks()

    def remove_dynamic_callbacks(self):
        if self.__overscan_callback is not None:
            scriptJob(kill=self.__overscan_callback)
            self.__overscan_callback = None

    def __retrieve_gate_attr(self):
        if self.__cam is not None:
            self.__is_gate_enabled = self.__cam.displayResolution.get()
            self.__is_gate_opaque = self.__cam.displayGateMaskOpacity.get() == 1.0

    def add_to_preset(self, part_name, preset):
        preset.set(part_name, "width", getAttr("defaultResolution.width"))
        preset.set(part_name, "height", getAttr("defaultResolution.height"))
        if self.__cam is not None:
            preset.set(part_name, "overscan", self.__cam.overscan.get())
            preset.set(part_name, "opacity_gate", self.__is_gate_opaque)
            preset.set(part_name, "gate_enabled", self.__is_gate_enabled)

    def apply(self, part_name, preset):
        width = preset.get(part_name, "width")
        height = preset.get(part_name, "height")
        setAttr("defaultResolution.width", width)
        setAttr("defaultResolution.height", height)
        setAttr("defaultResolution.deviceAspectRatio", width / height)
        self.__retrieve_aspect_ratio()
        if self.__cam is not None:
            self.__cam.overscan.set(preset.get(part_name, "overscan"))
            self.__is_gate_opaque = preset.get(part_name, "opacity_gate") == 1
            self.__is_gate_enabled = preset.get(part_name, "gate_enabled")
            self.set_gate_attr()

    def cam_changed(self, cam):
        self.__cam = cam
        self.__retrieve_gate_attr()
        self.remove_dynamic_callbacks()
        self.add_dynamic_callbacks()
        self.refresh_ui()
