from ControlRoomPart import *
from pymel.core import *


class DepthOfFieldPart(ControlRoomPart):
    def __init__(self, control_room):
        super(DepthOfFieldPart, self).__init__(control_room, "Depth of Field")
        self.__no_refresh = False
        self.__cam = None
        self.__ui_dof_cb = None
        self.__ui_lbl_fstop = None
        self.__ui_line_edit_fstop = None
        self.__camera_dof_callback = None
        self.__camera_fstop_callback = None

    def populate(self):
        content = QHBoxLayout()
        content.setContentsMargins(4, 4, 1, 4)

        self.__ui_dof_cb = QCheckBox("Depth of field")
        self.__ui_dof_cb.stateChanged.connect(self.__on_dof_changed)
        content.addWidget(self.__ui_dof_cb, 1, Qt.AlignLeft)

        form_layout = QFormLayout()
        content.addLayout(form_layout, 2)

        self.__ui_lbl_fstop = QLabel("FStop")
        self.__ui_line_edit_fstop = QLineEdit()
        validator = QDoubleValidator(bottom=1, top=64, decimals=3)
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        validator.setLocale(locale)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.__ui_line_edit_fstop.setValidator(validator)
        self.__ui_line_edit_fstop.editingFinished.connect(self.__on_fstop_changed)
        form_layout.addRow(self.__ui_lbl_fstop, self.__ui_line_edit_fstop)
        return content

    def refresh_ui(self):
        if self.__cam is not None and not self.__no_refresh:
            enabled = self.__cam.depthOfField.get()
            self.__ui_dof_cb.setChecked(enabled)
            self.__ui_lbl_fstop.setEnabled(enabled)
            self.__ui_line_edit_fstop.setEnabled(enabled)
            self.__ui_line_edit_fstop.setText(str(round(self.__cam.fStop.get(), 3)))

    # On checkbox Depth of Field changed
    def __on_dof_changed(self, state):
        if self.__cam is not None:
            self.__no_refresh = True
            self.__cam.depthOfField.set(state == 2)
            self.__no_refresh = False

    # On FStop line edit changed
    def __on_fstop_changed(self):
        if self.__cam is not None:
            self.__no_refresh = True
            self.__cam.fStop.set(float(self.__ui_line_edit_fstop.text()))
            self.__no_refresh = False

    # On camera changed refresh the callbacks and the UI
    def cam_changed(self, cam):
        self.__cam = cam
        self.remove_callbacks()
        self.add_dynamic_callbacks()
        self.refresh_ui()

    def add_callbacks(self):
        # Nothing
        pass

    # Add callbacks to the current camera
    def add_dynamic_callbacks(self):
        if self.__cam is not None:
            self.__camera_dof_callback = scriptJob(
                attributeChange=[self.__cam + '.depthOfField', self.refresh_ui])
            self.__camera_fstop_callback = scriptJob(
                attributeChange=[self.__cam + '.fStop', self.refresh_ui])

    # Remove the callbacks from the current camera
    def remove_callbacks(self):
        if self.__camera_dof_callback is not None:
            scriptJob(kill=self.__camera_dof_callback)
            self.__camera_dof_callback = None
        if self.__camera_fstop_callback is not None:
            scriptJob(kill=self.__camera_fstop_callback)
            self.__camera_fstop_callback = None

    def add_to_preset(self, part_name, preset):
        if self.__cam is not None:
            preset.set(part_name, "depthOfField", self.__cam.depthOfField.get())
            preset.set(part_name, "fStop", self.__cam.fStop.get())

    def apply(self, part_name, preset):
        if self.__cam is not None:
            self.__cam.depthOfField.set(preset.get(part_name, "depthOfField"))
            self.__cam.fStop.set(preset.get(part_name, "fStop"))
