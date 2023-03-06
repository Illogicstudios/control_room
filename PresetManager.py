import json
import base64
from pymel.core import *
from utils import *
from Preset import *


class PresetManager:
    # ################################################### singleton ####################################################
    __instance = None

    @staticmethod
    def get_instance():
        if PresetManager.__instance is None:
            PresetManager.__instance = PresetManager()
            PresetManager.__instance.retrieve_presets()
        return PresetManager.__instance

    # ################################################### singleton ####################################################

    def __init__(self):
        self.__presets = []
        self.__active_preset = None

    def clear(self):
        self.__presets.clear()
        self.__active_preset = None

    def add_preset(self, preset_to_add):
        to_remove = None
        for preset in self.__presets:
            if preset.get_name() == preset_to_add.get_name():
                to_remove = preset
                break
        if to_remove is not None:
            self.remove_preset(to_remove)
        if preset_to_add.is_active():
            for curr_preset in self.__presets:
                curr_preset.set_active(False)

        if preset_to_add not in self.__presets:
            self.__presets.append(preset_to_add)

    def remove_preset(self, preset_to_remove):
        if preset_to_remove is not None:
            self.__presets.remove(preset_to_remove)

    def set_preset_active(self, active_preset):
        # Set all presets to inactive except the wanted one
        if active_preset is not None:
            for preset in self.__presets:
                preset.set_active(preset is active_preset)

    def retrieve_presets(self):
        self.clear()

        if "presets" in fileInfo:
            found_active = False
            json_presets = fileInfo["presets"].replace("\\\"", "\"")
            arr_json_presets = json.loads(json_presets)
            for json_preset in arr_json_presets:
                preset = Preset.create_from_existant(json_preset)
                if preset.is_active() and not found_active:
                    self.__active_preset = preset
                self.__presets.append(preset)

    def save_presets(self):
        arr_json_presets = []
        for preset in self.__presets:
            arr_json_presets.append(preset.to_preset_array())
        fileInfo["presets"] = json.dumps(arr_json_presets)

    def __str__(self):
        string = "PresetManager("
        if len(self.__presets) > 0: string += "\n"
        for preset in self.__presets:
            string += "\t" + str(preset) + "\n"
        string += ")"
        return string

    def get_presets(self):
        self.__presets.sort(key=lambda x: x.get_name())
        return self.__presets

    def has_preset_with_name(self, name):
        for preset in self.__presets:
            if preset.get_name() == name:
                return True
