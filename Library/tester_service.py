from Library.json_settings_support import *
from Library.global_procedures import *
import subprocess


class DeviceTesterService:
    def __init__(self, path_setting):
        """
        Konstruktor klasy
        :param path_setting: lokalizacja pliku z ustawieniami urządzenia testujacego (tester/programatora)
        :type path_setting: str 
        """

        self.id = None
        self.devices_included = None
        self.version = None
        self.name = None
        self.settings = None
        self.path_setting = path_setting
        self.load_settings_from_file()

    def load_settings_from_file(self):
        """
        Wczytaj ustawienia urządzenia testujacego (tester/programator)
        :return:
        """

        self.settings = JsonSettingSupport.load_file(self.path_setting)
        self.name = self._get_name()
        self.version = self.settings[self.name]['version']
        self.devices_included = self.settings[self.name]['devices']
        self.id = self._get_id()

    def _get_name(self):
        """
        Pobierz nazwe testera z ustawień
        :return: Nazwa testera
        :rtype: str
        """

        _list_header = []
        for _name, dict_ in self.settings.items():
            _list_header.append(_name)
        return _list_header[0]

    @staticmethod
    def _get_id():
        """
        Pobierz nr id urzadzania na którym jest uruchomiona aplikacja
        :return: Nr id urządzenia
        :rtype: str
        """

        if is_platform_windows():
            _current_machine_id = subprocess.check_output('wmic csproduct get uuid').strip()
            return _current_machine_id[41:].decode('utf-8').strip()
