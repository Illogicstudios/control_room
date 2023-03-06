from ControlRoomPart import *
from FormSlider import *
from pymel.core import *


class MotionBlurPart(ControlRoomPart):
    def __init__(self, control_room):
        super(MotionBlurPart, self).__init__(control_room, "Motion Blur")
        self.__form_sliders = [
            FormSlider(FormSliderType.IntSlider, "Keys", "defaultArnoldRenderOptions.motion_steps", "motion_blur_keys",
                       2, 30, 300),
            FormSlider(FormSliderType.FloatSlider, "Motion Step", "defaultArnoldRenderOptions.motion_frames",
                       "motion_blur_step", 0, 1),
        ]
        self.__ui_enable_cb = None
        self.__ui_instant_shutter_cb = None
        self.__enable_callback = None
        self.__instant_shutter_callback = None

    def populate(self):
        content = QVBoxLayout()
        content.setContentsMargins(4, 4, 1, 4)

        lyt_cb = QHBoxLayout()
        self.__ui_enable_cb = QCheckBox("Enable Motion Blur")
        self.__ui_enable_cb.stateChanged.connect(self.__on_enable_changed)
        lyt_cb.addWidget(self.__ui_enable_cb)
        self.__ui_instant_shutter_cb = QCheckBox("Instantaneous Shutter")
        self.__ui_instant_shutter_cb.stateChanged.connect(self.__on_instant_shutter_changed)
        lyt_cb.addWidget(self.__ui_instant_shutter_cb)
        content.addLayout(lyt_cb)

        form_layout = QFormLayout()
        content.addLayout(form_layout)

        for fs in self.__form_sliders:
            lbl, slider = fs.generate_ui()
            form_layout.addRow(lbl, slider)
        return content

    def refresh_ui(self):
        self.__ui_enable_cb.setChecked(getAttr("defaultArnoldRenderOptions.motion_blur_enable"))
        self.__ui_instant_shutter_cb.setChecked(getAttr("defaultArnoldRenderOptions.ignoreMotionBlur"))
        for fs in self.__form_sliders:
            fs.refresh_ui()

    def __on_enable_changed(self, state):
        setAttr("defaultArnoldRenderOptions.motion_blur_enable", state == 2)

    def __on_instant_shutter_changed(self, state):
        setAttr("defaultArnoldRenderOptions.ignoreMotionBlur", state == 2)

    def add_callbacks(self):
        self.__enable_callback = scriptJob(attributeChange=["defaultArnoldRenderOptions.motion_blur_enable",
                                                            self.refresh_ui])
        self.__instant_shutter_callback = scriptJob(attributeChange=["defaultArnoldRenderOptions.ignoreMotionBlur",
                                                                     self.refresh_ui])
        for fs in self.__form_sliders:
            fs.add_callback()

    def remove_callbacks(self):
        scriptJob(kill=self.__enable_callback)
        scriptJob(kill=self.__instant_shutter_callback)
        for fs in self.__form_sliders:
            fs.remove_callback()

    def add_to_preset(self, part_name, preset):
        for fs in self.__form_sliders:
            key, field = fs.get_key_preset_and_field()
            preset.set(part_name, key, getAttr(field))
        preset.set(part_name, "enable", getAttr("defaultArnoldRenderOptions.motion_blur_enable"))
        preset.set(part_name, "instant_shutter", getAttr("defaultArnoldRenderOptions.ignoreMotionBlur"))

    def apply(self, part_name, preset):
        for fs in self.__form_sliders:
            key, field = fs.get_key_preset_and_field()
            setAttr(field, preset.get(part_name, key))
        setAttr("defaultArnoldRenderOptions.motion_blur_enable", preset.get(part_name, "enable"))
        setAttr("defaultArnoldRenderOptions.ignoreMotionBlur", preset.get(part_name, "instant_shutter"))
