import os
from Library.json_settings_support import *


class IncludedModuleDevice:
    def __init__(self, name_device, name_module, name_socket):
        self.port_nr = None
        self.address_ip = None
        self.baudrate = None
        self.name_port = None
        self.path_config_file = None
        self.name_module = name_module
        self.name_socket = name_socket
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
        self.path_config_file = f"{_current_directory}/Modules/modules_config.json"
        _load_data_from_file = JsonSettingSupport.load_file(self.path_config_file)
        for _module in _load_data_from_file['Modules']:
            if _module['Name'] == self.name_module:
                for _socket in _module['Sockets']:
                    if _socket['Name'] == self.name_socket:
                        for _device in _socket['Devices']:
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

    def check_connect(self):
        if self.address_ip is not None:
            print("Sprawdzam połaczenie .....")
            # to powinna znajdować się metoda do sprawdzania połaczenia
            _status = True
            print('Polaczenie: ({}, {}), Status: {}'.format(self.address_ip, self.port_nr, _status))
            return _status
        elif self.name_port is not None:
            print("Sprawdzam połaczenie .....")
            # to powinna znajdować się metoda do sprawdzania połaczenia
            _status = True
            print('Polaczenie: ({}, {}), Status: {}'.format(self.name_port, self.baudrate, _status))
            return _status
        else:
            print("Polaczenie: brak konfiguracji")
            return False

    def disconnect(self):
        # sprawdz czy jest otwarte połaczenie
        # rozlacz
        print("Rozlaczono z {}".format(self.name_device))

    def read_connect_param(self):
        if self.address_ip is not None:
            return self.address_ip, self.port_nr, self.name_module, self.name_socket
        elif self.name_port is not None:
            return self.name_port, self.baudrate, self.name_module, self.name_socket
        else:
            return None

