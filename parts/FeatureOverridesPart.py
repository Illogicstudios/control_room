from ControlRoomPart import *
from pymel.core import *


class IgnoreFields:
    def __init__(self, name, field_name, key_preset):
        self.__name = name
        self.__field_name = field_name
        self.__key_preset = key_preset
        self.__checkbox = None
        self.__callback = None

    def __on_state_changed(self, state):
        setAttr("defaultArnoldRenderOptions." + self.__field_name, state == 2)

    def get_key_preset_and_field(self):
        return self.__key_preset, self.__field_name

    def generate_checkbox(self):
        self.__checkbox = QCheckBox(self.__name)
        self.__checkbox.stateChanged.connect(self.__on_state_changed)
        return self.__checkbox

    def refresh_checkbox(self):
        self.__checkbox.setChecked(getAttr("defaultArnoldRenderOptions." + self.__field_name))

    def __callback_action(self):
        self.refresh_checkbox()

    def add_callback(self):
        self.__callback = scriptJob(
            attributeChange=['defaultArnoldRenderOptions.' + self.__field_name, self.__callback_action])

    def get_preset_value_tuple(self):
        return self.__key_preset, getAttr("defaultArnoldRenderOptions." + self.__field_name)

    def remove_callback(self):
        scriptJob(kill=self.__callback)


class FeatureOverridesPart(ControlRoomPart):
    def __init__(self, control_room):
        super(FeatureOverridesPart, self).__init__(control_room, "Feature Overrides")
        self.__ignore_fields = [
            IgnoreFields("Ignore Subdivision", "ignoreSubdivision", "ignore_subdivision"),
            IgnoreFields("Ignore Athmosphere", "ignoreAtmosphere", "ignore_atmosphere"),
            IgnoreFields("Ignore Displacement", "ignoreDisplacement", "ignore_displacement"),
            IgnoreFields("Ignore Motion", "ignoreMotion", "ignore_motion"),
            IgnoreFields("Ignore Depth of field", "ignoreDof", "ignore_dof")
        ]
        self.__ignore_aovs = False

        self.__ui_ignore_aovs_cb = None
        self.__ui_output_denoising_aovs_cb = None

        self.__arnold_render_callback = None

    def populate(self):
        content = QHBoxLayout()
        content.setContentsMargins(5, 5, 5, 5)
        content.setSizeConstraint(QLayout.SetNoConstraint)
        left_content = QVBoxLayout()
        content.addLayout(left_content, 1)
        right_content = QVBoxLayout()
        content.addLayout(right_content, 1)

        # Ignore fields
        for ign_field in self.__ignore_fields:
            left_content.addWidget(ign_field.generate_checkbox())

        # Ignore AOVs
        self.__ui_ignore_aovs_cb = QCheckBox()
        self.__ui_ignore_aovs_cb.stateChanged.connect(self.__on_state_changed_ignore_aovs)
        nb_enabled_aovs = 0
        for aov in ls(type="aiAOV"):
            if aov.enabled.get(): nb_enabled_aovs += 1
        self.__ignore_aovs = nb_enabled_aovs == 0
        self.__ui_ignore_aovs_cb.setChecked(self.__ignore_aovs)
        right_content.addWidget(self.__ui_ignore_aovs_cb)

        # Output denoising
        self.__ui_output_denoising_aovs_cb = QCheckBox("Output Denoising AOVs")
        self.__ui_output_denoising_aovs_cb.stateChanged.connect(self.__on_state_changed_output_denoising_aovs)
        right_content.addWidget(self.__ui_output_denoising_aovs_cb)

        return content

    def refresh_ui(self):
        self.__refresh_ignore_fields()
        self.__refresh_ignore_aov()
        self.__refresh_output_denoising_aov()

    def __refresh_ignore_fields(self):
        for ign_field in self.__ignore_fields:
            ign_field.refresh_checkbox()

    def __refresh_ignore_aov(self):
        aovs = ls(type="aiAOV")
        enabled_aov = [aov for aov in aovs if aov.enabled.get()]
        nb_aovs = len(aovs)
        nb_enabled_aovs = len(enabled_aov)
        self.__ui_ignore_aovs_cb.setText("Ignore AOVs [" + str(nb_enabled_aovs) + "/" + str(nb_aovs) + "]")

    def __refresh_output_denoising_aov(self):
        checked = ls("defaultArnoldRenderOptions")[0].outputVarianceAOVs.get()
        self.__ui_output_denoising_aovs_cb.setChecked(checked)

    def __on_state_changed_ignore_aovs(self, state):
        self.__ignore_aovs = state == 2
        self.__ignore_aovs_action()
        self.__refresh_ignore_aov()

    def __ignore_aovs_action(self):
        aov_list = ls(type="aiAOV")
        for aov in aov_list:
            aov.enabled.set(not self.__ignore_aovs)

    def __on_state_changed_output_denoising_aovs(self, state):
        ls("defaultArnoldRenderOptions")[0].outputVarianceAOVs.set(state == 2)
        self.__refresh_output_denoising_aov()

    def add_callbacks(self):
        self.__arnold_render_callback = scriptJob(
            attributeChange=['defaultArnoldRenderOptions.outputVarianceAOVs', self.__refresh_output_denoising_aov])
        for ign_field in self.__ignore_fields:
            ign_field.add_callback()

    def remove_callbacks(self):
        scriptJob(kill=self.__arnold_render_callback)

        for ign_field in self.__ignore_fields:
            ign_field.remove_callback()

    def add_to_preset(self, part_name, preset):
        for ign_field in self.__ignore_fields:
            key, value = ign_field.get_preset_value_tuple()
            preset.set(part_name, key, value)
        preset.set(part_name, "ignore_aovs", self.__ignore_aovs)
        preset.set(part_name, "output_denoising", getAttr("defaultArnoldRenderOptions.outputVarianceAOVs"))

    def apply(self, part_name, preset):
        for ign_field in self.__ignore_fields:
            key, field = ign_field.get_key_preset_and_field()
            setAttr("defaultArnoldRenderOptions."+field, preset.get(part_name, key))
        self.__ignore_aovs = preset.get(part_name, "ignore_aovs")
        self.__ignore_aovs_action()
        setAttr("defaultArnoldRenderOptions.outputVarianceAOVs", preset.get(part_name, "output_denoising"))