from Modules.Devices.device import *


class Camera(IncludedModuleDevice):
    def __init__(self, name_device, name_module, name_socket):
        super().__init__(name_device, name_module, name_socket)