import ControlRoom as cr
from ControlRoom import *
from ControlRoomPart import *
from pymel.core import *


class IgnoreFields:
    def __init__(self, name, field_name, key_preset):
        self.__name = name
        self.__field_name = field_name
        self.__key_preset = key_preset
        self.__checkbox = None
        self.__callback = None
        self.__layer_callback = None
        self.__override = None
        self.__action_add_override = QAction(text="Add Override")
        self.__action_add_override.triggered.connect(self.__create_override)
        self.__action_remove_override = QAction(text="Remove Override")
        self.__action_remove_override.triggered.connect(self.__remove_override)
        self.__retrieve_override()

    # Create an override for the field of the checkbox
    def __create_override(self):
        obj_attr = self.__field_name.split(".")
        self.__override = cr.ControlRoom.create_override(obj_attr[0], obj_attr[1])

    # Remove the override of the field of the checkbox
    def __remove_override(self):
        cr.ControlRoom.remove_override(self.__override)
        self.__override = None

    # Retrieve the override of the field of the checkbox
    def __retrieve_override(self):
        obj_attr = self.__field_name.split(".")
        self.__override = cr.ControlRoom.retrieve_override(obj_attr[0], obj_attr[1])

    # On checkbox changed
    def __on_state_changed(self, state):
        setAttr(self.__field_name, state == 2)

    # Getter of the key preset and the field
    def get_key_preset_and_field(self):
        return self.__key_preset, self.__field_name

    # Generate the checkbox
    def generate_checkbox(self):
        self.__checkbox = QCheckBox(self.__name)
        self.__checkbox.stateChanged.connect(self.__on_state_changed)
        self.__checkbox.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.__checkbox.addAction(self.__action_add_override)
        self.__checkbox.addAction(self.__action_remove_override)
        return self.__checkbox

    # Refresh the checkbox
    def refresh_checkbox(self):
        visible_layer = render_setup.instance().getVisibleRenderLayer()
        is_default_layer = visible_layer.name() == "defaultRenderLayer"
        self.__checkbox.setChecked(getAttr(self.__field_name))
        self.__action_add_override.setEnabled(not is_default_layer and self.__override is None)
        self.__action_remove_override.setEnabled(not is_default_layer and self.__override is not None)
        stylesheet_lbl = "color:" + cr.OVERRIDE_LABEL_COLOR if self.__override is not None else ""
        self.__checkbox.setStyleSheet("QCheckBox{" + stylesheet_lbl + "}")

    def add_callback(self):
        self.__callback = scriptJob(attributeChange=[self.__field_name, self.refresh_checkbox])
        self.__layer_callback = scriptJob(event=["renderLayerManagerChange", self.refresh_checkbox])

    def remove_callback(self):
        scriptJob(kill=self.__callback)
        scriptJob(kill=self.__layer_callback)


class FeatureOverridesPart(ControlRoomPart):
    def __init__(self, control_room):
        super(FeatureOverridesPart, self).__init__(control_room, "Feature Overrides")
        self.__ignore_fields = [
            IgnoreFields("Ignore Subdivision", "defaultArnoldRenderOptions.ignoreSubdivision", "ignore_subdivision"),
            IgnoreFields("Ignore Athmosphere", "defaultArnoldRenderOptions.ignoreAtmosphere", "ignore_atmosphere"),
            IgnoreFields("Ignore Displacement", "defaultArnoldRenderOptions.ignoreDisplacement", "ignore_displacement"),
            IgnoreFields("Ignore Motion", "defaultArnoldRenderOptions.ignoreMotion", "ignore_motion"),
            IgnoreFields("Ignore Depth of field", "defaultArnoldRenderOptions.ignoreDof", "ignore_dof")
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

    # Refresh all the ignore fields
    def __refresh_ignore_fields(self):
        for ign_field in self.__ignore_fields:
            ign_field.refresh_checkbox()

    # Refresh the ignore aovs field
    def __refresh_ignore_aov(self):
        aovs = ls(type="aiAOV")
        enabled_aov = [aov for aov in aovs if aov.enabled.get()]
        nb_aovs = len(aovs)
        nb_enabled_aovs = len(enabled_aov)
        self.__ui_ignore_aovs_cb.setText("Ignore AOVs [" + str(nb_enabled_aovs) + "/" + str(nb_aovs) + "]")

    # Refresh teh output denoising aov field
    def __refresh_output_denoising_aov(self):
        checked = ls("defaultArnoldRenderOptions")[0].outputVarianceAOVs.get()
        self.__ui_output_denoising_aovs_cb.setChecked(checked)

    # On ignore aov checkbox changed
    def __on_state_changed_ignore_aovs(self, state):
        self.__ignore_aovs = state == 2
        self.__ignore_aovs_action()
        self.__refresh_ignore_aov()

    # Refresh the state of AOVs
    def __ignore_aovs_action(self):
        aov_list = ls(type="aiAOV")
        for aov in aov_list:
            aov.enabled.set(not self.__ignore_aovs)

    # On output denoising aov checkbox changed
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
            key, field = ign_field.get_key_preset_and_field()
            preset.set(part_name, key, getAttr(field))
        preset.set(part_name, "ignore_aovs", self.__ignore_aovs)
        preset.set(part_name, "output_denoising", getAttr("defaultArnoldRenderOptions.outputVarianceAOVs"))

    def apply(self, part_name, preset):
        for ign_field in self.__ignore_fields:
            key, field = ign_field.get_key_preset_and_field()
            setAttr(field, preset.get(part_name, key))
        self.__ignore_aovs = preset.get(part_name, "ignore_aovs")
        self.__ignore_aovs_action()
        setAttr("defaultArnoldRenderOptions.outputVarianceAOVs", preset.get(part_name, "output_denoising"))
