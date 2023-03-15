import subprocess

current_machine_id = subprocess.check_output('wmic csproduct get uuid').strip()
print(current_machine_id)

import platform


def is_platform_windows():
    return platform.system() == "Windows"


print('Windows: {}'.format(is_platform_windows()))


def is_platform_linux():
    return platform.system() == "Linux"


print('Linux: {}'.format(is_platform_linux()))

import sys

print(sys.version)


print(platform.system())

print('bool:1 ',bool(0) )

# windows
'''
import _winreg
registry = _winreg.HKEY_LOCAL_MACHINE
address = 'SOFTWARE\\Microsoft\\Cryptography'
keyargs = _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY
key = _winreg.OpenKey(registry, address, 0, keyargs)
value = _winreg.QueryValueEx(key, 'MachineGuid')
_winreg.CloseKey(key)
unique = value[0]
'''

# linux

'''
import importlib 
winreg_exists = importlib.find_loader('winreg')
if winreg_exists:
    import winreg
...
if winreg_exists:
    # do winreg stuff
'''
