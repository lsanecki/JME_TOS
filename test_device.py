from Devices.device import *
from Modules.Devices.camera import *


def main():
    # sample_device = IncludedDevice('Sniffer')
    # sample_device2 = IncludedDevice('SignalMatrix')

    camera = Camera('Camera', 'module1', 'dut_left')
    print(camera.check_connect())


if __name__ == '__main__':
    main()
