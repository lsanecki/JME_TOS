from Library.libJson import *
from Library.global_function import *


class ProjectTestOS:
    def __init__(self, _path_project):
        self.final_test = None
        self.test = None
        self.init_test = None
        self.final_enable = None
        self.init_enable = None
        self.modules = None
        self.soft = None
        self.labels = None
        self.version_project = None
        self.index_project = None
        self.name_project = None
        self.settings = None
        self.name_device = None
        self.load_file_set = None
        self.path_project = _path_project + "Project_settings/ProjectSettings.json"
        self.load_project_settings()

    def load_project_settings(self):
        self.load_file_set = JsonSetting.load_file(self.path_project)
        self.settings = self.load_file_set['Project']['Settings']
        self.name_project = self.settings['Name']
        self.index_project = self.settings['Index']
        self.version_project = self.settings['Version']
        self.labels = self.settings['Labels']
        self.soft = self.settings['Soft']
        self.init_enable = bool(self.settings['EnableInitStep'])
        self.final_enable = bool(self.settings['EnableFinalStep'])
        self.init_test = self.load_file_set['Project']['InitStep']
        self.test = self.load_file_set['Project']['TestStep']
        self.final_test = self.load_file_set['Project']['FinalStep']

    def load_modules(self, _name_device, _version):
        self.name_device = _name_device
        self.modules = self.check_device(_name_device, _version)
        self.add_modules_fun()

    def check_device(self, _name_device, _version):
        devices = self.settings['Devices']
        for device in devices:
            if _name_device == device['Name'] and _version == device['Version']:
                return device['Modules']

    def add_modules_fun(self):
        for module in self.modules:
            for socket in module['Sockets']:
                lib = dynamic_import('Modules.{}.{}'.format(module['Name'], socket['Name']))
                dut_lib_fun = {"libFun": lib}
                socket.update(dut_lib_fun)
