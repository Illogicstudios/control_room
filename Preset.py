from utils import *

class Preset:

    @classmethod
    def create_from_existant(cls, preset_dict):
        name = preset_dict["name"]
        del preset_dict["name"]
        if "active" in preset_dict:
            active = preset_dict["active"]
            del preset_dict["active"]
        else:
            active = False
        return cls(name, preset_dict, active)

    def __init__(self, name, fields=None, active=False):
        self.__name = name.replace(" ", "_")
        self.__fields = {} if fields is None or type(fields) is not dict else fields
        self.__active = active

    # ###################################################### dict ######################################################

    def set(self, part_name, key, value):
        if part_name not in self.__fields:
            self.__fields[part_name] = {}
        self.__fields[part_name][key] = value

    def get(self, part_name, key):
        if part_name not in self.__fields or key not in self.__fields[part_name]:
            return None
        return self.__fields[part_name][key]

    def keys(self):
        return self.__fields.keys()

    def values(self):
        return self.__fields.values()

    def items(self):
        return self.__fields.items()

    # ###################################################### dict ######################################################

    def __eq__(self, other):
        return other.__name == self.__name

    def set_active(self, active):
        self.__active = active

    def is_active(self):
        return self.__active

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def to_preset_array(self):
        preset_dict = self.__fields.copy()
        preset_dict["name"] = self.__name
        preset_dict["active"] = self.__active
        return preset_dict

    def __str__(self):
        return "Preset(\"" + self.__name + "\", " + str(self.__active) + ", " + str(self.__fields) + ")"
