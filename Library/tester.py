from Library.libJson import *
from Library.global_function import *
import subprocess


class DeviceTester:
    def __init__(self, _path_setting):
        self.id = None
        self.devices_included = None
        self.version = None
        self.name = None
        self.settings = None
        self.path_setting = _path_setting
        self.load_settings_from_file()

    def load_settings_from_file(self):
        self.settings = JsonSetting.load_file(self.path_setting)
        self.name = self._get_name()
        self.version = self.settings[self.name]['version']
        self.devices_included = self.settings[self.name]['devices']
        self.id = self._get_id()

    def _get_name(self):
        list_header = []
        for name, dict_ in self.settings.items():
            list_header.append(name)
        return list_header[0]

    @staticmethod
    def _get_id():
        if is_platform_windows():
            current_machine_id = subprocess.check_output('wmic csproduct get uuid').strip()
            return current_machine_id[41:].decode('utf-8').strip()
