from Library.json_settings_support import *
from Library.global_procedures import *


class ProjectTestSupport:
    def __init__(self, path_project):
        """
        Konstruktor klasy
        :param path_project: Lokalizacja projektu
        :type path_project: str
        """

        self.test_finalization = None
        self.test = None
        self.test_initialization = None
        self.finalization_enabled = None
        self.initialization_enabled = None
        self.test_modules = None
        self.software_collection = None
        self.labels_collection = None
        self.version_project = None
        self.index_project = None
        self.name_project = None
        self.settings = None
        self.name_device = None
        self.settings_loaded_from_file = None
        self.path_project = path_project + "Project_settings/ProjectSettings.json"
        self.load_project_settings()

    def load_project_settings(self):
        """
        Wczytaj ustawienia projektu
        :return:
        """

        self.settings_loaded_from_file = JsonSettingSupport.load_file(self.path_project)
        self.settings = self.settings_loaded_from_file['Project']['Settings']
        self.name_project = self.settings['Name']
        self.index_project = self.settings['Index']
        self.version_project = self.settings['Version']
        self.labels_collection = self.settings['Labels']
        self.software_collection = self.settings['Soft']
        self.initialization_enabled = bool(self.settings['EnableInitStep'])
        self.finalization_enabled = bool(self.settings['EnableFinalStep'])
        self.test_initialization = self.settings_loaded_from_file['Project']['InitStep']
        self.test = self.settings_loaded_from_file['Project']['TestStep']
        self.test_finalization = self.settings_loaded_from_file['Project']['FinalStep']

    def load_test_modules(self, name_device, version_device):
        """
        Wczytaj moduły testowe urządzenia
        :param name_device: Nazwa urządzania (testera/programatora)
        :type name_device: str
        :param version_device: Wersja urządzenia
        :type version_device: str
        :return:
        """

        self.name_device = name_device
        self.test_modules = self.download_parameters_of_testing_modules(name_device, version_device)
        self.add_test_module_procedures()

    def download_parameters_of_testing_modules(self, name_device, version_device):
        """
        Pobiera parametry modułów testujacych
        :param name_device: Nazwa urządzania (testera/programatora)
        :type name_device: str
        :param version_device: Wersja urządzenia
        :type version_device: str
        :return: Zwraca parametry modułów testowych danego urządzenia
        :rtype: dict
        """

        _devices = self.settings['Devices']
        for _device in _devices:
            if name_device == _device['Name'] and version_device == _device['Version']:
                return _device['Modules']

    def add_test_module_procedures(self):
        """
        Dodaje procedury modułów testujących
        :return:
        """

        for _test_module in self.test_modules:
            for _test_socket in _test_module['Sockets']:
                _imported_library_test_socket = dynamic_import(
                    'Modules.{}.{}'.format(_test_module['Name'], _test_socket['Name']))
                _library_test_socket = {"libFun": _imported_library_test_socket}
                _test_socket.update(_library_test_socket)
