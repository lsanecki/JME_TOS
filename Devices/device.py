import os
from Library.json_settings_support import *


class IncludedDevice:
    def __init__(self, name_device):
        self.port_nr = None
        self.address_ip = None
        self.baudrate = None
        self.name_port = None
        self.path_config_file = None
        self.name_device = name_device
        self.load_settings()

    def configure_connection(self):
        pass

    def config_eth(self, address_ip, port_nr):
        print('Konfiguruje eth')
        self.address_ip = address_ip
        self.port_nr = port_nr
        print(self.address_ip, self.port_nr)

    def config_serial_port(self, port_name, baudrate):
        print('Konfigruje serial port')
        self.name_port = port_name
        self.baudrate = baudrate
        print(self.name_port, self.baudrate)

    def load_settings(self):
        _current_directory = os.getcwd()
        self.path_config_file = f"{_current_directory}/Settings/global_settings.json"
        _load_data_from_file = JsonSettingSupport.load_file(self.path_config_file)
        print(_load_data_from_file['devices'])
        for _device in _load_data_from_file['devices']:
            if _device['Name'] == self.name_device:
                print(_device['InputData'])
                if _device['InputData'][0] == 'SerialPort':
                    self.config_serial_port(_device['InputData'][1], _device['InputData'][2])
                    # konfiguruj port szeregowy
                elif _device['InputData'][0] == 'Ethernet':
                    self.config_eth(_device['InputData'][1], _device['InputData'][2])
                    # konfiguruj połaczenie przez Ethernet
                else:
                    pass
                    # zgłoś wyjatek

