from Modules.Devices.device import *
import random


class BarcodeReader(IncludedModuleDevice):
    def __init__(self, name_device, name_module, name_socket):
        super().__init__(name_device, name_module, name_socket)
        self.len_code = None
        self.type = None

    def read_serial_number(self):
        sn = random.randint(100000000, 999999999)
        if len(str(sn)) == self.len_code:
            return {'Serial': str(sn)}
        return None

    def set_type_code(self, type, len_code):
        self.type = type
        self.len_code = len_code
