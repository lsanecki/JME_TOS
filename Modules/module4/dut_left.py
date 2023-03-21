import random
import time
from Modules.Devices.camera import *
from Modules.Devices.barcode_reader import *
from Modules.Devices.microphone import *

name_module = 'module4'
name_socket = 'dut_left'

camera = Camera('Camera', name_module, name_socket)
barcode_reader = BarcodeReader('BarcodeReader', name_module, name_socket)
microphone = Microphone('Microphone', name_module, name_socket)

min_time = 0
max_time = 1000


def fun1_1(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print(f"Module: {name_module}, Dut: {name_socket}, Fun: fun1_1, input: {param}")
    status = True
    error_info = "0"

    return status, error_info


def check_camera(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print(f"Module: {name_module}, Dut: {name_module}, Fun: check_camera, input: {param}")
    status = camera.check_connect()
    error_info = "0"
    if status is False:
        error_info = "Blad polaczenia"

    return status, error_info, camera.read_connect_param()


def check_barcode_reader(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print(f"Module: {name_module}, Dut: {name_socket}, Fun: check_barcode_reader, input: {param}")
    status = barcode_reader.check_connect()
    error_info = "0"
    if status is False:
        error_info = "Blad polaczenia"

    return status, error_info, barcode_reader.read_connect_param()


def check_microphone(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print(f"Module: {name_module}, Dut: {name_socket}, Fun: check_microphone, input: {param}")
    status = microphone.check_connect()
    error_info = "0"
    if status is False:
        error_info = "Blad polaczenia"

    return status, error_info, microphone.read_connect_param()


def disconnect_camera(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print(f"Module: {name_module}, Dut: {name_module}, Fun: disconnect_camera, input: {param}")
    status = True
    camera.disconnect()
    error_info = "0"

    return status, error_info


def disconnect_barcode_reader(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print(f"Module: {name_module}, Dut: {name_socket}, Fun: disconnect_barcode_reader, input: {param}")
    status = True
    barcode_reader.disconnect()
    error_info = "0"

    return status, error_info


def disconnect_microphone(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print(f"Module: {name_module}, Dut: {name_socket}, Fun: disconnect_microphone, input: {param}")
    status = True
    microphone.disconnect()
    error_info = "0"

    return status, error_info, microphone.read_connect_param()


def read_barcode(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print(f"Module: {name_module}, Dut: {name_socket}, Fun: read_barcode, input: {param}")
    barcode_reader.set_type_code(param[0], param[1])
    serial_number = barcode_reader.read_serial_number()
    status = True
    error_info = "0"
    if serial_number is None:
        status = False
        error_info = "Bledny kod"

    return status, error_info, serial_number
